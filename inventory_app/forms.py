"""
Django Forms for Input Validation and Security
"""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import re
from .models import Product, Location, UserProfile


class LoginForm(forms.Form):
    """نموذج تسجيل الدخول مع التحقق من الأمان"""
    username = forms.CharField(
        label='اسم المستخدم',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم',
            'autocomplete': 'username',
        }),
        required=True
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور',
            'autocomplete': 'current-password',
        }),
        required=True
    )
    
    def clean_username(self):
        """تنظيف وتحديد اسم المستخدم"""
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError('اسم المستخدم مطلوب')
        
        # إزالة أي محاولات XSS أو HTML
        username = strip_tags(username)
        
        # التحقق من الطول
        if len(username) < 3:
            raise ValidationError('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if len(username) > 150:
            raise ValidationError('اسم المستخدم طويل جداً')
        
        # التحقق من الأحرف المسموحة (أحرف، أرقام، _)
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('اسم المستخدم يحتوي على أحرف غير مسموحة')
        
        return username
    
    def clean_password(self):
        """تنظيف كلمة المرور"""
        password = self.cleaned_data.get('password', '')
        if not password:
            raise ValidationError('كلمة المرور مطلوبة')
        
        if len(password) < 8:
            raise ValidationError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        
        return password


class RegisterStaffForm(forms.Form):
    """نموذج إنشاء حساب موظف جديد"""
    username = forms.CharField(
        label='اسم المستخدم',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم',
            'autocomplete': 'username',
        }),
        required=True
    )
    email = forms.EmailField(
        label='البريد الإلكتروني',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'autocomplete': 'email',
        })
    )
    phone = forms.CharField(
        label='رقم الهاتف',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '05xxxxxxxx',
        })
    )
    user_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        initial='staff'
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '8 أحرف على الأقل',
            'autocomplete': 'new-password',
        }),
        required=True
    )
    password_confirm = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور',
            'autocomplete': 'new-password',
        }),
        required=True
    )
    
    def clean_username(self):
        """تنظيف اسم المستخدم"""
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            raise ValidationError('اسم المستخدم مطلوب')
        
        # إزالة HTML/XSS
        username = strip_tags(username)
        
        # التحقق من الطول
        if len(username) < 3:
            raise ValidationError('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if len(username) > 150:
            raise ValidationError('اسم المستخدم طويل جداً')
        
        # التحقق من الأحرف المسموحة
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('اسم المستخدم يحتوي على أحرف غير مسموحة')
        
        # التحقق من عدم التكرار
        if User.objects.filter(username=username).exists():
            raise ValidationError('اسم المستخدم موجود بالفعل')
        
        return username
    
    def clean_email(self):
        """تنظيف البريد الإلكتروني"""
        email = self.cleaned_data.get('email', '').strip()
        
        if email:
            # إزالة HTML/XSS
            email = strip_tags(email)
            
            # التحقق من الطول
            if len(email) > 254:
                raise ValidationError('البريد الإلكتروني طويل جداً')
            
            # التحقق من عدم التكرار
            if User.objects.filter(email=email).exists():
                raise ValidationError('البريد الإلكتروني مستخدم بالفعل')
        
        return email
    
    def clean_phone(self):
        """تنظيف رقم الهاتف"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if phone:
            # إزالة HTML/XSS
            phone = strip_tags(phone)
            
            # إزالة المسافات والشرطات
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            # التحقق من التنسيق (يبدأ بـ 05 و 10 أرقام)
            if not re.match(r'^05\d{8}$', phone):
                raise ValidationError('رقم الهاتف غير صحيح. يجب أن يبدأ بـ 05 ويحتوي 10 أرقام')
        
        return phone
    
    def clean_password(self):
        """تنظيف كلمة المرور"""
        password = self.cleaned_data.get('password', '')
        
        if not password:
            raise ValidationError('كلمة المرور مطلوبة')
        
        if len(password) < 8:
            raise ValidationError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        
        # التحقق من قوة كلمة المرور
        if password.isdigit():
            raise ValidationError('كلمة المرور يجب أن تحتوي على أحرف وأرقام')
        
        return password
    
    def clean(self):
        """التحقق من تطابق كلمات المرور"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError({
                'password_confirm': 'كلمات المرور غير متطابقة'
            })
        
        return cleaned_data


