from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData
import requests
import json
import datetime

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


@csrf_exempt
def get_stock_data(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        ticker = request.POST.get('ticker', 'null').upper()

        # Check if the data for the given ticker and the latest trading day is already in the database
        latest_trading_day = datetime.date.today()
        existing_data = StockData.objects.filter(symbol=ticker, latest_trading_day=latest_trading_day).first()
        
        if existing_data:
            output_dictionary = {
                'symbol': existing_data.symbol,
                'open': str(existing_data.open),
                'high': str(existing_data.high),
                'low': str(existing_data.low),
                'price': str(existing_data.price),
                'volume': existing_data.volume,
                'latest_trading_day': existing_data.latest_trading_day,
                'previous_close': str(existing_data.previous_close),
                'change': str(existing_data.change),
                'change_percent': existing_data.change_percent,
            }
            return JsonResponse(output_dictionary)

        # Obtain stock data from Alpha Vantage API
        quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={APIKEY}'
        print('QUOTE URL', quote_url, '%'*80, requests.get(quote_url).json())
        quote_data = requests.get(quote_url).json()['Global Quote']

        stock_data = StockData.objects.create(
            symbol=quote_data['01. symbol'],
            open=quote_data['02. open'],
            high=quote_data['03. high'],
            low=quote_data['04. low'],
            price=quote_data['05. price'],
            volume=quote_data['06. volume'],
            latest_trading_day=quote_data['07. latest trading day'],
            previous_close=quote_data['08. previous close'],
            change=quote_data['09. change'],
            change_percent=quote_data['10. change percent'],
        )

        output_dictionary = {
            'symbol': stock_data.symbol,
            'open': str(stock_data.open),
            'high': str(stock_data.high),
            'low': str(stock_data.low),
            'price': str(stock_data.price),
            'volume': stock_data.volume,
            'latest_trading_day': stock_data.latest_trading_day,
            'previous_close': str(stock_data.previous_close),
            'change': str(stock_data.change),
            'change_percent': stock_data.change_percent,
        }

        return JsonResponse(output_dictionary)

    return JsonResponse({'error': 'Not an AJAX request'}, status=400)