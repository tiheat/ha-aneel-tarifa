"""Data update coordinator for the ANEEL tariff integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .aneel import Bandeira, Tarifa, bandeira_vigente, tarifa_vigente
from .api import AneelApi, AneelApiError
from .const import CONF_DISTRIBUIDORA, CONF_SUBCLASSE, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AneelData:
    """Current flag and tariff."""

    bandeira: Bandeira | None
    tarifa: Tarifa | None


type AneelConfigEntry = ConfigEntry[AneelCoordinator]


class AneelCoordinator(DataUpdateCoordinator[AneelData]):
    """Fetch flag and tariff from ANEEL periodically."""

    config_entry: AneelConfigEntry

    def __init__(self, hass: HomeAssistant, entry: AneelConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = AneelApi(async_get_clientsession(hass))

    async def _async_update_data(self) -> AneelData:
        today = dt_util.now().date()
        try:
            bandeiras = await self.api.bandeiras_recentes()
            tarifas = await self.api.tarifas(
                self.config_entry.data[CONF_DISTRIBUIDORA],
                self.config_entry.data[CONF_SUBCLASSE],
            )
        except AneelApiError as err:
            raise UpdateFailed(f"Erro ao consultar a ANEEL: {err}") from err
        tarifa = tarifa_vigente(tarifas, today)
        if tarifa is None:
            raise UpdateFailed("Nenhuma tarifa vigente encontrada para a distribuidora")
        return AneelData(bandeira=bandeira_vigente(bandeiras, today), tarifa=tarifa)
