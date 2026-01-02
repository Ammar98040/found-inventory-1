from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0011_container_product_barcode_product_dozens_per_carton_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='original_quantity',
            field=models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='الكمية الأصلية'),
        ),
    ]