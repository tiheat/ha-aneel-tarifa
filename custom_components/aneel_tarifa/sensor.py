"""Sensors for the ANEEL tariff integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .aneel import preco_final
from .const import CONF_COFINS, CONF_DISTRIBUIDORA, CONF_ICMS, CONF_PIS, CONF_SUBCLASSE, DOMAIN
from .coordinator import AneelConfigEntry, AneelCoordinator, AneelData

PRICE_UNIT = "BRL/kWh"


@dataclass(frozen=True, kw_only=True)
class AneelSensorDescription(SensorEntityDescription):
    """Describe an ANEEL sensor."""

    value_fn: Callable[[AneelData, dict[str, Any]], Any]
    attrs_fn: Callable[[AneelData, dict[str, Any]], dict[str, Any]] = lambda d, o: {}


def _impostos(options: dict[str, Any]) -> float:
    return float(options.get(CONF_ICMS, 0)) + float(options.get(CONF_PIS, 0)) + float(options.get(CONF_COFINS, 0))


def _adicional(data: AneelData) -> float:
    return data.bandeira.adicional_rs_kwh if data.bandeira else 0.0


SENSORS: tuple[AneelSensorDescription, ...] = (
    AneelSensorDescription(
        key="preco_final",
        translation_key="preco_final",
        icon="mdi:cash-multiple",
        native_unit_of_measurement=PRICE_UNIT,
        suggested_display_precision=5,
        value_fn=lambda d, o: preco_final(d.tarifa.total_rs_kwh, _adicional(d), _impostos(o)),
        attrs_fn=lambda d, o: {
            "icms_pct": o.get(CONF_ICMS),
            "pis_pct": o.get(CONF_PIS),
            "cofins_pct": o.get(CONF_COFINS),
            "impostos_pct": round(_impostos(o), 2),
        },
    ),
    AneelSensorDescription(
        key="tarifa_sem_impostos",
        translation_key="tarifa_sem_impostos",
        icon="mdi:cash",
        native_unit_of_measurement=PRICE_UNIT,
        suggested_display_precision=5,
        value_fn=lambda d, o: d.tarifa.total_rs_kwh,
        attrs_fn=lambda d, o: {
            "tusd_rs_kwh": d.tarifa.tusd_rs_kwh,
            "te_rs_kwh": d.tarifa.te_rs_kwh,
            "resolucao": d.tarifa.resolucao,
            "vigencia_inicio": d.tarifa.inicio,
            "vigencia_fim": d.tarifa.fim,
        },
    ),
    AneelSensorDescription(
        key="bandeira",
        translation_key="bandeira",
        icon="mdi:flag-variant",
        value_fn=lambda d, o: d.bandeira.nome if d.bandeira else None,
        attrs_fn=lambda d, o: {"competencia": d.bandeira.competencia} if d.bandeira else {},
    ),
    AneelSensorDescription(
        key="adicional_bandeira",
        translation_key="adicional_bandeira",
        icon="mdi:flag-plus",
        native_unit_of_measurement=PRICE_UNIT,
        suggested_display_precision=5,
        value_fn=lambda d, o: _adicional(d),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: AneelConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data
    async_add_entities(AneelSensor(coordinator, description) for description in SENSORS)


class AneelSensor(CoordinatorEntity[AneelCoordinator], SensorEntity):
    """ANEEL tariff sensor."""

    _attr_has_entity_name = True
    entity_description: AneelSensorDescription

    def __init__(self, coordinator: AneelCoordinator, description: AneelSensorDescription) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Tarifa {entry.data[CONF_DISTRIBUIDORA]}",
            manufacturer="ANEEL (dados abertos)",
            model=f"B1 {entry.data[CONF_SUBCLASSE]} convencional",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://dadosabertos.aneel.gov.br/",
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data, self.coordinator.config_entry.options)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return self.entity_description.attrs_fn(self.coordinator.data, self.coordinator.config_entry.options)
