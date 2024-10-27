from django.contrib import admin
from .models import Book, Tag, BookTags, Favorite, Author, Editor, Theme, Type, Cover, Format, Seria, Place
from django.contrib.admin import SimpleListFilter
from mptt.admin import MPTTModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author','year', 'pages', 'theme', 'status', 'controler')
    list_display_links = ('pk', 'title',)
    search_fields = ('title',)
    list_filter = ('status',)
    ordering = ('title', )
    list_per_page = 8
    list_editable = ('status', 'theme')

    actions = ['set_checked', 'set_unchecked']

    @admin.action(description='Пометить как прочитанные')
    def set_checked(self, request, queryset):
        updated_count = queryset.update(status=Book.Status.CHECKED)
        self.message_user(request, f'{updated_count} книг было помечено как прочитанные')

    @admin.action(description='Пометить как непрочитанные')
    def set_unchecked(self, request, queryset):
        updated_count = queryset.update(status=Book.Status.UNCHECKED)
        self.message_user(request, f'{updated_count} книг было помечено как непрочитанные', 'warning')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sirname', 'name', 'fathername')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

@admin.register(BookTags)
class BookTagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'book', 'tag')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'book', 'user')

@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'city')

@admin.register(Theme)
class ThemeAdmin(MPTTModelAdmin):
    list_display = ('pk', 'title')

@admin.register(Type)
class Type(admin.ModelAdmin):
    list_display = ('pk', 'type')
@admin.register(Cover)
class Cover(admin.ModelAdmin):
    list_display = ('pk', 'cover')

@admin.register(Format)
class Format(admin.ModelAdmin):
    list_display = ('pk', 'format')

@admin.register(Seria)
class Seria(admin.ModelAdmin):
    list_display = ('pk', 'seria')

@admin.register(Place)
class Place(admin.ModelAdmin):
    list_display = ('pk', 'place')