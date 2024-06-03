from django.shortcuts import render
from .models import StockData
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

APIKEY = 'MBSDTIBYI56I8KVA'

def home(request):
    return render(request, 'home.html', {})

def validate_ticker(ticker):
    """
    Validate the ticker symbol.
    Returns the ticker in uppercase if valid, otherwise returns None.
    """
    ticker = ticker.strip().upper()
    if not ticker.isalnum() or len(ticker) > 10:
        return None
    return ticker

def fetch_stock_data_from_api(ticker):
    """
    Fetch stock data from the Alpha Vantage API.
    Returns the stock data as a dictionary if successful, otherwise returns None and an error message.
    """
    quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={APIKEY}'
    response = requests.get(quote_url)
    if response.status_code != 200:
        return None, "Failed to fetch data from external API"
    
    quote_data = response.json().get('Global Quote', {})
    if quote_data:
        price = quote_data.get('05. price')
        if not price:
            return None, "Stock data not found"
        
        latest_trading_day = datetime.strptime(quote_data['07. latest trading day'], '%Y-%m-%d').date()
        
        stock_data = {
            "symbol": quote_data['01. symbol'],
            "price": price,
            "change": quote_data['09. change'],
            "change_percent": quote_data['10. change percent'],
            "latest_trading_day": latest_trading_day.strftime('%Y-%m-%d')
        }
        
        # Add to database
        StockData.objects.get_or_create(
            symbol=quote_data['01. symbol'],
            latest_trading_day=latest_trading_day,
            defaults={
                'price': price,
                'change': quote_data['09. change'],
                'change_percent': quote_data['10. change percent']
            }
        )
        
        return stock_data, None
    
    return None, "Stock data not found"

def format_stock_data(existing_data):
    """
    Format the existing stock data from the database for the API response.
    """
    return {
        "symbol": existing_data.symbol,
        "price": existing_data.price,
        "change": existing_data.change,
        "change_percent": existing_data.change_percent,
        "latest_trading_day": existing_data.latest_trading_day.strftime('%Y-%m-%d')
    }

@api_view(['GET'])
def get_stock_prices(request):
    """
    API endpoint to get stock prices for multiple tickers.
    Accepts a comma-separated list of tickers in the 'ids' query parameter.
    Returns the stock data for valid tickers.
    """
    ids = request.GET.get('ids', '')
    if not ids:  # Handle empty request
        return Response({"error": "No stock symbols provided"}, status=400)
    
    tickers = set(ids.split(','))  # Use a set to remove duplicates
    stock_data = []
    
    for ticker in tickers:
        ticker = validate_ticker(ticker)
        if not ticker:  # Skip invalid tickers
            continue
        
        latest_trading_day = datetime.today().date()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()
        
        if existing_data:
            stock_data.append(format_stock_data(existing_data))
        else:
            api_data, error = fetch_stock_data_from_api(ticker)
            if api_data:
                stock_data.append(api_data)
    
    if not stock_data:
        return Response({"error": "No valid stock data found"}, status=400)
    
    return Response(stock_data)

@api_view(['GET'])
def get_stock_price(request, ticker):
    """
    API endpoint to get the stock price for a single ticker.
    Returns the stock data if found, otherwise returns an error response.
    """
    try:
        ticker = validate_ticker(ticker)
        if not ticker:
            return Response({"error": "Invalid stock symbol"}, status=400)
        
        latest_trading_day = datetime.today().date()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()
        
        if existing_data:
            stock_data = format_stock_data(existing_data)
        else:
            stock_data, error = fetch_stock_data_from_api(ticker)
        
        if not stock_data:
            return Response({"error": error}, status=404)
        
        return Response(stock_data)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=500)