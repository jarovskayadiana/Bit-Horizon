import requests
import numpy as np
import datetime
from typing import Tuple

class CryptoHorizonPredictor:
    COINGECKO_API = "https://api.coingecko.com/api/v3"

    def __init__(self, symbol: str):
        self.symbol = symbol.lower()

    def get_market_data(self, days: int = 1, interval: str = "hourly") -> Tuple[list, list]:
        """
        Получает исторические данные цены монеты за указанный период.
        """
        url = f"{self.COINGECKO_API}/coins/{self.symbol}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": interval}
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        prices = data["prices"]  # [ [timestamp, price], ... ]
        timestamps = [datetime.datetime.fromtimestamp(p[0] / 1000) for p in prices]
        values = [p[1] for p in prices]
        return timestamps, values

    def predict_time_to_target(self, target_price: float) -> str:
        """
        Прогнозирует время достижения целевой цены.
        """
        times, prices = self.get_market_data(days=1)
        x = np.arange(len(prices))
        y = np.array(prices)

        if (y[-1] >= target_price and y[0] <= target_price) or (y[-1] <= target_price and y[0] >= target_price):
            return "Целевая цена уже достигнута в последние 24 часа."

        # Логарифмическая аппроксимация (экспоненциальный тренд)
        try:
            coeffs = np.polyfit(x, np.log(y), 1)
        except:
            return "Недостаточно данных для прогноза."

        growth_rate = coeffs[0]
        intercept = coeffs[1]

        if growth_rate == 0:
            return "Тренд плоский, прогноз невозможен."

        # Решаем уравнение: target_price = exp(growth_rate * t + intercept)
        t_target = (np.log(target_price) - intercept) / growth_rate

        hours_to_target = t_target - len(x) + 1

        if hours_to_target <= 0:
            return "Целевая цена будет достигнута очень скоро."

        eta = datetime.datetime.utcnow() + datetime.timedelta(hours=hours_to_target)
        return f"Ожидаемое время достижения цели: {eta} UTC (~{hours_to_target:.1f} ч)"

