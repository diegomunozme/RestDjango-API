from django.urls import path
from .views import StockDailyView

urlpatterns = [
    path('stock-daily/', StockDailyView.as_view(), name='stockdailyview'),
]