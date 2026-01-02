# دليل رفع النظام على VPS (بيئة الإنتاج)

هذا الدليل يشرح كيفية إعداد السيرفر (Ubuntu/Debian) وتشغيل النظام باستخدام Nginx و Gunicorn و PostgreSQL.

## 1. التحضير الأولي
1. قم برفع ملفات المشروع إلى السيرفر (مثلاً في المسار `/root/found-inventory`).
2. تأكد من وجود ملف `requirements.txt` المحدث.

## 2. إعداد البيئة
شغل السكريبت المساعد لتثبيت البرامج الضرورية:
```bash
chmod +x deployment/setup_vps.sh
./deployment/setup_vps.sh
```

## 3. إعداد قاعدة البيانات
قم بإنشاء قاعدة البيانات والمستخدم (تأكد من تغيير كلمة المرور):
```bash
sudo -u postgres psql
CREATE DATABASE inventory_db;
CREATE USER inventory_user WITH PASSWORD 'your_strong_password';
ALTER ROLE inventory_user SET client_encoding TO 'utf8';
ALTER ROLE inventory_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE inventory_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
\q
```

## 4. إعداد المشروع
1. أنشئ البيئة الافتراضية وفعلها:
```bash
virtualenv venv
source venv/bin/activate
```
2. ثبت المكتبات:
```bash
pip install -r requirements.txt
```
3. إعداد ملف `.env`:
   - انسخ ملف `.env.production.example` إلى `.env`.
   - عدل القيم بداخله (SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS).

4. ترحيل قاعدة البيانات وجمع الملفات الثابتة:
```bash
python found-inventory-1/manage.py migrate
python found-inventory-1/manage.py collectstatic
```

## 5. إعداد Gunicorn و Systemd
1. انسخ ملف الخدمة:
```bash
sudo cp found-inventory-1/deployment/inventory.service /etc/systemd/system/
```
2. شغل الخدمة:
```bash
sudo systemctl start inventory
sudo systemctl enable inventory
```

## 6. إعداد Nginx
1. انسخ ملف الإعدادات:
```bash
sudo cp found-inventory-1/deployment/inventory_nginx.conf /etc/nginx/sites-available/inventory
```
2. فعل الموقع:
```bash
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled
```
3. اختبر الإعدادات وأعد تشغيل Nginx:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 7. الأمان (HTTPS)
استخدم Certbot لتفعيل HTTPS مجاناً:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```
