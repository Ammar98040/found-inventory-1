import json
from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
from inventory_app.models import Product, Location, Warehouse, AuditLog, Order
from datetime import datetime


class Command(BaseCommand):
    help = 'استيراد البيانات من ملف JSON للنسخ الاحتياطي'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            required=True,
            help='مسار ملف النسخ الاحتياطي'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='حذف البيانات الموجودة قبل الاستيراد'
        )
        parser.add_argument(
            '--skip-confirmation',
            action='store_true',
            help='تخطي التأكيد'
        )

    def handle(self, *args, **options):
        input_file = options['input']
        clear_data = options['clear']
        skip_confirmation = options['skip_confirmation']
        
        try:
            # فتح الملف
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stdout.write(self.style.SUCCESS('✓ تم قراءة الملف بنجاح'))
            
            # معلومات التصدير
            if 'export_info' in data:
                export_info = data['export_info']
                self.stdout.write(self.style.SUCCESS(f"✓ تاريخ التصدير: {export_info.get('date', 'غير معروف')}"))
            
            # عرض الإحصائيات
            self.stdout.write(self.style.WARNING('\n📊 محتوى النسخ الاحتياطي:'))
            for key in ['warehouses', 'locations', 'products', 'orders', 'audit_logs']:
                count = len(data.get(key, []))
                self.stdout.write(f'  - {key}: {count}')
            
            # التحقق من حذف البيانات
            if clear_data and not skip_confirmation:
                self.stdout.write(self.style.ERROR('\n⚠️ سيتم حذف جميع البيانات الموجودة!'))
                confirm = input('هل أنت متأكد؟ (اكتب "نعم" للمتابعة): ')
                if confirm != 'نعم':
                    self.stdout.write(self.style.WARNING('تم إلغاء العملية'))
                    return
            
            # بدء الاستيراد
            with transaction.atomic():
                # حذف البيانات الموجودة إذا طُلب
                if clear_data:
                    self.stdout.write(self.style.WARNING('جاري حذف البيانات الموجودة...'))
                    AuditLog.objects.all().delete()
                    Order.objects.all().delete()
                    Product.objects.all().delete()
                    Location.objects.all().delete()
                    Warehouse.objects.all().delete()
                    
                    self.stdout.write(self.style.SUCCESS('✓ تم الحذف'))
                
                # استيراد البيانات
                self.stdout.write(self.style.WARNING('\nبدء الاستيراد...'))
                
                # استيراد المستودعات
                if 'warehouses' in data and data['warehouses']:
                    self.stdout.write('  - استيراد المستودعات...')
                    objects = serializers.deserialize('json', json.dumps(data['warehouses']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["warehouses"])} مستودع'))
                
                # استيراد الأماكن
                if 'locations' in data and data['locations']:
                    self.stdout.write('  - استيراد الأماكن...')
                    objects = serializers.deserialize('json', json.dumps(data['locations']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["locations"])} مكان'))
                
                # استيراد المنتجات
                if 'products' in data and data['products']:
                    self.stdout.write('  - استيراد المنتجات...')
                    objects = serializers.deserialize('json', json.dumps(data['products']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["products"])} منتج'))
                
                # استيراد الطلبات
                if 'orders' in data and data['orders']:
                    self.stdout.write('  - استيراد الطلبات...')
                    objects = serializers.deserialize('json', json.dumps(data['orders']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["orders"])} طلب'))
                
                # استيراد سجلات العمليات
                if 'audit_logs' in data and data['audit_logs']:
                    self.stdout.write('  - استيراد سجلات العمليات...')
                    objects = serializers.deserialize('json', json.dumps(data['audit_logs']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["audit_logs"])} سجل'))
                
                # لا يوجد تقارير يومية بعد الإزالة
            
            self.stdout.write(self.style.SUCCESS('\n✓ تم الاستيراد بنجاح!'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'✗ الملف غير موجود: {input_file}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('✗ الملف غير صالح. تأكد أنه ملف JSON صحيح'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ حدث خطأ أثناء الاستيراد: {str(e)}'))
            raise e
