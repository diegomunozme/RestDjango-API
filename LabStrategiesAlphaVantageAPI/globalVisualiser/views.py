from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData
import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

APIKEY = 'MBSDTIBYI56I8KVA'

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData

import requests
import json




DATABASE_ACCESS = True 
#if False, the app will always query the Alpha Vantage APIs regardless of whether the stock data for a given ticker is already in the local database


#view function for rendering home.html
def home(request):
    return render(request, 'home.html', {})


@api_view(['GET'])
def get_stock_prices(request):
    ids = request.GET.get('ids', '')
    tickers = ids.split(',')
    stock_data = []

    for ticker in tickers:
        ticker = ticker.strip().upper()
        latest_trading_day = datetime.today().date()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()

        if existing_data:
            stock_data.append({
                "symbol": existing_data.symbol,
                "open": existing_data.open,
                "high": existing_data.high,
                "low": existing_data.low,
                "price": existing_data.price,
                "volume": existing_data.volume,
                "latest_trading_day": existing_data.latest_trading_day,
                "previous_close": existing_data.previous_close,
                "change": existing_data.change,
                "change_percent": existing_data.change_percent
            })
        else:
            quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={APIKEY}'
            quote_data = requests.get(quote_url).json().get('Global Quote', {})
            if quote_data:
                price = quote_data.get('05. price')
                latest_trading_day = datetime.strptime(quote_data['07. latest trading day'], '%Y-%m-%d').date()
                stock_data.append({
                    "symbol": quote_data['01. symbol'],
                    "open": quote_data['02. open'],
                    "high": quote_data['03. high'],
                    "low": quote_data['04. low'],
                    "price": price,
                    "volume": quote_data['06. volume'],
                    "latest_trading_day": latest_trading_day,
                    "previous_close": quote_data['08. previous close'],
                    "change": quote_data['09. change'],
                    "change_percent": quote_data['10. change percent']
                })
                StockData.objects.create(
                    symbol=quote_data['01. symbol'],
                    open=quote_data['02. open'],
                    high=quote_data['03. high'],
                    low=quote_data['04. low'],
                    price=price,
                    volume=quote_data['06. volume'],
                    latest_trading_day=latest_trading_day,
                    previous_close=quote_data['08. previous close'],
                    change=quote_data['09. change'],
                    change_percent=quote_data['10. change percent'],
                )
            else:
                return Response({"error": f"Stock data for {ticker} not found"}, status=404)

    return Response(stock_data)


@api_view(['GET'])
def get_stock_price(request, ticker):
    ticker = ticker.strip().upper()
    latest_trading_day = datetime.today().date()
    existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()

    if existing_data:
        stock_data = {
            "symbol": existing_data.symbol,
            "open": existing_data.open,
            "high": existing_data.high,
            "low": existing_data.low,
            "price": existing_data.price,
            "volume": existing_data.volume,
            "latest_trading_day": existing_data.latest_trading_day,
            "previous_close": existing_data.previous_close,
            "change": existing_data.change,
            "change_percent": existing_data.change_percent
        }
    else:
        quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={APIKEY}'
        quote_data = requests.get(quote_url).json().get('Global Quote', {})
        if quote_data:
            price = quote_data.get('05. price')
            latest_trading_day = datetime.strptime(quote_data['07. latest trading day'], '%Y-%m-%d').date()
            stock_data = {
                "symbol": quote_data['01. symbol'],
                "open": quote_data['02. open'],
                "high": quote_data['03. high'],
                "low": quote_data['04. low'],
                "price": price,
                "volume": quote_data['06. volume'],
                "latest_trading_day": latest_trading_day,
                "previous_close": quote_data['08. previous close'],
                "change": quote_data['09. change'],
                "change_percent": quote_data['10. change percent']
            }
            StockData.objects.create(
                symbol=quote_data['01. symbol'],
                open=quote_data['02. open'],
                high=quote_data['03. high'],
                low=quote_data['04. low'],
                price=price,
                volume=quote_data['06. volume'],
                latest_trading_day=latest_trading_day,
                previous_close=quote_data['08. previous close'],
                change=quote_data['09. change'],
                change_percent=quote_data['10. change percent'],
            )
        else:
            return Response({"error": "Stock data not found"}, status=404)

    return Response(stock_data)

