from django.core.paginator import Paginator
from django.conf import settings


def paginator_obj(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
