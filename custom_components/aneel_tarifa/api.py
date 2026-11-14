"""Async client for the ANEEL CKAN datastore API."""

from __future__ import annotations

import json
from typing import Any

import aiohttp

from .const import API_URL, RESOURCE_BANDEIRA, RESOURCE_TARIFAS, TARIFA_FILTERS


class AneelApiError(Exception):
    """Raised when the ANEEL API cannot be reached or returns an error."""


class AneelApi:
    """Minimal client for the datasets used by this integration."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _search(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            async with self._session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                payload = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise AneelApiError(str(err)) from err
        if not payload.get("success"):
            raise AneelApiError(str(payload.get("error")))
        return payload["result"]["records"]

    async def bandeiras_recentes(self, limit: int = 3) -> list[dict[str, Any]]:
        """Latest monthly tariff flags (most recent first)."""
        return await self._search({"resource_id": RESOURCE_BANDEIRA, "limit": limit, "sort": "DatCompetencia desc"})

    async def tarifas(self, distribuidora: str, subclasse: str, limit: int = 10) -> list[dict[str, Any]]:
        """Latest B1 conventional tariffs for a distributor and residential subclass."""
        filters = {**TARIFA_FILTERS, "SigAgente": distribuidora, "DscSubClasse": subclasse}
        return await self._search(
            {
                "resource_id": RESOURCE_TARIFAS,
                "limit": limit,
                "sort": "DatInicioVigencia desc",
                "filters": json.dumps(filters, ensure_ascii=False),
            }
        )

    async def distribuidoras(self) -> list[str]:
        """Distributors that have B1 residential tariffs in the dataset."""
        filters = {**TARIFA_FILTERS, "DscSubClasse": "Residencial"}
        records = await self._search(
            {
                "resource_id": RESOURCE_TARIFAS,
                "fields": "SigAgente",
                "distinct": "true",
                "limit": 1000,
                "filters": json.dumps(filters, ensure_ascii=False),
            }
        )
        return sorted({r["SigAgente"] for r in records if r.get("SigAgente")}, key=str.casefold)
