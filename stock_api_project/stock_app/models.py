from django.db import models

class Stock(models.Model):
    """
    Represents a stock and its daily price data.
    """
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    class Meta:
        unique_together = ('symbol', 'date')
        ordering = ['-date']
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
