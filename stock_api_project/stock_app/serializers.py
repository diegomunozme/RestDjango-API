from rest_framework import serializers
from .models import Stock

class StockDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')