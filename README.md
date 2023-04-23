
# RESTAPI_FASTAPI

Welcome to Trades REST API, a powerful tool for accessing and managing trade data. 
- This API is designed to provide real-time access to all trade-related information, from asset class and instrument details to counterparty and trader data. 
- With this API, you can easily retrieve a list of all trades stored in our database and filter them by various parameters such as buy/sell indicator, asset class, counterparty, and trader name. 
- Each trade is represented by a well-defined schema that includes all relevant details such as trade date/time, trade ID, and trade details (price and quantity).

The app will appear like this using swagger UI
![readme](https://user-images.githubusercontent.com/79595858/233818745-d84a2556-0fda-4d33-8bb5-01189d69fbcd.jpg)







## Database
The mocked database for testing purpose of all the api calls is created  using SQLite3 and stored in "trades.db" file.
-  I implemented SQLite3 in the REST API project for storing the trade data because it is a lightweight and self-contained database system
- SQLite3 also has the advantage of not requiring a separate server process or system. Instead, it simply reads and writes to a file on the local disk, which is quite fast and efficient.
## Schema_model
```
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")

    price: float = Field(description="The price of the Trade.")

    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")

    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")

    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")

    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")

    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")

    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")

    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")

    trader: str = Field(description="The name of the Trader")

```

This will look something like into the database:
```
{
  "asset_class": "assetclass",
  "counterparty": "counterparty",
  "instrument_id": "drum1",
  "instrument_name": "drum",
  "trade_date_time": "2023-04-21T03:57:11.269000+00:00",
  "trade_details": {
    "buy_sell_indicator": "buy",
    "price": 50,
    "quantity": 6
  },
  "trade_id": "1",
  "trader": "Rupesh"
}

```


## Database creation for testing

```

# Endpoint to create trade in the local memory for testing
@app.post("/trades")
async def create_trade(trade: Trade)
```
![createTrades](https://user-images.githubusercontent.com/79595858/233819096-6d97000e-bbcf-4e8f-b5bb-a3d460ef6016.jpg)

The Response will be like this:

![createTradeResponse](https://user-images.githubusercontent.com/79595858/233819283-f99a0335-3c94-47b3-a693-2e3b42661d9e.jpg)


## Listing trades

This is the endpoint for returing all the trades created into the database in the form of list.

```
#EndPoint to fetch a list of available trades
@app.get('/trades/gettradelist')
async def get_trades_list()
```

The request will look like this:

![ListingtradesResponse](https://user-images.githubusercontent.com/79595858/233819392-da6a5ccb-bc11-41f8-911c-fc26d5e72ce7.jpg)


## Fetching the single trade against trade id

As trade id will be unique so we will be able to fetch the trade by passing it as the query parameter.

```
# EndPoint to fetch single trade with the trade_id
@app.get("/trades/{trade_id}")
async def get_trade_by_tradeid(trade_id: str):

```
Query parameter input

![tradebytradeid](https://user-images.githubusercontent.com/79595858/233819564-0c45f0ac-6bd1-441c-ae6c-f99d3555dfbb.jpg)

Response will be:
![responsetraidid](https://user-images.githubusercontent.com/79595858/233819660-4057edf3-37ac-40e6-8778-0a3580911ca7.jpg)


## Searching trades

The user will be able to search the trade on the basis of following field as the query parameter.

- counterparty
- instrumentId
- instrumentName
- trader

The output query will be sorted in the descending order according to trade_date_time so that the latest trades can be viewed at the top.

```
## EndPoint to search the trade details using the counterparty,instrument_id,trader,instrument_ name
@app.get("/trades/search/details")
async def search_trades(
    counterparty: str = None,
    instrument_id: str = None,
    trader: str = None,
    instrument_name: str = None
):
```

Query parameter for input view:
![searches](https://user-images.githubusercontent.com/79595858/233819893-e200824e-f417-4317-981d-fa66ebd40a50.jpg)


Response view:
![searchresponse](https://user-images.githubusercontent.com/79595858/233819939-6809657f-518f-4017-a67b-45a199016757.jpg)





## Advanced Filtering

The endpoints under this section are capable of doing the following optional query parameter

| Parameter  | Description |
| ------------- | ------------- |
| assetClass  | Asset class of the trade.  |
| end  | The maximum date for the tradeDateTime field.  |
|  maxprice | The maximum value for the tradeDetails.price field.  |
| minprice | The minimum value for the tradeDetails.price field.  |
| start  | The minimum date for the tradeDateTime field.  |
| tradetype  | The tradeDetails.buySellIndicator is a BUY or SELL  |

On the basis of max_price and min_price

![price](https://user-images.githubusercontent.com/79595858/233820320-3b479b0f-e695-4590-87b4-09a230698cea.jpg)


![priceresponse](https://user-images.githubusercontent.com/79595858/233820324-4a9ff4f9-95b3-4a2d-b8d5-44387efd4a30.jpg)


On the basis of trade_date_time:
- The query will be returned in the sorted order by latest date

![date](https://user-images.githubusercontent.com/79595858/233820439-320d8509-15bc-4c5e-8447-a59daa66c06c.jpg)
![dateresponse](https://user-images.githubusercontent.com/79595858/233820441-cdb02892-6826-4f96-a453-46e259146916.jpg)



On the basis of asset_class

![assetclass](https://user-images.githubusercontent.com/79595858/233820520-fc9be162-f16f-449f-b951-833f2efb4e3f.jpg)


![assetclassresponse](https://user-images.githubusercontent.com/79595858/233820524-db1b5e00-9256-4701-aa83-2805174b7b79.jpg)






## Scope of Furthur improvement
I am looking forward to paginate these responses that large database queries can be returned according to the limit and offset according to the pages available.