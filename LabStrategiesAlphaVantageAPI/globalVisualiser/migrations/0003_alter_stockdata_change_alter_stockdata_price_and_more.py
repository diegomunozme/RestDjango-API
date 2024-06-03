# Generated by Django 4.2.13 on 2024-06-03 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('globalVisualiser', '0002_remove_stockdata_high_remove_stockdata_low_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockdata',
            name='change',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterUniqueTogether(
            name='stockdata',
            unique_together={('symbol', 'latest_trading_day')},
        ),
    ]