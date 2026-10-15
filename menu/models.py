from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField('nombre', max_length=120)
    slug = models.SlugField('slug', max_length=140, unique=True, blank=True)
    order = models.PositiveIntegerField('orden', default=0)
    is_active = models.BooleanField('activa', default=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class SubCategory(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='categoría',
    )
    name = models.CharField('nombre', max_length=120)
    slug = models.SlugField('slug', max_length=140, blank=True)
    order = models.PositiveIntegerField('orden', default=0)
    is_active = models.BooleanField('activa', default=True)

    class Meta:
        verbose_name = 'subcategoría'
        verbose_name_plural = 'subcategorías'
        ordering = ('order', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('category', 'slug'),
                name='unique_subcategory_slug_per_category',
            ),
        ]

    def __str__(self):
        return f'{self.category.name} · {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Dish(TimeStampedModel):
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name='subcategoría',
    )
    name = models.CharField('nombre', max_length=160)
    description = models.TextField('descripción', blank=True)
    price = models.DecimalField(
        'precio',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    prep_time_minutes = models.PositiveIntegerField(
        'tiempo de preparación (min)',
        null=True,
        blank=True,
    )
    image = models.ImageField(
        'imagen',
        upload_to='dishes/',
        max_length=255,
        blank=True,
        null=True,
    )
    is_available = models.BooleanField('disponible', default=True)
    order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'platillo'
        verbose_name_plural = 'platillos'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    @property
    def prep_time_display(self):
        if not self.prep_time_minutes:
            return ''
        return f'{self.prep_time_minutes} min'
