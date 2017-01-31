from rest_framework.routers import SimpleRouter, Route, DynamicDetailRoute
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url


class SingularResourceRouter(SimpleRouter):
    """
    Provides a Django REST Framework router that allows you to use viewsets for
    single objects with a singular path.

    For example:

        ```
        from pyeti.eti_django.rest_framework.routers import SingularResourceRouter


        class CurrentUserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
            ...

            def get_object(self):
                return self.request.user

            ...


        router = SingularResourceRouter()
        router.register(r'me', CurrentUserViewSet, base_name='user')
        ```
    """
    include_format_suffixes = True

    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'create',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        raise NotImplementedError(
            """Singular routers do not have a lookup regex. Are you sure you
            don't want to use the standard DefaultRouter?"""
        )

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        urls = []

        for prefix, viewset, basename in self.registry:
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    trailing_slash=self.trailing_slash
                )
                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                urls.append(url(regex, view, name=name))

        if self.include_format_suffixes:
            urls = format_suffix_patterns(urls)

        return urls
