import json
from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
from inventory_app.models import Product, Location, Warehouse, AuditLog
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
            with open(input_file, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            try:
                data = json.loads(raw_text)
                self.stdout.write(self.style.SUCCESS('✓ تم قراءة الملف بنجاح'))
            except json.JSONDecodeError:
                data = None
                self.stdout.write(self.style.WARNING('⚠️ الملف غير صالح JSON بشكل كامل، سيتم استخدام آلية استيراد جزئي'))
            
            if data and 'export_info' in data:
                export_info = data['export_info']
                self.stdout.write(self.style.SUCCESS(f"✓ تاريخ التصدير: {export_info.get('date', 'غير معروف')}"))
            
            self.stdout.write(self.style.WARNING('\n📊 محتوى النسخ الاحتياطي:'))
            if data:
                for key in ['warehouses', 'locations', 'products', 'audit_logs']:
                    count = len(data.get(key, []))
                    self.stdout.write(f'  - {key}: {count}')
            else:
                def collect_objects(text, model_key):
                    target = f'"model": "inventory_app.{model_key}"'
                    objs = []
                    buf = []
                    depth = 0
                    in_string = False
                    escape = False
                    for ch in text:
                        if escape:
                            escape = False
                            continue
                        if ch == '\\':
                            escape = True
                            continue
                        if ch == '"':
                            in_string = not in_string
                            continue
                        if in_string:
                            continue
                        if ch == '{':
                            if depth == 0:
                                buf = ['{']
                            else:
                                buf.append('{')
                            depth += 1
                        elif ch == '}':
                            buf.append('}')
                            depth -= 1
                            if depth == 0:
                                obj_text = ''.join(buf).strip()
                                if target in obj_text:
                                    try:
                                        json.loads(obj_text)
                                        objs.append(obj_text)
                                    except json.JSONDecodeError:
                                        pass
                                buf = []
                        else:
                            if depth > 0:
                                buf.append(ch)
                    if not objs:
                        return None
                    return '[' + ',\n'.join(objs) + ']'
                counts_preview = {}
                mapping = {
                    'warehouses': 'warehouse',
                    'locations': 'location',
                    'products': 'product',
                    'audit_logs': 'auditlog',
                }
                for key, mk in mapping.items():
                    arr_text = collect_objects(raw_text, mk)
                    counts_preview[key] = 0 if arr_text is None else arr_text.count('"model"')
                for k, v in counts_preview.items():
                    self.stdout.write(f'  - {k}: {v}')
            
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
                    Product.objects.all().delete()
                    Location.objects.all().delete()
                    Warehouse.objects.all().delete()
                    
                    self.stdout.write(self.style.SUCCESS('✓ تم الحذف'))
                
                # استيراد البيانات
                self.stdout.write(self.style.WARNING('\nبدء الاستيراد...'))
                
                if data and 'warehouses' in data and data['warehouses']:
                    self.stdout.write('  - استيراد المستودعات...')
                    objects = serializers.deserialize('json', json.dumps(data['warehouses']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["warehouses"])} مستودع'))
                elif not data:
                    arr_text = collect_objects(raw_text, 'warehouse')
                    if arr_text:
                        self.stdout.write('  - استيراد المستودعات...')
                        objects = serializers.deserialize('json', arr_text)
                        c = 0
                        for obj in objects:
                            obj.save()
                            c += 1
                        self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {c} مستودع'))
                
                if data and 'locations' in data and data['locations']:
                    self.stdout.write('  - استيراد الأماكن...')
                    objects = serializers.deserialize('json', json.dumps(data['locations']))
                    for obj in objects:
                        obj.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {len(data["locations"])} مكان'))
                elif not data:
                    arr_text = collect_objects(raw_text, 'location')
                    if arr_text:
                        self.stdout.write('  - استيراد الأماكن...')
                        objects = serializers.deserialize('json', arr_text)
                        c = 0
                        for obj in objects:
                            obj.save()
                            c += 1
                        self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {c} مكان'))
                
                if data and 'products' in data and data['products']:
                    self.stdout.write('  - استيراد المنتجات...')
                    objects = serializers.deserialize('json', json.dumps(data['products']))
                    c = 0
                    for obj in objects:
                        inst = obj.object
                        lid = getattr(inst, 'location_id', None)
                        if lid is not None and lid != 0 and not Location.objects.filter(pk=lid).exists():
                            continue
                        obj.save()
                        c += 1
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {c} منتج'))
                elif not data:
                    arr_text = collect_objects(raw_text, 'product')
                    if arr_text:
                        self.stdout.write('  - استيراد المنتجات...')
                        objects = serializers.deserialize('json', arr_text)
                        c = 0
                        for obj in objects:
                            inst = obj.object
                            lid = getattr(inst, 'location_id', None)
                            if lid is not None and lid != 0 and not Location.objects.filter(pk=lid).exists():
                                continue
                            obj.save()
                            c += 1
                        self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {c} منتج'))
                
                if data and 'audit_logs' in data and data['audit_logs']:
                    self.stdout.write('  - استيراد سجلات العمليات...')
                    objects = serializers.deserialize('json', json.dumps(data['audit_logs']))
                    c = 0
                    for obj in objects:
                        inst = obj.object
                        pid = getattr(inst, 'product_id', None)
                        if pid is not None and pid != 0 and not Product.objects.filter(pk=pid).exists():
                            continue
                        obj.save()
                        c += 1
                    self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {c} سجل'))
                elif not data:
                    arr_text = collect_objects(raw_text, 'auditlog')
                    if arr_text:
                        self.stdout.write('  - استيراد سجلات العمليات...')
                        objects = serializers.deserialize('json', arr_text)
                        c = 0
                        for obj in objects:
                            inst = obj.object
                            pid = getattr(inst, 'product_id', None)
                            if pid is not None and pid != 0 and not Product.objects.filter(pk=pid).exists():
                                continue
                            obj.save()
                            c += 1
                        self.stdout.write(self.style.SUCCESS(f'    ✓ تم استيراد {c} سجل'))
                
                # لا يوجد تقارير يومية بعد الإزالة
            
            self.stdout.write(self.style.SUCCESS('\n✓ تم الاستيراد بنجاح!'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'✗ الملف غير موجود: {input_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ حدث خطأ أثناء الاستيراد: {str(e)}'))
            raise e
