# 🔒 دليل إعداد الأمان للنظام

## 📋 الخطوات المطلوبة قبل النشر في الإنتاج

### 1. إنشاء ملف `.env`

قم بنسخ ملف `.env.example` وإعادة تسميته إلى `.env`:

```bash
cp .env.example .env
```

### 2. تحديث المعلومات الحساسة في `.env`

افتح ملف `.env` وقم بتحديث القيم التالية:

```env
# Django Settings
SECRET_KEY=قم-بتوليد-مفتاح-سري-جديد-هنا
DEBUG=False

# Database Settings (PostgreSQL)
DB_NAME=اسم_قاعدة_البيانات
DB_USER=اسم_المستخدم
DB_PASSWORD=كلمة_مرور_قوية_جداً
DB_HOST=localhost
DB_PORT=5432

# Security Settings (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
RATELIMIT_ENABLE=True

# Allowed Hosts (comma separated)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. توليد SECRET_KEY جديد

استخدم الأمر التالي لتوليد مفتاح سري جديد:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. تأكد من إضافة `.env` إلى `.gitignore`

تأكد من أن ملف `.env` مضاف إلى `.gitignore` لعدم رفعه إلى Git:

```
.env
*.env
```

### 5. إعدادات قاعدة البيانات

#### للإنتاج (PostgreSQL):
تأكد من أن PostgreSQL مثبت ومشغل، ثم قم بإنشاء قاعدة البيانات:

```sql
CREATE DATABASE inventory_db;
CREATE USER your_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO your_user;
```

#### للتطوير (SQLite):
إذا كنت تريد استخدام SQLite للتطوير، قم بتعديل `settings.py`:

```python
# قم بتعليق إعدادات PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         ...
#     }
# }

# وإلغاء تعليق إعدادات SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 6. تشغيل Migrations

```bash
python manage.py migrate
```

### 7. إنشاء مستخدم مسؤول

```bash
python manage.py create_admin --username=admin --password=secure_password
```

### 8. جمع الملفات الثابتة (للإنتاج)

```bash
python manage.py collectstatic
```

---

## 🔐 إعدادات الأمان الإضافية

### 1. HTTPS (للإنتاج فقط)

تأكد من أن خادمك يدعم HTTPS، ثم قم بتفعيل الإعدادات التالية في `.env`:

```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Rate Limiting

النظام يستخدم `django-ratelimit` لحماية من Brute Force Attacks. تأكد من تثبيته:

```bash
pip install django-ratelimit
```

### 3. Firewall

قم بإعداد Firewall لحماية الخادم:

```bash
# مثال على Ubuntu
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 4. النسخ الاحتياطي

قم بإعداد نظام نسخ احتياطي تلقائي:

```bash
# مثال: نسخ احتياطي يومي
0 2 * * * /path/to/backup_script.sh
```

---

## ⚠️ تحذيرات مهمة

1. **لا ترفع ملف `.env` إلى Git أبداً**
2. **غيّر SECRET_KEY في الإنتاج**
3. **استخدم كلمات مرور قوية لقاعدة البيانات**
4. **فعّل DEBUG=False في الإنتاج**
5. **استخدم HTTPS في الإنتاج**
6. **راقب ملفات السجلات بانتظام**

---

## 📊 مراقبة الأمان

راقب الملفات التالية بانتظام:

- `logs/security.log` - محاولات الاختراق
- `logs/errors.log` - الأخطاء
- `logs/inventory.log` - السجل العام

---

## 🆘 في حالة اختراق أمني

1. أوقف الخادم فوراً
2. غيّر جميع كلمات المرور
3. راجع ملفات السجلات
4. قم بفحص قاعدة البيانات
5. أعد تشغيل النظام بعد التأكد من الأمان

---

## ✅ Checklist قبل النشر

- [ ] تم إنشاء ملف `.env` وتحديث القيم
- [ ] تم توليد SECRET_KEY جديد
- [ ] DEBUG=False
- [ ] تم إعداد PostgreSQL
- [ ] تم تشغيل migrations
- [ ] تم إنشاء مستخدم مسؤول
- [ ] تم جمع الملفات الثابتة
- [ ] تم تفعيل HTTPS
- [ ] تم إعداد Firewall
- [ ] تم إعداد النسخ الاحتياطي التلقائي
- [ ] تم اختبار النظام بالكامل

---

**النظام جاهز للنشر الآمن!** 🎉

