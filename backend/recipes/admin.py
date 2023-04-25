from django.contrib import admin

from recipes import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование модели Tag."""

    list_display = ('id', 'name', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование модели Ingredient."""

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ['name']
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Администрирование модели RecipeIngredient."""

    model = models.RecipeIngredient
    min_num = 1
    extra = 1


class RecipeTagInline(admin.TabularInline):
    """Администрирование модели RecipeTag."""

    model = models.RecipeTag
    min_num = 1
    extra = 0


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование модели Recipe."""

    list_display = ('id', 'name', 'author', 'in_favorite')
    list_filter = ['name', 'author', 'tags']
    inlines = (RecipeIngredientInline, RecipeTagInline)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Администрирование модели Favorite."""

    list_display = ('id', 'user', 'recipe')


@admin.register(models.ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Администрирование модели ShoppingList."""

    list_display = ('id', 'user', 'recipe')
