from django.contrib import admin

from recipes import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс администрирования модели Tag."""

    list_display = ('id', 'name', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс администрирования модели Ingredient."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ['name']
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Класс администрирования модели RecipeIngredient на странице Recipe."""

    model = models.RecipeIngredient
    min_num = 1
    extra = 1


class RecipeTagInline(admin.TabularInline):
    """Класс администрирования модели RecipeTag на странице Recipe."""

    model = models.RecipeTag
    min_num = 1
    extra = 0


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс администрирования модели Recipe."""

    list_display = ('id', 'name', 'author', 'in_favorite')
    list_filter = ['name', 'author', 'tags']
    inlines = (RecipeIngredientInline,)
    inlines = (RecipeIngredientInline, RecipeTagInline)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс администрирования модели Favorite."""

    list_display = ('id', 'user', 'recipe')


@admin.register(models.ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Класс администрирования модели ShoppingList."""

    list_display = ('id', 'user', 'recipe')
