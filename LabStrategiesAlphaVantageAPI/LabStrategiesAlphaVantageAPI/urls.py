#urls.py

from django.contrib import admin
from django.urls import path
import globalVisualiser.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", globalVisualiser.views.home),
    path('stocks/', globalVisualiser.views.get_stock_prices, name='get_stock_prices'),
    path('stocks/<str:ticker>/', globalVisualiser.views.get_stock_price, name='get_stock_price'),
]