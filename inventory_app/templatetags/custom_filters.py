from django import template

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    """
    قسمة رقم على آخر
    الاستخدام: {{ value|divide:arg }}
    """
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return value / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='multiply')
def multiply(value, arg):
    """
    ضرب رقم في آخر
    الاستخدام: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

