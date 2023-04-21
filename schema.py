from pydantic import BaseModel,Field
from typing import Optional
import datetime as dt

class TradeDetails(BaseModel):
    buy_sell_indicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: str = Field(description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrument_id: str = Field(description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrument_name: str = Field(description="The name of the instrument traded.")
    trade_date_time: dt.datetime = Field(description="The date-time the Trade was executed")
    trade_details: TradeDetails = Field(description="The details of the trade, i.e. price, quantity")
    trade_id: Optional[str] = Field(default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")
