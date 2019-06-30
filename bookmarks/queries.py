from django.contrib.auth.models import User
from django.db.models import Q, Count, Aggregate, CharField

from bookmarks.models import Bookmark


class Concat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s)'

    def __init__(self, expression, distinct=False, **extra):
        super(Concat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            output_field=CharField(),
            **extra)


def query_bookmarks(user: User, query_string: str):

    # Add aggregated tag info to bookmark instances
    query_set = Bookmark.objects \
        .annotate(tags_count=Count('tags')) \
        .annotate(tags_string=Concat('tags__name'))

    # Sanitize query params
    if not query_string:
        query_string = ''

    # Filter for user
    query_set = query_set.filter(owner=user)

    # Split query into keywords
    keywords = query_string.strip().split(' ')
    keywords = [word for word in keywords if word]

    # Filter for each keyword
    for word in keywords:
        query_set = query_set.filter(
            Q(title__contains=word)
            | Q(description__contains=word)
            | Q(website_title__contains=word)
            | Q(website_description__contains=word)
        )

    # Sort by modification date
    query_set = query_set.order_by('-date_modified')

    return query_set
