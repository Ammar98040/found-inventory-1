import multiprocessing

# اسم المشروع (يجب أن يطابق اسم المجلد الرئيسي أو التطبيق)
command = '/root/found-inventory/venv/bin/gunicorn'
pythonpath = '/root/found-inventory/found-inventory-1'
bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
user = 'root'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=inventory_project.settings'
