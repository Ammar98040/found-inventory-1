from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_app', '0019_dailyreport_counts'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DailyReportArchive',
        ),
    ]