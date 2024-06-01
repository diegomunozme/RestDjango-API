from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import Stock
from .serializers import StockDailySerializer

class StockDailyView(APIView):
    """
    This class handles retrieving daily stock data either from Alpha Vantage API or from the SQLite database.
    """
    def get(self, request):
        stock_symbols = request.query_params.get('symbols', '').split(',')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        api_key = 'CPEP1P5375AK6428'
        output_size = 'full'  # Retrieve the full history
        
        for stock_symbol in stock_symbols:
            # Check if the daily data exists in the database
            daily_data = Stock.objects.filter(symbol=stock_symbol, date__range=(start_date, end_date)).order_by('date') 
            
            if not daily_data:
                # Fetch daily data from Alpha Vantage API
                url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={api_key}'
                response = requests.get(url)
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    daily_data = []
                    for date, prices in data['Time Series (Daily)'].items():
                        if start_date <= date <= end_date:
                            stock_data = Stock(
                                symbol=stock_symbol,
                                date=date,
                                open_price=prices['1. open'],
                                high_price=prices['2. high'],
                                low_price=prices['3. low'],
                                close_price=prices['4. close'],
                                volume=int(prices['6. volume'])
                            )
                            daily_data.append(stock_data)
                    
                    # Save daily data to the database
                    Stock.objects.bulk_create(daily_data) 
        
        # Retrieve the daily data for all requested stocks within the specified date range
        daily_data = Stock.objects.filter(symbol__in=stock_symbols, date__range=(start_date, end_date)).order_by('symbol', 'date') 
        serializer = StockDailySerializer(daily_data, many=True)
        return Response(serializer.data)