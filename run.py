"""Price European options and report analytic sensitivities."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def price(spot: float, strike: float, rate: float, volatility: float, years: float) -> tuple[float, float]:
    root_time = math.sqrt(years)
    d1 = (math.log(spot / strike) + (rate + volatility**2 / 2) * years) / (volatility * root_time)
    d2 = d1 - volatility * root_time
    call = spot * cdf(d1) - strike * math.exp(-rate * years) * cdf(d2)
    put = strike * math.exp(-rate * years) * cdf(-d2) - spot * cdf(-d1)
    return call, put


def main() -> None:
    spot, strike, rate, volatility, years = 100.0, 100.0, 0.03, 0.22, 0.75
    call, put = price(spot, strike, rate, volatility, years)
    d1 = (math.log(spot / strike) + (rate + volatility**2 / 2) * years) / (volatility * math.sqrt(years))
    call_delta = cdf(d1)
    vega = spot * math.sqrt(years) * math.exp(-d1**2 / 2) / math.sqrt(2 * math.pi) / 100
    parity_residual = call - put - (spot - strike * math.exp(-rate * years))
    spots = list(range(70, 131, 5))
    values = [price(value, strike, rate, volatility, years) for value in spots]
    metrics = {
        "spot": spot,
        "strike": strike,
        "risk_free_rate_pct": rate * 100,
        "implied_volatility_pct": volatility * 100,
        "time_to_expiry_years": years,
        "european_call_price": round(call, 6),
        "european_put_price": round(put, 6),
        "call_delta": round(call_delta, 6),
        "put_delta": round(call_delta - 1, 6),
        "vega_per_vol_point": round(vega, 6),
        "put_call_parity_residual": round(parity_residual, 10),
        "pricing_method": "Black-Scholes-Merton closed form",
    }
    payload = {
        "project": "Options Pricing Library",
        "data_notice": "Analytic European-option example on synthetic inputs under Black-Scholes assumptions; not a valuation recommendation.",
        "metrics": metrics,
        "chart": {
            "title": "Option value across underlying spot levels",
            "x_label": "Underlying spot",
            "y_label": "Option value",
            "series": [
                {"name": "Call", "values": [round(pair[0], 4) for pair in values]},
                {"name": "Put", "values": [round(pair[1], 4) for pair in values]},
            ],
        },
        "flow": ["Contract terms", "Market inputs", "Closed-form pricer", "Greeks & checks", "Valuation result"],
        "flow_values": [0.1, 0.2, 0.4, 0.1, 0.1],
    }
    output = ROOT / "reports" / "metrics.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
