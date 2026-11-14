"""Config and options flow for the ANEEL tariff integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from homeassistant.util import dt as dt_util

from .aneel import tarifa_vigente
from .api import AneelApi, AneelApiError
from .const import (
    CONF_COFINS,
    CONF_DISTRIBUIDORA,
    CONF_ICMS,
    CONF_PIS,
    CONF_SUBCLASSE,
    DEFAULT_COFINS,
    DEFAULT_ICMS,
    DEFAULT_PIS,
    DEFAULT_SUBCLASSE,
    DOMAIN,
    SUBCLASSES,
)

PERCENT = NumberSelector(
    NumberSelectorConfig(min=0, max=40, step=0.01, mode=NumberSelectorMode.BOX, unit_of_measurement="%")
)


def _taxes_schema(defaults: dict[str, Any]) -> dict:
    return {
        vol.Required(CONF_ICMS, default=defaults.get(CONF_ICMS, DEFAULT_ICMS)): PERCENT,
        vol.Required(CONF_PIS, default=defaults.get(CONF_PIS, DEFAULT_PIS)): PERCENT,
        vol.Required(CONF_COFINS, default=defaults.get(CONF_COFINS, DEFAULT_COFINS)): PERCENT,
    }


def _validate_taxes(user_input: dict[str, Any]) -> dict[str, str]:
    total = user_input[CONF_ICMS] + user_input[CONF_PIS] + user_input[CONF_COFINS]
    return {"base": "invalid_taxes"} if total >= 100 else {}


class AneelTarifaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Choose distributor, subclass and taxes."""

    VERSION = 1

    def __init__(self) -> None:
        self._distribuidoras: list[str] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        api = AneelApi(async_get_clientsession(self.hass))
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_taxes(user_input)
            distribuidora = user_input[CONF_DISTRIBUIDORA]
            subclasse = user_input[CONF_SUBCLASSE]
            await self.async_set_unique_id(f"{distribuidora}_{subclasse}".lower())
            self._abort_if_unique_id_configured()
            if not errors:
                try:
                    records = await api.tarifas(distribuidora, subclasse)
                except AneelApiError:
                    errors["base"] = "cannot_connect"
                else:
                    if tarifa_vigente(records, dt_util.now().date()) is None:
                        errors["base"] = "no_tariff"
            if not errors:
                return self.async_create_entry(
                    title=f"Tarifa ANEEL {distribuidora}",
                    data={CONF_DISTRIBUIDORA: distribuidora, CONF_SUBCLASSE: subclasse},
                    options={k: user_input[k] for k in (CONF_ICMS, CONF_PIS, CONF_COFINS)},
                )

        if not self._distribuidoras:
            try:
                self._distribuidoras = await api.distribuidoras()
            except AneelApiError:
                return self.async_abort(reason="cannot_connect")

        defaults = user_input or {}
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DISTRIBUIDORA, default=defaults.get(CONF_DISTRIBUIDORA, vol.UNDEFINED)
                ): SelectSelector(SelectSelectorConfig(options=self._distribuidoras, mode=SelectSelectorMode.DROPDOWN)),
                vol.Required(CONF_SUBCLASSE, default=defaults.get(CONF_SUBCLASSE, DEFAULT_SUBCLASSE)): SelectSelector(
                    SelectSelectorConfig(options=SUBCLASSES, mode=SelectSelectorMode.DROPDOWN)
                ),
                **_taxes_schema(defaults),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> AneelTarifaOptionsFlow:
        """Return the options flow."""
        return AneelTarifaOptionsFlow()


class AneelTarifaOptionsFlow(OptionsFlowWithReload):
    """Update taxes (they change monthly on the bill)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage taxes."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_taxes(user_input)
            if not errors:
                return self.async_create_entry(data=user_input)
        defaults = user_input or dict(self.config_entry.options)
        return self.async_show_form(step_id="init", data_schema=vol.Schema(_taxes_schema(defaults)), errors=errors)
