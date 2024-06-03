from django.db import models

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.DecimalField(max_digits=10, decimal_places=2)
    change_percent = models.CharField(max_length=10)
    latest_trading_day = models.DateField()

    class Meta:
        unique_together = ('symbol', 'latest_trading_day')  # Enforce unique combination

    def __str__(self):
        return self.symbol
