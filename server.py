import uvicorn
from fastapi import FastAPI
from typing import Union

from api import IBapi
from time import sleep

api = IBapi()
app = FastAPI(title="Skynet sbapi", version="0.0.1")


@app.on_event("startup")
def startup_event():
    api.init('172.29.0.109', 4002, 123)
    # estas lineas son para poner que se pueda obtener precios en delay
    sleep(1)
    api.reqMarketDataType(3)


@app.on_event("shutdown")
def shutdown_event():
    api.disconnect()


@app.get("/positions")
def get_positions():
    return api.getPositions()


@app.get("/orders")
def get_orders():
    return api.getOrders()


@app.get("/price/{symbol}")
def get_symbol_price(symbol: str, secType: str = 'STK'):
    return api.getSymbolPrice(symbol, secType)


if __name__ == "__main__":
    uvicorn.run("server:app", host='0.0.0.0', port=4000, log_level="info")
