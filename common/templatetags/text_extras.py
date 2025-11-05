from django import template

register = template.Library()

@register.filter
def only_shop_name(shop_code):
    """
    eg. BSM-2025 -> BSM
    """
    
    shop_short_name=shop_code.split("-")[0]
    return shop_short_name