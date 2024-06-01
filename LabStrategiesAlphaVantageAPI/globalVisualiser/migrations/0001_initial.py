# Generated by Django 4.2.13 on 2024-05-31 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('open', models.DecimalField(decimal_places=4, max_digits=10)),
                ('high', models.DecimalField(decimal_places=4, max_digits=10)),
                ('low', models.DecimalField(decimal_places=4, max_digits=10)),
                ('price', models.DecimalField(decimal_places=4, max_digits=10)),
                ('volume', models.BigIntegerField()),
                ('latest_trading_day', models.DateField()),
                ('previous_close', models.DecimalField(decimal_places=4, max_digits=10)),
                ('change', models.DecimalField(decimal_places=4, max_digits=10)),
                ('change_percent', models.CharField(max_length=10)),
            ],
        ),
    ]