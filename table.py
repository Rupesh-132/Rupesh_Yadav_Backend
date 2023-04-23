# Create a Trades table schema
create_table_sql = '''
CREATE TABLE Trades (
    id INTEGER PRIMARY KEY,
    asset_class varchar,
    counterparty varchar,
    instrument_id varchar NOT NULL,
    instrument_name varchar NOT NULL,
    trade_date_time varchar NOT NULL,
    trade_details jason NOT NULL,
    trade_id varchar NOT NULL UNIQUE,
    trader varchar NOT NULL,
    trade_buy_sell_indicator varchar
);
'''

