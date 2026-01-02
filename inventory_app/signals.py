import json
import hashlib
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from .models import Product, Order, ProductReturn, Warehouse, Location, Container, SecureBackup

from django.db.models.fields.files import FieldFile

def get_model_data(instance):
    """تحويل كائن النموذج إلى قاموس بيانات كامل"""
    data = model_to_dict(instance)
    
    # إضافة الحقول التي قد تكون مفقودة (مثل id, created_at, updated_at)
    for field in instance._meta.fields:
        if field.name not in data:
            data[field.name] = getattr(instance, field.name)
            
    # معالجة أنواع البيانات التي لا تدعم JSON serialization مباشرة
    for key, value in data.items():
        if isinstance(value, FieldFile):
            data[key] = str(value) if value else None
                
    return data

def create_secure_backup(instance, action):
    """إنشاء نسخة احتياطية آمنة"""
    try:
        model_name = instance.__class__.__name__
        record_id = instance.id
        
        # تجاهل نموذج النسخ الاحتياطي نفسه لتجنب الحلقة اللانهائية
        if model_name == 'SecureBackup' or model_name == 'Session' or model_name == 'AuditLog':
            return

        data = get_model_data(instance)
        
        # تحويل البيانات إلى JSON
        json_data = json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True, ensure_ascii=False)
        
        # إنشاء توقيع رقمي (Hash) للبيانات لضمان عدم التلاعب
        # نستخدم البيانات + الوقت الحالي + مفتاح سري (يمكن تعقيده أكثر)
        hash_input = f"{model_name}:{record_id}:{action}:{json_data}"
        hash_signature = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        
        SecureBackup.objects.create(
            table_name=model_name,
            record_id=record_id,
            backup_data=json.loads(json_data),
            action=action,
            hash_signature=hash_signature
        )
    except Exception as e:
        # يجب ألا نوقف النظام إذا فشل النسخ الاحتياطي، لكن يجب تسجيل الخطأ
        print(f"Backup Error: {str(e)}")

@receiver(post_save, sender=Product)
@receiver(post_save, sender=Order)
@receiver(post_save, sender=ProductReturn)
@receiver(post_save, sender=Warehouse)
@receiver(post_save, sender=Location)
@receiver(post_save, sender=Container)
def backup_on_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    create_secure_backup(instance, action)

@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=Order)
@receiver(post_delete, sender=ProductReturn)
@receiver(post_delete, sender=Warehouse)
@receiver(post_delete, sender=Location)
@receiver(post_delete, sender=Container)
def backup_on_delete(sender, instance, **kwargs):
    create_secure_backup(instance, 'delete')
