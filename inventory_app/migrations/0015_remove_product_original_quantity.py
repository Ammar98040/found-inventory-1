from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0014_fix_order_id_sequence'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE inventory_app_product "
                        "DROP COLUMN IF EXISTS original_quantity;"
                    ),
                    reverse_sql=(
                        "ALTER TABLE inventory_app_product "
                        "ADD COLUMN original_quantity integer NOT NULL DEFAULT 0;"
                    ),
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='product',
                    name='original_quantity',
                ),
            ],
        ),
    ]