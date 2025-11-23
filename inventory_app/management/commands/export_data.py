import json
import os
from django.core.management.base import BaseCommand
from django.core import serializers
from inventory_app.models import Product, Location, Warehouse, AuditLog
from datetime import datetime


class Command(BaseCommand):
    help = 'تصدير جميع البيانات إلى ملف JSON للنسخ الاحتياطي'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='backup_data.json',
            help='اسم ملف النسخ الاحتياطي'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'json-indent'],
            help='صيغة الملف'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        format_type = options['format']
        
        self.stdout.write(self.style.WARNING('بدء عملية التصدير...'))
        
        try:
            # جمع البيانات من جميع النماذج
            data = {
                'export_info': {
                    'date': datetime.now().isoformat(),
                    'version': '1.0',
                    'description': 'نسخ احتياطي كامل من نظام إدارة المستودع'
                },
                'warehouses': json.loads(serializers.serialize('json', Warehouse.objects.all())),
                'locations': json.loads(serializers.serialize('json', Location.objects.all())),
                'products': json.loads(serializers.serialize('json', Product.objects.all())),
                'audit_logs': json.loads(serializers.serialize('json', AuditLog.objects.all())),
            }
            
            # كتابة الملف
            if format_type == 'json-indent':
                json_data = json.dumps(data, ensure_ascii=False, indent=2)
            else:
                json_data = json.dumps(data, ensure_ascii=False)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            # إحصائيات
            stats = {
                'warehouses': Warehouse.objects.count(),
                'locations': Location.objects.count(),
                'products': Product.objects.count(),
                'audit_logs': AuditLog.objects.count(),
            }
            
            self.stdout.write(self.style.SUCCESS('✓ تم التصدير بنجاح!'))
            self.stdout.write(self.style.SUCCESS(f'✓ اسم الملف: {output_file}'))
            self.stdout.write(self.style.SUCCESS('✓ الإحصائيات:'))
            for key, value in stats.items():
                self.stdout.write(f'  - {key}: {value}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ حدث خطأ أثناء التصدير: {str(e)}'))
            raise e
