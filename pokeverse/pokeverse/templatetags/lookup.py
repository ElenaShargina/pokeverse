from django.template.defaulttags import register


@register.filter(name='lookup')
def lookup(value, arg):
    """
    Возвращает элемент из value по ключу arg : value[arg]
    """
    if value:
        return value.get(arg)
    else:
        return None