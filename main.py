from fastapi import FastAPI,Depends,HTTPException,Query,status
from pydantic import BaseModel,Field
import uvicorn
from pydantic import parse_obj_as
from pydantic.types import Json

from datetime import datetime 
from typing import List
from typing import Optional

from typing import List

import sqlite3
from table import create_table_sql as Trades
from schemas.schema import Trade,TradeDetails
import json

#creating instance for fastApi
app = FastAPI(
    title='RUPESH_RESTAPI_FASTAPI',
    description='Api for trades',
)

# Create a connection to the database
conn = sqlite3.connect('trades.db')

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()

# Endpoint to create trade in the local memory for testing
@app.post("/trades")
async def create_trade(trade: Trade):
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



#EndPoint to fetch a list of available trades
@app.get('/trades/gettradelist')
async def get_trades_list():
    conn = sqlite3.connect('trades.db')
    c = conn.cursor()
    c.execute("SELECT * FROM trades")
    rows = c.fetchall()
    trades = []
    for row in rows:
        trade_dict = {
            "asset_class": row[1],
            "counterparty": row[2],
            "instrument_id": row[3],
            "instrument_name": row[4],
            "trade_date_time": row[5],
            "trade_details": json.loads(row[6]),
            "trade_id": row[7],
            "trader": row[8]
        }
        trades.append(trade_dict)
    c.close()
    return trades






# EndPoint to fetch single trade with the trade_id
@app.get("/trades/{trade_id}")
async def get_trade_by_tradeid(trade_id: str):
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

    try:
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
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Invalid input: " + str(e))
    
    return trade


## EndPoint to search the trade details using the counterparty,instrument_id,trader,instrument_ name
@app.get("/trades/search/details")
async def search_trades(
    counterparty: str = None,
    instrument_id: str = None,
    trader: str = None,
    instrument_name: str = None
):
    # Connect to the database
    conn = sqlite3.connect('trades.db')

    # Build the WHERE clause of the SQL query based on the provided query parameters
    where_clauses = []
    parameters = []
    
    #searching into the data if according to either any provided fields or all
    if counterparty:
        where_clauses.append("counterparty LIKE ?")
        parameters.append(f"%{counterparty}%")
    if instrument_id:
        where_clauses.append("instrument_id LIKE ?")
        parameters.append(f"{instrument_id}")
    if trader:
        where_clauses.append("trader LIKE ?")
        parameters.append(f"%{trader}%")
    if instrument_name:
        where_clauses.append("instrument_name LIKE ?")
        parameters.append(f"%{instrument_name}%")

    if not where_clauses:
        raise HTTPException(status_code=400, detail="At least one search parameter is required")

    # Combine the WHERE clauses into a single SQL query
    where_clause = " OR ".join(where_clauses)
    
    select_sql = f'''
    SELECT * FROM Trades WHERE {where_clause} ORDER BY trade_date_time DESC
    '''
    
    cursor = conn.execute(select_sql, tuple(parameters))
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # If no Trades were found, return an empty list
    if not rows:
        return []

    # Otherwise, parse the Trade details from the rows and return them
    trades = []
    for row in rows:
        try:
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
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input: " + str(e))

        trades.append(trade)

    return trades



# End point for searching all the trades with particular assser class
@app.get("/trades/search/assetclass/filter{asset_class}")
async def search_acc_assetclass(
    asset_class: str = None,
   
):

    # Connect to the database
    conn = sqlite3.connect('trades.db')

    # Build the WHERE clause of the SQL query based on the provided query parameters
    where_clauses = []
    parameters = []

    if asset_class:
        where_clauses.append("asset_class LIKE ?")
        parameters.append(f"{asset_class}")

    if not where_clauses:
        raise HTTPException(status_code=404, detail="No such asset_class exists")

    # Combine the WHERE clauses into a single SQL query
    where_clause = " OR ".join(where_clauses)
    select_sql = f'''
    SELECT * FROM Trades WHERE {where_clause}
    '''
    cursor = conn.execute(select_sql, tuple(parameters))
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # If no Trades were found, return an empty list
    if not rows:
        return []

    # Otherwise, parse the Trade details from the rows and return them
    trades = []
    for row in rows:

        try: 
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
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input: " + str(e))


        trades.append(trade)

    return trades


# EndPoint to fetch single trade with the trade_id
@app.get("/trades/date_time/filter/{start}/{end}")
async def get_trades_acc_date_time(start: datetime,end:datetime):
    #print(start,end)
    
    #converting a datetime object into a string representation in the format '%Y-%m-%d %H:%M:%S'
    start = start.strftime('%Y-%m-%d %H:%M:%S')
    end = end.strftime('%Y-%m-%d %H:%M:%S')


    # Connect to the database
    conn = sqlite3.connect('trades.db')

    # Retrieve Trade details from the Trades table and sorting the query to fetch the latest  by date
    select_sql = '''
    SELECT * FROM Trades WHERE trade_date_time BETWEEN ? AND ? ORDER BY trade_date_time DESC
    '''

    cursor = conn.execute(select_sql,(start,end))
    rows = cursor.fetchall()

   
    # Close the connection
    conn.close()

    trades = []
    for row in rows:

        try:
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
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input: " + str(e))
        
        trades.append(trade)

    return trades


 #Endpoint to filter data according the min and max price
@app.get("/trades/{mini_price}/{maxi_price}")
async def search_trade_acc_price(mini:float,maxi:float):
    # Connect to the database
    conn = sqlite3.connect('trades.db')
    c = conn.cursor()
    query = f"SELECT * FROM trades"
   
    c.execute(query)
    data = c.fetchall()
    price_data = []
    for item in data:
        try:
           dict_data = json.loads(item[6])
           if mini <= int(dict_data["price"]) <= maxi:
               price_data.append(item)
        except:
            pass

  
    c.close()

    return price_data
    

# Endpoint to filter the trade according to the tradetype
@app.get('/trades/filter/{buy_sell_indicator}')
async def filter_trade_acc_trade_type(buy_sell_indicator:str=None):

    # Connect to the database
    conn = sqlite3.connect('trades.db')
    
    # creating a cursor to iterate row by row in the database
    c = conn.cursor()
    #print(type(c))

    #getting all the records and ordering by asset_class
    query = f"SELECT * FROM trades ORDER BY asset_class"
   
    #excute the query
    c.execute(query)

    #retrived all the matching query and return the data as list
    data = c.fetchall()

    
    # fetching all the data having price range from min_price to max_price
    trade_data = []
    for item in data:
        try:
           dict_data = json.loads(item[6])
           match = dict_data["buy_sell_indicator"].lower()
           if buy_sell_indicator.lower() == match:
               trade_data.append(item)
        except:
            pass

    c.close()
    return trade_data
    

   

    