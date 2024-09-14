from django.urls import path
from . import views
from books.views import CategoryListView, BookByCategoryView

urlpatterns = [
    path('catalog/', views.CatalogView.as_view(), name = 'catalog'),
    path('category_list/', CategoryListView.as_view(), name = 'category_list'),
    path('category_list/<str:slug>/', BookByCategoryView.as_view(), name='book-by-category'),
    path('tags/<int:tag_id>/', views.get_books_by_tag, name='get_books_by_tag'),
    path('<int:pk>/detail/', views.BookDetailView.as_view(), name='detail_book_by_id'),
    path('<int:pk>/edit/', views.EditBookUpdateView.as_view(), name='edit_book'),
    path('<int:pk>/delete/', views.DeleteBookView.as_view(), name='delete_book'),
    path('series/', views.SeriaView.as_view(), name = 'series'),
    path('reader/', views.get_control, name = 'reader'),
    path('add/', views.AddBookCreateView.as_view(), name='add_book'),
]
