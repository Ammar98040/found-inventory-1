from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0016_alter_auditlog_product_setnull'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='product_snapshot',
            field=models.JSONField(blank=True, null=True, verbose_name='لقطة المنتج عند الإجراء'),
        ),
    ]