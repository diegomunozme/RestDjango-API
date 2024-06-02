# globalVisualiser/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData
import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.shortcuts import render

APIKEY = 'MBSDTIBYI56I8KVA'

def home(request):
    return render(request, 'home.html', {})

@api_view(['GET'])
def get_stock_prices(request):
    ids = request.GET.get('ids', '')
    tickers = set(ids.split(','))  # Use a set to remove duplicates
    stock_data = []

    for ticker in tickers:
        ticker = ticker.strip().upper()
        latest_trading_day = datetime.today().date()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()

        if existing_data:
            stock_data.append({
                "symbol": existing_data.symbol,
                "price": existing_data.price,
                "change": existing_data.change,
                "change_percent": existing_data.change_percent,
                "latest_trading_day": existing_data.latest_trading_day
            })
        else:
            quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={APIKEY}'
            quote_data = requests.get(quote_url).json().get('Global Quote', {})
            if quote_data:
                price = quote_data.get('05. price')
                latest_trading_day = datetime.strptime(quote_data['07. latest trading day'], '%Y-%m-%d').date()
                stock_data.append({
                    "symbol": quote_data['01. symbol'],
                    "price": price,
                    "change": quote_data['09. change'],
                    "change_percent": quote_data['10. change percent'],
                    "latest_trading_day": latest_trading_day
                })
                StockData.objects.create(
                    symbol=quote_data['01. symbol'],
                    price=price,
                    change=quote_data['09. change'],
                    change_percent=quote_data['10. change percent'],
                    latest_trading_day=latest_trading_day,
                )
            else:
                return Response({"error": f"Stock data for {ticker} not found"}, status=404)

    return Response(stock_data)

@api_view(['GET'])
def get_stock_price(request, ticker):
    try:
        ticker = ticker.strip().upper()
        if not ticker.isalnum():  # Check if the ticker is alphanumeric
            return Response({"error": "Invalid stock symbol"}, status=400)

        latest_trading_day = datetime.today().date()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()

        if existing_data:
            stock_data = {
                "symbol": existing_data.symbol,
                "price": existing_data.price,
                "change": existing_data.change,
                "change_percent": existing_data.change_percent,
                "latest_trading_day": existing_data.latest_trading_day
            }
        else:
            quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={APIKEY}'
            quote_data = requests.get(quote_url).json().get('Global Quote', {})
            if quote_data:
                price = quote_data.get('05. price')
                latest_trading_day = datetime.strptime(quote_data['07. latest trading day'], '%Y-%m-%d').date()
                stock_data = {
                    "symbol": quote_data['01. symbol'],
                    "price": price,
                    "change": quote_data['09. change'],
                    "change_percent": quote_data['10. change percent'],
                    "latest_trading_day": latest_trading_day
                }
                # adding the data to the database
                StockData.objects.create(
                    symbol=quote_data['01. symbol'],
                    price=price,
                    change=quote_data['09. change'],
                    change_percent=quote_data['10. change percent'],
                    latest_trading_day=latest_trading_day,
                )
            else:
                return Response({"error": "Stock data not found"}, status=404)

        return Response(stock_data)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=500)
