from django import template

register = template.Library()

@register.filter
def map(objects, attribute):
    """
    Extracts the given attribute from each object in a queryset or list.
    Example: {{ categories|map:"name" }}
    """
    result = []
    for obj in objects:
        value = getattr(obj, attribute, None)
        result.append(value)
    return result


@register.filter
def multiply(value, arg):
    """Multiply two numbers in templates"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

def sum(value,arg):
    try:
        return float(value) + float(arg)
    except(ValueError,TypeError):
        return 0