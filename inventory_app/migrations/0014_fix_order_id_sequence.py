from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0013_product_original_quantity'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "SELECT setval(pg_get_serial_sequence('inventory_app_order','id'), "
                "COALESCE((SELECT MAX(id) FROM inventory_app_order), 1), true);"
            ),
            reverse_sql="SELECT 1;",
        ),
        migrations.RunSQL(
            sql=(
                "SELECT setval(pg_get_serial_sequence('inventory_app_productreturn','id'), "
                "COALESCE((SELECT MAX(id) FROM inventory_app_productreturn), 1), true);"
            ),
            reverse_sql="SELECT 1;",
        ),
    ]