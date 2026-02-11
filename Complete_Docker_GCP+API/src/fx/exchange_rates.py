import requests
import pandas as pd


def fetch_exchange_rates(api_url: str) -> pd.DataFrame:
    """
    Fetch exchange rates from an API and return as a DataFrame with:
      - Currency
      - Exchange Rate

    Expected JSON shape:
      { "conversion_rates": { "USD": 1.07, ... } }
    """
    resp = requests.get(api_url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    conversion_rates = data.get("conversion_rates")
    if not isinstance(conversion_rates, dict):
        raise ValueError("API response missing 'conversion_rates' dict")

    df = pd.DataFrame(list(conversion_rates.items()), columns=["Currency", "Exchange Rate"])
    return df
