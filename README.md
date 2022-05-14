python etfs

known pools: http://0.0.0.0:8000/pools

portfolio by owner: http://0.0.0.0:8000/portfolio?owner=tz1LQjdKgiAsHkYMzBH2HFDcynf7QSd5Z4Eg

portfolio emulation curl -H 'content-type: application/json' -XPOST http://localhost:8000/emulate -d'{"assets": [{"symbol": "SPI", "weight": 65}, {"symbol": "WTZ", "weight": 35}]}'

markovitz portfolio optimization curl -H 'content-type: application/json' -XPOST http://localhost:8000/emmarkovitz-optimiz-d'{"assets": [curl -H 'content-type: application/json' -XPOST http://localhost:8000/markovitz-optimize -d'{"assets": [{"symbol": "SPI", "weight": 65}, {"symbol": "WTZ", "weight": 35}]}'