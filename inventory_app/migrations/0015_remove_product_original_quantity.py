from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0014_fix_order_id_sequence'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='original_quantity',
        ),
    ]