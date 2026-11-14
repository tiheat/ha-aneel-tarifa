"""Constants for the ANEEL tariff integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "aneel_tarifa"

API_URL = "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search"
RESOURCE_BANDEIRA = "0591b8f6-fe54-437b-b72b-1aa2efd46e42"
RESOURCE_TARIFAS = "fcf2906c-7c32-4b9b-a637-054e7a5234f4"

CONF_DISTRIBUIDORA = "distribuidora"
CONF_SUBCLASSE = "subclasse"
CONF_ICMS = "icms"
CONF_PIS = "pis"
CONF_COFINS = "cofins"

DEFAULT_SUBCLASSE = "Residencial"
DEFAULT_ICMS = 20.5
DEFAULT_PIS = 1.19
DEFAULT_COFINS = 5.48

SUBCLASSES = [
    "Residencial",
    "Baixa Renda",
    "Residencial Tarifa Social – faixa 01",
    "Residencial Tarifa Social – faixa 02",
    "Residencial Desconto Social – faixa 01",
    "Residencial Desconto Social – faixa 02",
]

TARIFA_FILTERS = {
    "DscSubGrupo": "B1",
    "DscModalidadeTarifaria": "Convencional",
    "DscClasse": "Residencial",
    "DscDetalhe": "Não se aplica",
    "DscBaseTarifaria": "Tarifa de Aplicação",
}

UPDATE_INTERVAL = timedelta(hours=6)
