# globalVisualiser/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import StockData
from datetime import datetime
from unittest.mock import patch

class StockAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.api_key = 'MBSDTIBYI56I8KVA'
        self.stock_data = {
            'symbol': 'AAPL',
            'price': '152.00',
            'change': '1.00',
            'change_percent': '0.66%',
            'latest_trading_day': datetime.today().date(),
        }
        StockData.objects.create(**self.stock_data)

    def test_get_single_stock_price(self):
        response = self.client.get(reverse('get_stock_price', args=['AAPL']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], self.stock_data['symbol'])
        self.assertEqual(float(response.data['price']), float(self.stock_data['price']))

    @patch('requests.get')
    def test_get_single_stock_price_api(self, mock_get):
        mock_response = {
            'Global Quote': {
                '01. symbol': 'TSLA',
                '05. price': '610.00',
                '07. latest trading day': datetime.today().strftime('%Y-%m-%d'),
                '09. change': '5.00',
                '10. change percent': '0.83%'
            }
        }
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(reverse('get_stock_price', args=['TSLA']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], mock_response['Global Quote']['01. symbol'])
        self.assertEqual(float(response.data['price']), float(mock_response['Global Quote']['05. price']))

    def test_get_multiple_stock_prices(self):
        response = self.client.get(reverse('get_stock_prices'), {'ids': 'AAPL,TSLA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('AAPL', [stock['symbol'] for stock in response.data])
        self.assertEqual(float(response.data[0]['price']), float(self.stock_data['price']))

    @patch('requests.get')
    def test_get_multiple_stock_prices_api(self, mock_get):
        mock_response = {
            'Global Quote': {
                '01. symbol': 'TSLA',
                '05. price': '610.00',
                '07. latest trading day': datetime.today().strftime('%Y-%m-%d'),
                '09. change': '5.00',
                '10. change percent': '0.83%'
            }
        }
        mock_get.side_effect = [mock_response, {}]  # First call returns valid, second returns empty
        response = self.client.get(reverse('get_stock_prices'), {'ids': 'AAPL,INVALID'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('AAPL', [stock['symbol'] for stock in response.data])
        self.assertNotIn('INVALID', [stock['symbol'] for stock in response.data])

    def test_case_insensitivity(self):
        response = self.client.get(reverse('get_stock_price', args=['aapl']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], self.stock_data['symbol'].upper())

    def test_special_characters_in_stock_symbol(self):
        response = self.client.get(reverse('get_stock_price', args=['A@PL!']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_stock_symbols(self):
        response = self.client.get(reverse('get_stock_prices'), {'ids': 'AAPL,AAPL'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('requests.get')
    def test_api_rate_limiting(self, mock_get):
        mock_get.return_value.status_code = 429
        mock_get.return_value.json.return_value = {"Note": "API call frequency is 5 calls per minute and 500 calls per day."}
        response = self.client.get(reverse('get_stock_price', args=['AAPL']))
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('API call frequency', response.data['error'])

    @patch('django.db.models.query.QuerySet.filter')
    def test_database_connection_issues(self, mock_filter):
        mock_filter.side_effect = Exception("Database connection error")
        response = self.client.get(reverse('get_stock_price', args=['AAPL']))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Internal server error')
