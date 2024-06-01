from django.db import models

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    open = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()
    latest_trading_day = models.DateField()
    previous_close = models.DecimalField(max_digits=10, decimal_places=4)
    change = models.DecimalField(max_digits=10, decimal_places=4)
    change_percent = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol
