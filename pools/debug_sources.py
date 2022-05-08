from pools.datasources import SpicyaDataSource

# from pricing.model import do_forecast

# http://techflare.blog/how-to-calculate-historical-volatility-and-sharpe-ratio-in-python/
# https://bitcoin.org/bitcoin.pdf
# https://tezos.com/whitepaper.pdfhttps://tezos.com/whitepaper.pdf
if __name__ == "__main__":
    source = SpicyaDataSource()
    symbols = source.symbols()
    print(symbols)
    # history = source.get_symbol_history(symbols[1])
    full_history = source.get_history(symbols[:5])
    full_history.to_pickle('full-history.gz')
    # history.to_parquet("history.gz.pq", compression="gzip")
    # do_forecast()
    print(full_history.to_markdown())
