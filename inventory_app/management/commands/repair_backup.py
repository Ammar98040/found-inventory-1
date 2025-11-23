import io
import json
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'إصلاح ملف النسخة الاحتياطية JSON عبر استخراج الكائنات الصالحة لكل قسم'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='مسار ملف النسخة الاحتياطية المصدّر')
        parser.add_argument('--output', type=str, required=True, help='مسار الملف الناتج بعد الإصلاح')

    def handle(self, *args, **options):
        input_path = options['input']
        output_path = options['output']

        try:
            data_text = io.open(input_path, 'r', encoding='utf-8', errors='ignore').read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'✗ الملف غير موجود: {input_path}'))
            return

        def collect(text, model_key):
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
            return objs

        warehouses = collect(data_text, 'warehouse')
        locations = collect(data_text, 'location')
        products = collect(data_text, 'product')
        audit_logs = collect(data_text, 'auditlog')

        try:
            export_info = json.loads(data_text).get('export_info', {})
        except Exception:
            export_info = {}

        rebuilt_obj = {
            'export_info': export_info,
            'warehouses': [json.loads(x) for x in warehouses],
            'locations': [json.loads(x) for x in locations],
            'products': [json.loads(x) for x in products],
            'audit_logs': [json.loads(x) for x in audit_logs],
        }

        rebuilt_text = json.dumps(rebuilt_obj, ensure_ascii=False, indent=2)

        io.open(output_path, 'w', encoding='utf-8').write(rebuilt_text)
        self.stdout.write(self.style.SUCCESS(f'✓ تم الإصلاح وكتابة الملف: {output_path}'))