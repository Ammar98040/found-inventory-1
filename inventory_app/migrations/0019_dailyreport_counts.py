from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0017_auditlog_product_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreportarchive',
            name='quantities_added',
            field=models.IntegerField(default=0, verbose_name='كميات مضافة (عدد عمليات)'),
        ),
        migrations.AddField(
            model_name='dailyreportarchive',
            name='locations_removed',
            field=models.IntegerField(default=0, verbose_name='مواقع ملغاة الربط'),
        ),
    ]