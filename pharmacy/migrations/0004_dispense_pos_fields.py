from django.db import migrations, models
import decimal


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0003_stock_inventory_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispense',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='dispense',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='dispense',
            name='payment_method',
            field=models.CharField(default='Cash', max_length=20),
        ),
        migrations.AddField(
            model_name='dispense',
            name='receipt_no',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]