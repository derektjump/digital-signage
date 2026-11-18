"""Template helpers for the Grid kit's pieces in Glow's new look."""
from django import template

from signage import kit

register = template.Library()


@register.simple_tag(takes_context=True)
def fk_run_path(context, n, name=''):
    """{% fk_run_path 4 as d %}: the trail through n tiles, picked by the page's address."""
    request = context.get('request')
    return kit.run_path(n, kit.run_for(getattr(request, 'path', '') or '', name or None))


@register.simple_tag
def fk_figs(*args):
    """{% fk_figs v1 'Label 1' v2 'Label 2' as figs %}: a run's figures in a template."""
    return [(args[i], args[i + 1]) for i in range(0, len(args) - 1, 2)]


@register.filter
def fk_minus(value, other):
    """{{ total|fk_minus:online }}: a difference of two counts (Django's add
    filter cannot subtract a variable, so `add:"-"|add:x` came out blank)."""
    try:
        return int(value) - int(other)
    except (TypeError, ValueError):
        return ''
