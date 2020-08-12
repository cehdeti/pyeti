from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def unique_html_id(context, prefix):
    """
    Given a string, return a string that is guaranteed to be unique across all
    calls to this template tag, suitable for use as an HTML `id` attribute.

    Note that only calls to this template tag will result in unique IDs. This
    tag does not know anything about HTML IDs that exist on the page that were
    generated is some other fashion.
    """
    if 'request' not in context:
        raise Exception('Need a request')

    if not hasattr(context['request'], 'html_ids'):
        context['request'].html_ids = {}

    if prefix not in context['request'].html_ids:
        context['request'].html_ids[prefix] = 0
        return prefix

    context['request'].html_ids[prefix] += 1
    return '%s--%s' % (prefix, context['request'].html_ids[prefix])
