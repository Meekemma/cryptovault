# Generated by Django 3.2 on 2025-02-22 06:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='balance',
            options={},
        ),
        migrations.AlterField(
            model_name='withdrawalrequest',
            name='crypto_currency',
            field=models.CharField(blank=True, choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT', 'Tether'), ('BNB', 'Binance Coin'), ('SOL', 'Solana'), ('BCH', 'Bitcoin Cash')], max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(max_length=255)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='BTC', max_length=10)),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('verified_by_admin', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
