from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

class Book(models.Model):
    class Status(models.IntegerChoices):
        UNCHECKED = 0, 'Не прочитано'
        CHECKED = 1, 'Прочитано'

    class Controler(models.IntegerChoices):
        POSTPONE = 0, 'Отложить'
        TOREAD = 1, 'К прочтению'

    id = models.AutoField(primary_key=True, db_column='BookID')
    title = models.CharField(max_length=100, db_column='Название книги', verbose_name='Название')
    author = models.ForeignKey('Author', on_delete=models.CASCADE, db_column='AuthorID', null=True, verbose_name='Автор')
    editor = models.ForeignKey('Editor', on_delete=models.CASCADE, db_column='EditorID', null=True, verbose_name='Издательство')
    year = models.IntegerField(default=0, db_column='Год издания', verbose_name='Год')
    theme = TreeForeignKey('Theme', on_delete=models.PROTECT, related_name='books', null=True, verbose_name='Тематика')
    type = models.ForeignKey('Type', on_delete=models.CASCADE, null=True, db_column='TypeID', verbose_name='Тип книги')
    cover = models.ForeignKey('Cover', on_delete=models.CASCADE, db_column='CoverID',  null=True, verbose_name='Обложка')
    format = models.ForeignKey('Format', on_delete=models.CASCADE, db_column='FormatID', null=True,  verbose_name='Формат')
    seria = models.ForeignKey('Seria', on_delete=models.CASCADE, db_column='SeriaID', null=True, verbose_name='Серия')
    tom = models.IntegerField(default=0, db_column='Номер тома', verbose_name='Номер тома')
    pages = models.IntegerField(default=0, db_column='Количество страниц', verbose_name='Страницы')
    status = models.BooleanField(default=0, choices=(map(lambda x: (bool(x[0]), x[1]), Status.choices)), verbose_name='Прочитано')
    controler = models.BooleanField(default=0, choices=(map(lambda x: (bool(x[0]), x[1]), Controler.choices)), verbose_name='На контроле')
    images_path = models.ImageField(upload_to='books/images', blank=True)
    file_path = models.FileField(upload_to='books/e_books', blank=True)
    review = models.CharField(max_length=100, db_column='Рецензия', verbose_name='Рецензия')
    place = models.ForeignKey('Place', on_delete=models.CASCADE, db_column='PlaceID', null=True, verbose_name='Место хранения')
    tags = models.ManyToManyField('Tag', through='BookTags', related_name='books')

    class Meta:
        db_table = 'Books'  # имя таблицы в базе данных
        verbose_name = 'книга'  # имя модели в единственном числе
        verbose_name_plural = 'книги'  # имя модели во множественном числе

    def __str__(self):
        return f'Книга {self.title}'

    def get_absolute_url(self):
        return f'/books/{self.id}/detail/'


class Tag(models.Model):
    id = models.AutoField(primary_key=True, db_column='TagID')
    name = models.CharField(max_length=100, db_column='Name')

    class Meta:
        db_table = 'Tag'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Тег {self.name}'


class BookTags(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column='TagID')

    class Meta:
        db_table = 'BookTags'
        verbose_name = 'Тег книги'
        verbose_name_plural = 'Теги книг'

        # уникальность пары карточка-тег
        unique_together = ('book', 'tag')

    def __str__(self):
        return f'Тег {self.tag.name} к книге {self.book.title}'


class Favorite(models.Model):
     id = models.AutoField(primary_key=True, db_column='id')
     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='UserID')
     book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')

     class Meta:
         unique_together = ('user', 'book')


class Author(models.Model):
    id = models.AutoField(primary_key=True, db_column='AuthorID')
    sirname = models.CharField(max_length=100, db_column='Фамилия',verbose_name='Фамилия')
    name = models.CharField(max_length=100, db_column='Имя', verbose_name='Имя')
    fathername = models.CharField(max_length=100, db_column='Отчество', verbose_name='Отчество')

    class Meta:
        db_table = 'Author'
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return f'{self.sirname} {self.name} {self.fathername}'

class Editor(models.Model):
    id = models.AutoField(primary_key=True, db_column='EditorID')
    name = models.CharField(max_length=100, db_column='Издательство',verbose_name='Издательство')
    city = models.CharField(max_length=100, db_column='Город',verbose_name='Город')

    class Meta:
        db_table = 'Editor'
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'

    def __str__(self):
        return f'Издательство {self.name}, г. {self.city}'

class Theme(MPTTModel):
    title = models.CharField(max_length=50, unique=True, verbose_name='Тематика')
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name='Родительская категория')
    slug = models.SlugField()

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        unique_together = [['parent', 'slug']]
        verbose_name = 'Тематика'
        verbose_name_plural = 'Тематика'

    def get_absolute_url(self):
        return reverse('book-by-category', args=[str(self.slug)])

    def __str__(self):
        return self.title


class Type(models.Model):
    id = models.AutoField(primary_key=True, db_column='TypeID')
    type = models.CharField(max_length=20, db_column='Тип книги',verbose_name='Типы книг')

    class Meta:
        db_table = 'Type'
        verbose_name = 'Тип книги'
        verbose_name_plural = 'Типы книг'

    def __str__(self):
        return f'{self.type}'

class Cover(models.Model):
    id = models.AutoField(primary_key=True, db_column='CoverID')
    cover = models.CharField(max_length=50, db_column='Тип обложки',verbose_name='Тип обложки')

    class Meta:
        db_table = 'Cover'
        verbose_name = 'Тип обложки'
        verbose_name_plural = 'Типы обложек'

    def __str__(self):
        return f'{self.cover}'


class Format(models.Model):
    id = models.AutoField(primary_key=True, db_column='FormatID')
    format = models.CharField(max_length=10, db_column='Формат книги', verbose_name='Форматы книг')

    class Meta:
        db_table = 'Format'
        verbose_name = 'Формат книги'
        verbose_name_plural = 'Форматы книг'

    def __str__(self):
        return f'{self.format}'


class Seria(models.Model):
    id = models.AutoField(primary_key=True, db_column='SeriaID')
    seria = models.CharField(max_length=50, db_column='Серия книг',verbose_name='Серии книг')

    class Meta:
        db_table = 'Seria'
        verbose_name = 'Серия книг'
        verbose_name_plural = 'Серии книг'

    def __str__(self):
        return f'{self.seria}'

class Place(models.Model):
    id = models.AutoField(primary_key=True, db_column='PlaceID')
    place = models.CharField(max_length=50, db_column='Место хранения',verbose_name='Места хранения')

    class Meta:
        db_table = 'Place'
        verbose_name = 'Место хранения'
        verbose_name_plural = 'Места хранения'

    def __str__(self):
        return f'{self.place}'