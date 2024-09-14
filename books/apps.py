from django.apps import AppConfig


class BooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'
    verbose_name = 'Книга'  # имя модели в единственном числе
    verbose_name_plural = 'Книги'  # имя модели во множественном числе