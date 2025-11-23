"""
سكريبت لتصدير قاعدة بيانات PostgreSQL بشكل كامل
ينشئ ملف SQL يمكن استيراده مباشرة في الاستضافة
"""
import os
import sys
import subprocess
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    if sys.stdout:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')

import django
django.setup()

from decouple import config
from datetime import datetime

def export_postgresql_dump():
    """تصدير قاعدة البيانات PostgreSQL بشكل كامل"""
    
    # معلومات قاعدة البيانات من .env
    db_name = config('DB_NAME')
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    # اسم ملف النسخة الاحتياطية
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'inventory_db_backup_{timestamp}.sql'
    
    print("[BACKUP] Starting database export...")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Host: {db_host}:{db_port}")
    print(f"   Backup file: {backup_filename}")
    print()
    
    # البحث عن pg_dump
    pg_dump_paths = [
        r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\12\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe",
    ]
    
    pg_dump_exe = None
    for path in pg_dump_paths:
        if os.path.exists(path):
            pg_dump_exe = path
            break
    
    if not pg_dump_exe:
        # محاولة استخدام psycopg2 مباشرة
        print("[WARNING] pg_dump not found, using alternative method...")
        return export_using_psycopg2(db_name, db_user, db_password, db_host, db_port, backup_filename)
    
    # استخدام pg_dump
    print("[OK] Using pg_dump to export database...")
    
    # إعداد متغير البيئة لكلمة المرور
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    # بناء أمر pg_dump
    # --clean: حذف الكائنات قبل إنشائها
    # --if-exists: استخدام IF EXISTS مع DROP
    # --create: إنشاء قاعدة البيانات
    # --format=plain: صيغة SQL عادية
    # --verbose: عرض التقدم
    cmd = [
        pg_dump_exe,
        '--host', db_host,
        '--port', str(db_port),
        '--username', db_user,
        '--dbname', db_name,
        '--file', backup_filename,
        '--clean',           # حذف الكائنات قبل إنشائها
        '--if-exists',       # استخدام IF EXISTS
        '--create',          # إنشاء قاعدة البيانات
        '--verbose',         # عرض التقدم
        '--no-owner',        # عدم تضمين مالكي الكائنات (مفيد للاستضافة)
        '--no-acl',          # عدم تضمين صلاحيات (مفيد للاستضافة)
        '--format=plain',    # صيغة SQL عادية
    ]
    
    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print(f"✅ تم تصدير قاعدة البيانات بنجاح!")
        print(f"📁 الملف: {backup_filename}")
        
        # عرض حجم الملف
        file_size = os.path.getsize(backup_filename)
        file_size_mb = file_size / (1024 * 1024)
        print(f"📊 حجم الملف: {file_size_mb:.2f} MB")
        
        return backup_filename
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pg_dump error: {e}")
        print("[INFO] Trying alternative method...")
        return export_using_psycopg2(db_name, db_user, db_password, db_host, db_port, backup_filename)
    except FileNotFoundError:
        print(f"[ERROR] pg_dump not found")
        print("[INFO] Trying alternative method...")
        return export_using_psycopg2(db_name, db_user, db_password, db_host, db_port, backup_filename)


def export_using_psycopg2(db_name, db_user, db_password, db_host, db_port, backup_filename):
    """تصدير قاعدة البيانات باستخدام psycopg2 مباشرة"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    print("[OK] Using psycopg2 to export database...")
    
    try:
        # الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        cursor = conn.cursor()
        
        # جمع جميع الجداول
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   عدد الجداول: {len(tables)}")
        
        # بدء كتابة ملف SQL
        with open(backup_filename, 'w', encoding='utf-8') as f:
            # كتابة رأس الملف
            f.write(f"-- PostgreSQL Database Dump\n")
            f.write(f"-- Database: {db_name}\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"--\n\n")
            f.write(f"SET statement_timeout = 0;\n")
            f.write(f"SET lock_timeout = 0;\n")
            f.write(f"SET idle_in_transaction_session_timeout = 0;\n")
            f.write(f"SET client_encoding = 'UTF8';\n")
            f.write(f"SET standard_conforming_strings = on;\n")
            f.write(f"SET check_function_bodies = false;\n")
            f.write(f"SET xmloption = content;\n")
            f.write(f"SET client_min_messages = warning;\n")
            f.write(f"SET row_security = off;\n\n")
            
                # تصدير كل جدول
            for table in tables:
                print(f"   Exporting table: {table}")
                cursor.execute(f"""
                    SELECT * FROM "{table}"
                """)
                
                # الحصول على أسماء الأعمدة
                columns = [desc[0] for desc in cursor.description]
                
                # تصدير البيانات
                rows = cursor.fetchall()
                
                if rows:
                    f.write(f"\n-- Data for table: {table}\n")
                    f.write(f"TRUNCATE TABLE \"{table}\" CASCADE;\n\n")
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            elif isinstance(val, bool):
                                values.append('TRUE' if val else 'FALSE')
                            else:
                                # الهروب من الأحرف الخاصة
                                val_str = str(val).replace("'", "''").replace("\\", "\\\\")
                                values.append(f"'{val_str}'")
                        
                        cols_str = ', '.join([f'"{col}"' for col in columns])
                        vals_str = ', '.join(values)
                        f.write(f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str});\n')
                    f.write("\n")
            
            # تصدير التسلسلات (Sequences)
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public';
            """)
            sequences = [row[0] for row in cursor.fetchall()]
            
            if sequences:
                f.write("\n-- Reset sequences\n")
                for seq in sequences:
                    cursor.execute(f"SELECT last_value FROM {seq};")
                    last_val = cursor.fetchone()[0]
                    f.write(f"SELECT setval('{seq}', {last_val}, true);\n")
        
        cursor.close()
        conn.close()
        
        print(f"[SUCCESS] Database exported successfully!")
        print(f"[FILE] {backup_filename}")
        
        # عرض حجم الملف
        file_size = os.path.getsize(backup_filename)
        file_size_mb = file_size / (1024 * 1024)
        print(f"[SIZE] {file_size_mb:.2f} MB")
        print(f"[TABLES] {len(tables)} tables")
        
        return backup_filename
        
    except Exception as e:
        print(f"[ERROR] Export error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    result = export_postgresql_dump()
    if result:
        print("\n" + "="*60)
        print("[SUCCESS] Backup created successfully!")
        print(f"[FILE] {result}")
        print("[INFO] You can now upload this file to your hosting")
        print("[INFO] Import using: psql -U username -d database_name < " + result)
        print("="*60)
    else:
        print("\n[ERROR] Failed to create backup")
        sys.exit(1)

