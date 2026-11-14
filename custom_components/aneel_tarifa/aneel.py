"""Pure helpers to interpret ANEEL open data records (no Home Assistant imports)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class Bandeira:
    """Tariff flag in force for a month."""

    nome: str
    adicional_rs_kwh: float
    competencia: str


@dataclass(frozen=True)
class Tarifa:
    """Homologated tariff (without taxes) in force on a date."""

    tusd_rs_kwh: float
    te_rs_kwh: float
    resolucao: str
    inicio: str
    fim: str

    @property
    def total_rs_kwh(self) -> float:
        """TUSD + TE in R$/kWh."""
        return round(self.tusd_rs_kwh + self.te_rs_kwh, 5)


def parse_brl(value: Any) -> float:
    """Parse ANEEL numeric strings such as '620,08', ',00' or '1.234,56'."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return 0.0
    return float(text.replace(".", "").replace(",", "."))


def bandeira_vigente(records: list[dict[str, Any]], today: date) -> Bandeira | None:
    """Return the flag for the current month, or the latest one not in the future."""
    month = today.strftime("%Y-%m")
    current = [r for r in records if str(r.get("DatCompetencia", "")).startswith(month)]
    if not current:
        current = sorted(
            (r for r in records if str(r.get("DatCompetencia", "")) <= today.isoformat()),
            key=lambda r: r["DatCompetencia"],
            reverse=True,
        )
    if not current:
        return None
    rec = current[0]
    return Bandeira(
        nome=str(rec.get("NomBandeiraAcionada", "")).strip(),
        adicional_rs_kwh=round(parse_brl(rec.get("VlrAdicionalBandeira")) / 1000, 5),
        competencia=str(rec.get("DatCompetencia", ""))[:10],
    )


def tarifa_vigente(records: list[dict[str, Any]], today: date) -> Tarifa | None:
    """Return the tariff whose validity window contains today (values come in R$/MWh)."""
    iso = today.isoformat()
    valid = [
        r for r in records if str(r.get("DatInicioVigencia", "")) <= iso <= str(r.get("DatFimVigencia", "9999-12-31"))
    ]
    if not valid:
        return None
    rec = sorted(valid, key=lambda r: r["DatInicioVigencia"], reverse=True)[0]
    return Tarifa(
        tusd_rs_kwh=round(parse_brl(rec.get("VlrTUSD")) / 1000, 5),
        te_rs_kwh=round(parse_brl(rec.get("VlrTE")) / 1000, 5),
        resolucao=str(rec.get("DscREH", "")).strip(),
        inicio=str(rec.get("DatInicioVigencia", ""))[:10],
        fim=str(rec.get("DatFimVigencia", ""))[:10],
    )


def preco_final(tarifa_rs_kwh: float, adicional_rs_kwh: float, impostos_pct: float) -> float:
    """Final price with taxes calculated 'por dentro': base / (1 - taxes)."""
    if not 0 <= impostos_pct < 100:
        raise ValueError("impostos_pct must be in [0, 100)")
    return round((tarifa_rs_kwh + adicional_rs_kwh) / (1 - impostos_pct / 100), 5)
