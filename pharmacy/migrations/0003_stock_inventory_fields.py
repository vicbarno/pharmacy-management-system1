from django.db import migrations, models
import decimal


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0002_alter_adminhod_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='item_id',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='buying_price',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='selling_price',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='stock',
            name='supplier',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]