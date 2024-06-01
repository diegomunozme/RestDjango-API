from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Stock
from unittest.mock import patch

class StockModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            date='2023-01-01',
            open_price=100.0,
            high_price=110.0,
            low_price=90.0,
            close_price=105.0,
            volume=10000
        )

    def test_stock_creation(self):
        self.assertEqual(self.stock.symbol, 'AAPL')
        self.assertEqual(self.stock.open_price, 100.0)

class StockDailyViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.stock = Stock.objects.create(
            symbol='AAPL',
            date='2023-01-01',
            open_price=100.0,
            high_price=110.0,
            low_price=90.0,
            close_price=105.0,
            volume=10000
        )
        self.url = reverse('stockdailyview')

    def test_get_stock_data_from_db(self):
        response = self.client.get(self.url, {'symbols': 'AAPL', 'start_date': '2023-01-01', 'end_date': '2023-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['symbol'], 'AAPL')

    @patch('requests.get')
    def test_get_stock_data_from_api(self, mock_get):
        mock_response = {
            "Time Series (Daily)": {
                "2023-01-01": {
                    "1. open": "120.00",
                    "2. high": "125.00",
                    "3. low": "115.00",
                    "4. close": "123.00",
                    "6. volume": "15000"
                }
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(self.url, {'symbols': 'GOOG', 'start_date': '2023-01-01', 'end_date': '2023-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['symbol'], 'GOOG')
        self.assertEqual(response.data[0]['open_price'], 120.00)
