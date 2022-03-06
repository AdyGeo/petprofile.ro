from django import template
from django.utils.http import urlencode

register = template.Library()

@register.filter(name='new_notif_count')
def new_notif_count(ds):
    return ds.filter(user_has_seen=0).count()
   
@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
