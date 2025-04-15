import re
import numpy as np
import pandas as pd

def clean_price(price_text: str) -> float | None:
    cleaned_text = re.sub(r'[^\d.,]', '', price_text).replace(',', '.')
    try:
        return float(cleaned_text)
    except ValueError:
        return None

def calculate_average_prices(df: pd.DataFrame) -> list[dict]:
    result = []
    grouped_data = df.groupby('title')

    for site_title, group in grouped_data:
        prices = [
            clean_price(str(price))
            for price in group['xpath']
            if clean_price(str(price)) is not None
        ]

        average_price = np.mean(prices) if prices else None

        result.append({
            'title': site_title,
            'url': group['url'].iloc[0],
            'average_price': average_price
        })

    return result