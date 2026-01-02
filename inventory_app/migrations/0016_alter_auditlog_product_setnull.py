from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0015_remove_product_original_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='product',
            field=models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_logs', to='inventory_app.product', verbose_name='المنتج'),
        ),
    ]