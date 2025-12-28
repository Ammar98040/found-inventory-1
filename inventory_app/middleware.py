"""
Middleware مخصص لمعالجة الأخطاء وتحسين تجربة المستخدم
"""
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('inventory_app')
security_logger = logging.getLogger('inventory_app.security')


class ErrorHandlingMiddleware:
    """
    Middleware لمعالجة الأخطاء وعرض رسائل واضحة للمستخدمين
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """معالجة الاستثناءات وعرض رسائل واضحة"""
        
        # تسجيل الخطأ
        logger.error(f'خطأ في الصفحة {request.path}: {str(exception)}', exc_info=True)
        
        # إذا كان الطلب AJAX، أرجع JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى أو التواصل مع المسؤول.'
            }, status=500)
        
        # في وضع التطوير، أظهر تفاصيل الخطأ ما لم يكن مسار API
        if settings.DEBUG:
            if request.path.startswith('/api/') or request.headers.get('Accept','').find('application/json') != -1:
                return JsonResponse({
                    'success': False,
                    'error': str(exception)
                }, status=500)
            return None  # دع Django يعرض صفحة الخطأ الافتراضية
        
        # في الإنتاج، أظهر صفحة خطأ مخصصة
        return render(request, 'errors/500.html', {
            'error_message': 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.'
        }, status=500)


class UserActivityMiddleware:
    """
    Middleware لتتبع نشاط المستخدمين تلقائياً
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # تحديث آخر نشاط للمستخدم إذا كان مسجل دخول
        if request.user.is_authenticated and hasattr(request.user, 'user_profile'):
            try:
                # تحديث آخر نشاط بدون إنشاء سجل في UserActivityLog
                # (لتجنب ملء قاعدة البيانات بسجلات كثيرة)
                request.user.user_profile.update_activity(
                    ip_address=self.get_client_ip(request)
                )
            except Exception as e:
                # لا توقف الطلب إذا فشل التحديث
                logger.warning(f'فشل تحديث نشاط المستخدم: {str(e)}')
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def get_client_ip(request):
        """الحصول على عنوان IP الحقيقي للعميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Middleware لإضافة headers أمنية إضافية
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # إضافة headers أمنية
        if not settings.DEBUG:
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Content Security Policy
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' data:;"
            )
        
        return response