class ProductForm(forms.ModelForm):
    """نموذج المنتج مع التحقق من الأمان"""
    class Meta:
        model = Product
        fields = ['product_number', 'name', 'category', 'price', 'description', 'quantity', 'location']
        labels = {
            'product_number': 'رقم المنتج',
            'name': 'اسم المنتج',
            'category': 'الفئة',
            'price': 'السعر',
            'description': 'الوصف',
            'quantity': 'الكمية',
            'location': 'الموقع',
        }
        widgets = {
            'product_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'BAG-001',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المنتج',
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الفئة',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'وصف المنتج...',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
            'location': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def clean_product_number(self):
        """تنظيف رقم المنتج"""
        product_number = self.cleaned_data.get('product_number', '').strip()
        
        if not product_number:
            raise ValidationError('رقم المنتج مطلوب')
        
        # إزالة HTML/XSS
        product_number = strip_tags(product_number)
        
        # التحقق من الطول
        if len(product_number) > 100:
            raise ValidationError('رقم المنتج طويل جداً')
        
        # التحقق من الأحرف المسموحة
        if not re.match(r'^[\w\-_]+$', product_number):
            raise ValidationError('رقم المنتج يحتوي على أحرف غير مسموحة')
        
        return product_number.upper()
    
    def clean_name(self):
        """تنظيف اسم المنتج"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('اسم المنتج مطلوب')
        
        # إزالة HTML/XSS
        name = strip_tags(name)
        
        # التحقق من الطول
        if len(name) > 200:
            raise ValidationError('اسم المنتج طويل جداً')
        
        return name
    
    def clean_category(self):
        """تنظيف الفئة"""
        category = self.cleaned_data.get('category', '').strip() if self.cleaned_data.get('category') else ''
        
        if category:
            # إزالة HTML/XSS
            category = strip_tags(category)
            
            # التحقق من الطول
            if len(category) > 100:
                raise ValidationError('الفئة طويلة جداً')
        
        return category
    
    def clean_description(self):
        """تنظيف الوصف"""
        description = self.cleaned_data.get('description', '').strip() if self.cleaned_data.get('description') else ''
        
        if description:
            # إزالة HTML tags فقط، نحتفظ بالمسافات
            description = strip_tags(description)
            
            # التحقق من الطول
            if len(description) > 5000:
                raise ValidationError('الوصف طويل جداً')
        
        return description
    
    def clean_quantity(self):
        """تنظيف الكمية"""
        quantity = self.cleaned_data.get('quantity', 0)
        
        if quantity < 0:
            raise ValidationError('الكمية لا يمكن أن تكون سالبة')
        
        if quantity > 999999:
            raise ValidationError('الكمية كبيرة جداً')
        
        return quantity


class EditStaffForm(forms.Form):
    """نموذج تعديل بيانات الموظف"""
    username = forms.CharField(
        label='اسم المستخدم',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='البريد الإلكتروني',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='رقم الهاتف',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    user_type = forms.ChoiceField(
        label='نوع المستخدم',
        choices=UserProfile.USER_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='كلمة المرور الجديدة (اتركه فارغاً للحفاظ على كلمة المرور الحالية)',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        })
    )
    notes = forms.CharField(
        label='ملاحظات',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
        })
    )
    
    def clean_username(self):
        """تنظيف اسم المستخدم"""
        username = self.cleaned_data.get('username', '').strip()
        username = strip_tags(username)
        
        if len(username) < 3:
            raise ValidationError('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('اسم المستخدم يحتوي على أحرف غير مسموحة')
        
        return username
    
    def clean_phone(self):
        """تنظيف رقم الهاتف"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if phone:
            phone = strip_tags(phone)
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            if not re.match(r'^05\d{8}$', phone):
                raise ValidationError('رقم الهاتف غير صحيح')
        
        return phone
    
    def clean_password(self):
        """تنظيف كلمة المرور"""
        password = self.cleaned_data.get('password', '').strip()
        
        if password:
            if len(password) < 8:
                raise ValidationError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
            
            if password.isdigit():
                raise ValidationError('كلمة المرور يجب أن تحتوي على أحرف وأرقام')
        
        return password if password else None

