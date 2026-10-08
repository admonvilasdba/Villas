from modeltranslation.translator import TranslationOptions, register

from .models import Category, Dish, SubCategory


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(SubCategory)
class SubCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Dish)
class DishTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
