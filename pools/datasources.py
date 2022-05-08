import json
import logging
import time

# import urllib
import urllib.request

import pandas as pd


# известные источники
# https://blog.rmotr.com/top-5-free-apis-to-access-historical-cryptocurrencies-data-2438adc8b62
# https://finance.yahoo.com/quote/XTZ-USD?p=XTZ-USD

# https://docs.spicyswap.xyz/tutorial-extras/api-reference
#
# https://spicya.sdaotools.xyz/api/rest/TokenList
# https://spicya.sdaotools.xyz/api/rest/TokenDailyMetrics?_ilike=KT1KRvNVubq64ttPbQarxec5XdS6ZQU4DVD2:0


def get_json(json_url, error_msg=""):
    for attemp in range(5):
        try:
            logging.info(json_url)
            with urllib.request.urlopen(json_url, timeout=10) as url:
                parsed = json.loads(url.read().decode())
                return parsed
        except Exception:
            time.sleep(1)
            logging.exception(f"attempt {attemp}: {error_msg} for {json_url}")


class SpicyaDataSource:
    REST_URL = "https://spicya.sdaotools.xyz/api/rest/"

    def __init__(self):
        self.tokens = self.get_tokens_data()

    def symbols(self):
        return list(self.tokens)

    def load_data(self, symbol, from_date):
        pass

    def get_hash(self, symbol: str):
        symbol = symbol.lower()
        if symbol not in self.tokens:
            raise ValueError(f"symbol {symbol} not found. available symbols = {self.tokens.keys()}")
        return self.tokens[symbol]['tag']

    def get_tokens_data(self):
        json_data = get_json(f"{self.REST_URL}/TokenList")

        tokens = json_data.get("tokens", [])
        result = {token["symbol"].lower(): token for token in tokens}
        logging.info(f'loaded {result.keys()} symbols from spicya data')
        return result

    def get_symbol_history(self, symbol):
        symbol = symbol.lower()
        if symbol not in self.tokens:
            raise ValueError(f"can't find symbol {symbol} in tokens registry")

        symbol_data = self.tokens[symbol]
        tag_value = symbol_data["tag"]

        token_daily_metrics = get_json(f"{self.REST_URL}/TokenDailyMetrics?_ilike={tag_value}")
        day_data = token_daily_metrics["token_day_data"]

        result_df = pd.DataFrame(day_data)
        result_df["day"] = pd.to_datetime(result_df["day"])
        result_df['token'] = result_df['tag']
        result_df.sort_values("day", inplace=True)

        result_df.rename(
            columns={
                "dailyvolumextz": "volume",
                "totalliquidityxtz": "liquidity",
                "derivedxtz_high": "high",
                "derivedxtz_low": "low",
                "derivedxtz_open": "open",
                "derivedxtz_close": "close",
            },
            inplace=True,
        )

        return result_df

    def get_history(self, symbols):
        dfs = list()
        for symbol in symbols:
            symbol_history = self.get_symbol_history(symbol)
            dfs.append(symbol_history)

        return pd.concat(dfs).sort_values('day').copy()
