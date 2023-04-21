from fastapi import FastAPI,Depends,HTTPException,Query
from pydantic import BaseModel,Field
import databases
import sqlalchemy
import uvicorn
import uuid

import datetime as dt
from typing import List
from typing import Optional

from typing import List

from pydantic import BaseModel, Field
import sqlite3

app = FastAPI()




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


trades_db = {}


# Create a connection to the database
conn = sqlite3.connect('trades.db')

# Create a Trades table schema
create_table_sql = '''
CREATE TABLE Trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_class TEXT,
    counterparty TEXT,
    instrument_id TEXT NOT NULL,
    instrument_name TEXT NOT NULL,
    trade_date_time TEXT NOT NULL,
    trade_details TEXT NOT NULL,
    trade_id TEXT NOT NULL,
    trader TEXT NOT NULL
);
'''

# Execute the SQL command to create the Trades table
#conn.execute(create_table_sql)

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()


@app.post("/trades")
def create_trade(trade: Trade):
    # Connect to the database
    conn = sqlite3.connect('trades.db')

    # Insert Trade details into the Trades table
    insert_sql = '''
    INSERT INTO Trades (asset_class, counterparty, instrument_id, instrument_name, trade_date_time, trade_details, trade_id, trader)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''

    conn.execute(insert_sql, (trade.asset_class, trade.counterparty, trade.instrument_id, trade.instrument_name,
                              trade.trade_date_time, trade.trade_details.json(), trade.trade_id, trade.trader))

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()

    # Return the created Trade
    return trade



@app.get("/trades/{trade_id}")
def get_trade(trade_id: str):
    # Connect to the database
    conn = sqlite3.connect('trades.db')

    # Retrieve Trade details from the Trades table
    select_sql = '''
    SELECT * FROM Trades WHERE trade_id=?
    '''

    cursor = conn.execute(select_sql, (trade_id,))
    row = cursor.fetchone()

    # Close the connection
    conn.close()

    # If no Trade was found, return a 404 Not Found error
    if row is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Otherwise, parse the Trade details from the row and return them
    trade = Trade(
        asset_class=row[1],
        counterparty=row[2],
        instrument_id=row[3],
        instrument_name=row[4],
        trade_date_time=row[5],
        trade_details=TradeDetails.parse_raw(row[6]),
        trade_id=row[7],
        trader=row[8]
    )

    return trade





# Endpoint to search Trades
@app.get("/trades/search")
def search_trades(
    counterparty: str = None,
    instrument_id: str = None,
    trader: str = None,
    instrument_name: str = None,
):
    # Connect to the SQLite database
    conn = sqlite3.connect("trades.db")
    c = conn.cursor()

    # Build the SQL query based on the provided search parameters
    query = "SELECT * FROM trades"
    conditions = []
    parameters = []
    if counterparty is not None:
        conditions.append("counterparty LIKE ?")
        parameters.append(f"%{counterparty}%")
    if instrument_id is not None:
        conditions.append("instrument_id LIKE ?")
        parameters.append(f"%{instrument_id}%")
    if trader is not None:
        conditions.append("trader LIKE ?")
        parameters.append(f"%{trader}%")
    if instrument_name is not None:
        conditions.append("instrument_name LIKE ?")
        parameters.append(f"%{instrument_name}%")
    if len(conditions) > 0:
        query += f" WHERE {' AND '.join(conditions)}"

    # Execute the SQL query and retrieve the results
    c.execute(query, tuple(parameters))
    trades = []
    for row in c.fetchall():
        trade = {
            "asset_class": row[0],
            "counterparty": row[1],
            "instrument_id": row[2],
            "instrument_name": row[3],
            "trade_date_time": row[4],
            "trade_details": {
                "buy_sell_indicator": row[5],
                "price": row[6],
                "quantity": row[7],
            },
            "trade_id": row[8],
            "trader": row[9],
        }
        trades.append(trade)

    # Close the database connection and return the results
    conn.close()
    return trades