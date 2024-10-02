import yfinance as yf

def get_current_price(asset_code):
    asset = yf.Ticker(asset_code + '.sa')
    return asset.history().tail(1)['Close'].values[0]

def get_previous_close_price(asset_code):
    asset = yf.Ticker(asset_code + '.sa')
    historical_data = asset.history(period="2d")  # Fetch 2 days of historical data
    previous_close = historical_data['Close'].iloc[0]  # Close price of the previous day
    return previous_close
