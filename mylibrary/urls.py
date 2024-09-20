from django.contrib import admin
from django.urls import path, include
from mylibrary import settings
from django.conf.urls.static import static
from books import views
from books.views import CategoryListView, BookByCategoryView
from django.views.decorators.cache import cache_page
from django.conf import settings

admin.site.site_header = 'Управление сайтом МОЯ ДОМАШНЯЯ БИБЛИОТЕКА'
admin.site.site_title = 'Администрирование сайта МОЯ ДОМАШНЯЯ БИБЛИОТЕКА'
admin.site.index_title = 'Добро пожаловать в панель управления!'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', cache_page(60 * 15)(views.IndexView.as_view()), name='index'),
    path('books/',include('books.urls')),
    path('users/',include('users.urls', namespace='users')),
    path('<str:slug>/', BookByCategoryView.as_view(), name='book-by-category'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        # другие URL-паттерны
    ] + urlpatterns


handler404 = views.PageNotFoundView.as_view()