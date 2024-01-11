from django import template

register = template.Library()

@register.filter
def custom_format(value):
    try:
        parts = value.split('.')
        int_part = "{:,}".format(int(parts[0])).replace(",", ".")
        if len(parts) > 1:
            return f"{int_part},{parts[1]}"
        else:
            return int_part
    except ValueError:
        return value
