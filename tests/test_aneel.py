from datetime import date

import pytest
from aneel import bandeira_chave, bandeira_vigente, parse_brl, preco_final, tarifa_vigente

BANDEIRAS = [
    {"DatCompetencia": "2026-12-01", "NomBandeiraAcionada": "Amarela", "VlrAdicionalBandeira": "18,85"},
    {"DatCompetencia": "2026-11-01", "NomBandeiraAcionada": "Verde", "VlrAdicionalBandeira": ",00"},
    {"DatCompetencia": "2026-10-01", "NomBandeiraAcionada": "Vermelha P1", "VlrAdicionalBandeira": "44,63"},
]

TARIFAS = [
    {
        "DatInicioVigencia": "2026-04-22",
        "DatFimVigencia": "2027-04-21",
        "VlrTUSD": "620,08",
        "VlrTE": "257,65",
        "DscREH": "REH 3.578/2026",
    },
    {
        "DatInicioVigencia": "2026-01-01",
        "DatFimVigencia": "2026-04-21",
        "VlrTUSD": "560,48",
        "VlrTE": "277,24",
        "DscREH": "REH 3.443/2025",
    },
]


@pytest.mark.parametrize(
    ("raw", "expected"), [("620,08", 620.08), (",00", 0.0), ("1.234,56", 1234.56), (None, 0.0), ("", 0.0), (12, 12.0)]
)
def test_parse_brl(raw, expected):
    assert parse_brl(raw) == expected


def test_bandeira_uses_current_month_even_if_next_month_is_published():
    b = bandeira_vigente(BANDEIRAS, date(2026, 11, 14))
    assert (b.nome, b.adicional_rs_kwh, b.competencia) == ("Verde", 0.0, "2026-11-01")


def test_bandeira_falls_back_to_latest_past_month():
    b = bandeira_vigente(BANDEIRAS[1:], date(2027, 1, 5))
    assert b.nome == "Verde"


def test_bandeira_converts_mwh_to_kwh():
    assert bandeira_vigente(BANDEIRAS, date(2026, 12, 3)).adicional_rs_kwh == 0.01885


@pytest.mark.parametrize(
    ("nome", "chave"),
    [
        ("Verde", "verde"),
        ("Amarela", "amarela"),
        ("Vermelha P1", "vermelha_p1"),
        ("Vermelha  P2 ", "vermelha_p2"),
        ("Escassez Hídrica", "escassez_hidrica"),
        ("Roxa", None),
    ],
)
def test_bandeira_chave(nome, chave):
    assert bandeira_chave(nome) == chave


def test_bandeira_vigente_exposes_key():
    assert bandeira_vigente(BANDEIRAS, date(2026, 10, 9)).chave == "vermelha_p1"


def test_bandeira_empty():
    assert bandeira_vigente([], date(2026, 11, 14)) is None


def test_tarifa_vigente_picks_window():
    t = tarifa_vigente(TARIFAS, date(2026, 11, 14))
    assert (t.tusd_rs_kwh, t.te_rs_kwh, t.total_rs_kwh, t.resolucao) == (0.62008, 0.25765, 0.87773, "REH 3.578/2026")
    assert tarifa_vigente(TARIFAS, date(2026, 3, 1)).total_rs_kwh == 0.83772


def test_tarifa_vigente_none_outside_windows():
    assert tarifa_vigente(TARIFAS, date(2028, 1, 1)) is None


def test_preco_final_por_dentro():
    assert preco_final(0.87773, 0.0, 27.17) == 1.20518
    assert preco_final(0.87773, 0.01885, 27.17) == 1.23106


def test_preco_final_rejects_invalid_taxes():
    with pytest.raises(ValueError):
        preco_final(1, 0, 100)
