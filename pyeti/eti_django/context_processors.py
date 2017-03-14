from pyeti.utils import is_truthy


def marquee(request):
    return {
        'marquee': is_truthy(request.GET.get('marquee', False))
    }
