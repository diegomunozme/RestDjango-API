from django.shortcuts import render
from .models import StockData
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

APIKEY = 'MBSDTIBYI56I8KVA'

def home(request):
    '''
    Renders the home.html file for front end use
    '''
    return render(request, 'home.html', {})

def validate_ticker(ticker):
    '''
    
    '''
    ticker = ticker.strip().upper()
    if not ticker.isalnum() or len(ticker) > 10:
        return None
    return ticker

def fetch_stock_data_from_alphaVantage(ticker):
    '''
    Helper function that pulls the stock data from alphaVantage live API.
    '''
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
        # Add to database, wll be a new row
        StockData.objects.create(
            symbol=quote_data['01. symbol'],
            price=price,
            change=quote_data['09. change'],
            change_percent=quote_data['10. change percent'],
            latest_trading_day=latest_trading_day,
        )
        return stock_data, None
    return None, "Stock data not found"

def format_stock_data(existing_data):
    return {
        "symbol": existing_data.symbol,
        "price": existing_data.price,
        "change": existing_data.change,
        "change_percent": existing_data.change_percent,
        "latest_trading_day": existing_data.latest_trading_day.strftime('%Y-%m-%d')
    }

@api_view(['GET'])
def get_stock_prices(request):
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
            api_data, error = fetch_stock_data_from_alphaVantage(ticker)
            if api_data:
                stock_data.append(api_data)

    if not stock_data:
        return Response({"error": "No valid stock data found"}, status=400)
        
    return Response(stock_data)

@api_view(['GET'])
def get_stock_price(request, ticker):
    try:
        ticker = validate_ticker(ticker)
        if not ticker:
            return Response({"error": "Invalid stock symbol"}, status=400)

        latest_trading_day = datetime.today().date()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()

        if existing_data:
            stock_data = format_stock_data(existing_data)
        else:
            stock_data, error = fetch_stock_data_from_alphaVantage(ticker)
            if not stock_data:
                return Response({"error": error}, status=404)

        return Response(stock_data)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=500)
