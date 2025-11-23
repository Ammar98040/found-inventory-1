from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0015_remove_product_original_quantity'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE inventory_app_auditlog ALTER COLUMN product_id DROP NOT NULL;"
                    ),
                    reverse_sql=(
                        "ALTER TABLE inventory_app_auditlog ALTER COLUMN product_id SET NOT NULL;"
                    ),
                ),
                migrations.RunSQL(
                    sql=(
                        "DO $$\n"
                        "DECLARE fk_name text;\n"
                        "BEGIN\n"
                        "  SELECT tc.constraint_name INTO fk_name\n"
                        "  FROM information_schema.table_constraints tc\n"
                        "  JOIN information_schema.key_column_usage kcu\n"
                        "    ON tc.constraint_name = kcu.constraint_name\n"
                        "  WHERE tc.table_name = 'inventory_app_auditlog'\n"
                        "    AND tc.constraint_type = 'FOREIGN KEY'\n"
                        "    AND kcu.column_name = 'product_id';\n"
                        "  IF fk_name IS NOT NULL THEN\n"
                        "    EXECUTE format('ALTER TABLE inventory_app_auditlog DROP CONSTRAINT %I', fk_name);\n"
                        "  END IF;\n"
                        "  EXECUTE 'ALTER TABLE inventory_app_auditlog\n"
                        "           ADD CONSTRAINT auditlog_product_fk\n"
                        "           FOREIGN KEY (product_id) REFERENCES inventory_app_product(id) ON DELETE SET NULL';\n"
                        "END$$;"
                    ),
                    reverse_sql=(
                        "DO $$\n"
                        "BEGIN\n"
                        "  BEGIN\n"
                        "    EXECUTE 'ALTER TABLE inventory_app_auditlog DROP CONSTRAINT auditlog_product_fk';\n"
                        "  EXCEPTION WHEN others THEN NULL;\n"
                        "  END;\n"
                        "END$$;"
                    ),
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='auditlog',
                    name='product',
                    field=models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_logs', to='inventory_app.product', verbose_name='المنتج'),
                ),
            ],
        ),
    ]