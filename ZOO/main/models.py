from functools import reduce
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from imagekit.models import ProcessedImageField
from smart_selects.db_fields import ChainedManyToManyField

from .validators import name_validator, phone_validator


class MyManager(models.Manager):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        results = super(MyManager, self).bulk_create(
            objs, batch_size=None, ignore_conflicts=False
        )
        filter_of_result = set(map(lambda option: option.product, results))
        for result in filter_of_result:
            if result.options.filter(is_active=True).count() < 1:
                result.is_active = False
        Product.objects.bulk_update(filter_of_result, ["is_active"])


class Product(models.Model):
    """Товары магазина"""

    POPULAR_CHOICES = (
        (
            0,
            "Стандартный",
        ),
        (
            1,
            "Популярный",
        ),
        (
            2,
            "Очень популярный",
        ),
    )
    name = models.CharField(
        verbose_name="Название товара",
        max_length=150,
        unique=True,
        blank=False,
        null=False,
    )
    description = RichTextField(
        verbose_name="Описание товара", null=True, blank=True, config_name="default"
    )
    features = RichTextField(
        verbose_name="Ключевые особенности",
        null=True,
        blank=True,
        config_name="default",
    )
    composition = RichTextField(
        verbose_name="Состав", null=True, blank=True, config_name="default"
    )
    additives = RichTextField(
        verbose_name="Пищевые добавки", null=True, blank=True, config_name="default"
    )
    analysis = RichTextField(
        verbose_name="Гарантированный анализ",
        null=True,
        blank=True,
        config_name="default",
    )
    date_added = models.DateTimeField(verbose_name="Дата добавления", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="Активен", default=True, db_index=True)
    animal = models.ManyToManyField(
        "Animal", related_name="products", verbose_name="Тип животного", blank=True
    )
    brand = models.ForeignKey(
        "Brand",
        related_name="products",
        verbose_name="Бренд",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    category = ChainedManyToManyField(
        "Category",
        chained_field="animal",
        chained_model_field="animal",
        # show_all=False,
        auto_choose=True,
        # sort=True,
        related_name="products",
        verbose_name="Категория",
    )
    # on_delete=models.PROTECT)
    subcategory = ChainedManyToManyField(
        "SubCategory",
        chained_field="category",
        chained_model_field="category",
        # show_all=False,
        auto_choose=True,
        # sort=True,
        related_name="products",
        verbose_name="Подкатегория",
    )
    # on_delete=models.PROTECT,)
    popular = models.IntegerField(
        verbose_name="Популярность", choices=POPULAR_CHOICES, default=0
    )
    animal_ids = ArrayField(
        models.BigIntegerField(null=True),
        null=True,
    )
    category_ids = ArrayField(
        models.BigIntegerField(null=True),
        null=True,
    )
    subcategory_ids = ArrayField(
        models.BigIntegerField(null=True),
        null=True,
    )

    class Meta:
        verbose_name = "ПРОДУКТ"
        verbose_name_plural = "ПРОДУКТЫ"

    def __str__(self):
        return self.name

    def product_options(self):
        return self.options.count()

    product_options.short_description = "Доступные фасовки"

    # def save(self, *args, **kwargs):
    # #     # if self.options.filter(is_active=True).count() == 0:
    # #     #     self.is_active = False
    # #     # else:
    # #     #     self.is_active = True
    #     self.animal_ids = self.animal.values_list('id', flat=True)
    #     self.category_ids = self.category.values_list('id', flat=True)
    #     self.subcategory_ids = self.subcategory.values_list('id', flat=True)
    #     super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Изображение товара"""

    product = models.ForeignKey(
        "Product",
        related_name="images",
        verbose_name="Изображение товара",
        on_delete=models.CASCADE,
    )
    image = ProcessedImageField(
        verbose_name="Изображение товара",
        options={"quality": 70},
        null=True,
        blank=True,
        upload_to="photos_products/",
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "ИЗОБРАЖЕНИЕ ТОВАРА"

    def __str__(self):
        return str(self.product.name)


class Units(models.Model):
    """Единицы измерения"""

    unit_name = models.CharField(
        max_length=50,
        verbose_name="Название единиц измерения",
        blank=True,
        null=True,
        help_text="Создайте новую единицу измерения (шт. л. кг. и тд.) если её нету в списке",
    )

    def __str__(self):
        return self.unit_name

    class Meta:
        verbose_name = "Еденица измерения"
        verbose_name_plural = "ЕДИНИЦЫ ИЗМЕРЕНИЯ"

    def count_prod(self):
        return self.prods.count()

    count_prod.short_description = "Количество товаров"


class ProductOptions(models.Model):
    """Доступные фасовки для товара(разные фасовки по весу, объёму и тд. ...)"""

    article_number = models.CharField(
        verbose_name="Артикул товара",
        max_length=200,
        unique=True,
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        "Product",
        related_name="options",
        on_delete=models.CASCADE,
        verbose_name="Название товара",
    )
    partial = models.BooleanField(
        verbose_name="На развес", default=False, db_index=True
    )
    price = models.DecimalField(verbose_name="Цена", max_digits=8, decimal_places=2)
    size = models.IntegerField(verbose_name="Объём упаковки", blank=False, null=False)
    stock_balance = models.DecimalField(
        verbose_name="Остаток на складе", max_digits=8, decimal_places=2
    )
    is_active = models.BooleanField(verbose_name="Активно", default=True, db_index=True)
    date_created = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True, blank=True, null=True
    )
    date_updated = models.DateTimeField(
        verbose_name="Дата обновления", auto_now=True, blank=True, null=True
    )
    units = models.ForeignKey(
        "Units",
        related_name="prods",
        verbose_name="Единица измерения",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    discount_by_product_option = models.ForeignKey(
        "DiscountByProductOption",
        on_delete=models.SET_NULL,
        related_name="options",
        verbose_name="Скидка на вариант товара",
        null=True,
        blank=True,
    )
    objects = MyManager()

    def __str__(self):
        return f"{self.article_number} : {self.product.name} : {self.size}{self.units}"

    class Meta:
        verbose_name = "Вариант фасовки"
        verbose_name_plural = "ВАРИАНТЫ ФАСОВКИ"
        ordering = (
            "partial",
            "size",
        )

    def save(self, *args, **kwargs):
        if self.stock_balance <= 0:
            self.is_active = False
        # if self.partial == False:
        #     super(ProductOptions, self).save(*args, **kwargs)
        if self.partial is True:
            self.size = 1000
            self.units = Units.objects.get(unit_name="грамм")
        super(ProductOptions, self).save(*args, **kwargs)

        if (
            self.product.options.exclude(article_number=self.article_number)
            .filter(is_active=True)
            .count()
            == 0
            and self.is_active is False
        ):
            self.product.is_active = False
        else:
            self.product.is_active = True
        self.product.save()

    def get_animal(self):
        # return 1
        return reduce(lambda x, y: f"{x}/{y}", self.product.animal.all())

    get_animal.short_description = "Животное"


class Animal(models.Model):
    """Доступные типы животных для поиска товаров"""

    name = models.CharField(
        verbose_name="Название животного", max_length=20, unique=True
    )
    image = ProcessedImageField(
        verbose_name="Изображение животного",
        options={"quality": 50},
        null=True,
        blank=True,
        upload_to="photos_animal/",
    )

    class Meta:
        verbose_name = "ЖИВОТНОГО"
        verbose_name_plural = "ЖИВОТНЫЕ"

    def __str__(self):
        return self.name

    def count_prod(self):
        return self.categories.subcategory.products.count()

    count_prod.short_description = "Количество товаров"


class Brand(models.Model):
    """Бренды товаров доступные в магазине"""

    name = models.CharField(verbose_name="Название бренда", max_length=250, unique=True)
    image = ProcessedImageField(
        verbose_name="Изображение бренда",
        options={"quality": 50},
        null=True,
        blank=True,
        upload_to="photos_brand/",
    )

    class Meta:
        verbose_name = "БРЕНД"
        verbose_name_plural = "БРЕНДЫ"

    def __str__(self):
        return self.name

    def count_prod(self):
        return self.products.count()

    count_prod.short_description = "Количество товаров"


class Category(models.Model):
    """Категории товаров"""

    name = models.CharField(
        verbose_name="Название категории", max_length=30, blank=False, null=False
    )
    is_active = models.BooleanField(verbose_name="Активно", default=True)
    animal = models.ForeignKey(
        "Animal", on_delete=models.PROTECT, null=True, related_name="categories"
    )

    class Meta:
        verbose_name = "КАТЕГОРИИ"
        verbose_name_plural = "КАТЕГОРИИ"

    def __str__(self):
        return f"{self.name} <{self.animal.name.upper()}>"

    def count_prod(self):
        return self.products.count()

    count_prod.short_description = "Количество товаров"


class SubCategory(models.Model):
    """Подкатегории товаров"""

    name = models.CharField(verbose_name="Название подкатегории", max_length=255)
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        verbose_name="Название категории",
        related_name="subcategory",
    )
    is_active = models.BooleanField(verbose_name="Активно", default=True)

    def __str__(self):
        return f"{self.name} <{self.category.animal.name.upper()}>"

    class Meta:
        verbose_name = "ПОДКАТЕГОРИЯ"
        verbose_name_plural = "ПОДКАТЕГОРИИ"

    def count_prod(self):
        return self.products.count()

    count_prod.short_description = "Количество товаров"

    def animal(self):
        return self.category.animal.name


class Article(models.Model):
    """Полезные статьи"""

    title = models.CharField(verbose_name="Название статьи", max_length=200)
    animals = models.ForeignKey(
        Animal, verbose_name="Название животного", on_delete=models.PROTECT
    )
    description = RichTextField(verbose_name="Описание статьи", config_name="custom")
    image = ProcessedImageField(
        verbose_name="Изображение бренда",
        options={"quality": 50},
        null=True,
        blank=True,
        upload_to="photos_article/",
    )
    time_read = models.CharField(verbose_name="Время чтения статьи", max_length=50)
    date_added = models.DateField(
        verbose_name="Дата добавления статьи", auto_now_add=True
    )
    is_active = models.BooleanField(verbose_name="Активна", default=True)

    class Meta:
        verbose_name = "Полезная статья"
        verbose_name_plural = "ПОЛЕЗНЫЕ СТАТЬИ"
        ordering = ["-date_added"]

    def __str__(self):
        return self.title

    def body_description(self):
        return f"%s..." % (self.description[:200],)

    body_description.short_description = "Описание статьи"


class Comments(models.Model):
    """Отзыв о магазине"""

    name_author = models.CharField(
        verbose_name="Автор отзыва", max_length=100, validators=[name_validator]
    )
    body_of_comment = models.TextField(verbose_name="Содержание отзыва")
    phone_number = models.CharField(
        verbose_name="Номер телефона",
        max_length=20,
        null=True,
        blank=True,
        validators=[phone_validator],
    )
    name_animal = models.CharField(
        verbose_name="Имя питомца",
        max_length=100,
        null=True,
        blank=True,
        validators=[name_validator],
    )
    date_added = models.DateTimeField(verbose_name="Дата добавления", auto_now_add=True)
    published = models.BooleanField(verbose_name="Опубликовано", default=False)

    class Meta:
        verbose_name = "Отзыв о магазине"
        verbose_name_plural = "ОТЗЫВЫ О МАГАЗИНЕ"
        ordering = ["-date_added"]

    def __str__(self):
        return f"Отзыв от {self.name_author}, номер телефона {self.phone_number}"

    def body_description(self):
        return f"%s..." % (self.body_of_comment[:200],)

    body_description.short_description = "Описание статьи"


class InfoShop(models.Model):
    """Информация о магазине - адрес, телефон, ст.метро и тд."""

    address = models.CharField(
        verbose_name="Адрес магазина", max_length=100, blank=True, null=True
    )
    metro = models.CharField(
        verbose_name="Станция метро", max_length=50, blank=True, null=True
    )
    time_weekdays = models.CharField(
        verbose_name="Время работы (будние)", max_length=50, blank=True, null=True
    )
    time_weekend = models.CharField(
        verbose_name="Время работы (выходные)", max_length=50, blank=True, null=True
    )
    phone_number = models.CharField(
        verbose_name="Номер телефона", max_length=20, blank=True, null=True
    )
    social = models.TextField(
        verbose_name="Социальная сеть",
        help_text="Ссылка на страницу",
        blank=True,
        null=True,
    )
    maps = models.TextField(
        verbose_name="Расположение на карте",
        help_text="Ссылка с яндекс карты (размер 670х374)",
        blank=True,
    )
    photo = ProcessedImageField(
        verbose_name="Фото режима работы",
        options={"quality": 80},
        null=True,
        blank=True,
        upload_to="photos_time/",
    )
    title = models.CharField(
        verbose_name="Заголовок описания", max_length=100, null=True, blank=True
    )
    main_info = models.TextField(verbose_name="Тело описания", null=True, blank=True)
    published = models.BooleanField(verbose_name="Опубликовано", default=True)
    personal_data_politics = RichTextField(
        verbose_name="Политика в отношении обработки персональных данных",
        null=True,
        blank=True,
        config_name="custom",
    )

    class Meta:
        verbose_name = "О магазине"
        verbose_name_plural = "О МАГАЗИНЕ"

    def __str__(self):
        return f"{self.address}, {self.metro}"


class InfoShopMainPage(models.Model):
    """Информация о магазине на главной странице"""

    main_title = RichTextField(
        verbose_name="Главный блок", null=True, config_name="main_page"
    )
    option_one = RichTextField(
        verbose_name="Первый блок", null=True, config_name="main_page"
    )
    option_two = RichTextField(
        verbose_name="Второй блок", null=True, config_name="main_page"
    )
    info_shop = models.OneToOneField(
        "InfoShop",
        related_name="info_main_page",
        verbose_name="Информация на главной странице",
        on_delete=models.CASCADE,
    )
    photo_main_page = ProcessedImageField(
        verbose_name="Фото на главной странице",
        options={"quality": 80},
        null=True,
        blank=True,
        upload_to="photos_main_page/",
    )

    def __str__(self):
        return ""

    class Meta:
        verbose_name = "Информация на главной странице о магазине"


class InfoShopBlock(models.Model):
    """Блок Информации о магазине"""

    info_shop = models.ForeignKey(
        "InfoShop",
        related_name="second_info",
        verbose_name="О магазине",
        on_delete=models.CASCADE,
    )
    info_title = models.CharField(
        verbose_name="Заголовок Блока", max_length=50, blank=True, null=True
    )
    info_text = models.TextField(verbose_name="Описание Блока", blank=True, null=True)

    class Meta:
        verbose_name = "Блок о магазине"
        verbose_name_plural = "БЛОКИ О МАГАЗИНЕ"

    def __str__(self):
        return ""


class Consultation(models.Model):
    """Консультация"""

    customer_name = models.CharField(
        verbose_name="Имя",
        max_length=100,
        blank=True,
        null=True,
        validators=[name_validator],
    )
    phone_number = models.CharField(
        verbose_name="Номер телефона",
        max_length=13,
        unique=True,
        validators=[phone_validator],
    )
    date_added = models.DateTimeField(
        verbose_name="Дата первого обращения", auto_now_add=True
    )
    date_update = models.DateTimeField(
        verbose_name="Дата последнего обращения", auto_now=True, null=True
    )

    class Meta:
        verbose_name = "Консультация"
        verbose_name_plural = "КОНСУЛЬТАЦИЯ"

    def __str__(self):
        return f"Имя: {self.customer_name}, Телефон: {self.phone_number}"


class Customer(models.Model):
    """Покупатели"""

    phone_number = models.CharField(
        verbose_name="Номер телефона",
        max_length=13,
        blank=True,
        null=True,
        unique=True,
        validators=[phone_validator],
    )
    customer_name = models.CharField(
        verbose_name="Имя покупателя",
        max_length=50,
        blank=True,
        null=True,
        validators=[name_validator],
    )
    first_order_date = models.DateTimeField(
        verbose_name="Дата первого заказа", auto_now_add=True
    )
    last_order_date = models.DateTimeField(
        verbose_name="Дата последнего заказа", auto_now=True, null=True
    )

    # TODO: Нужны ли ещё поля для учёта статистики

    class Meta:
        verbose_name = "ПОКУПАТЕЛЬ"
        verbose_name_plural = "ПОКУПАТЕЛИ"
        ordering = ("first_order_date",)

    def __str__(self):
        return f"{self.customer_name}, {self.phone_number}"


class Order(models.Model):
    """Заказы"""

    PAID_CHOICES = (
        (
            1,
            "Да",
        ),
        (
            0,
            "Нет",
        ),
    )
    customer = models.ForeignKey(
        "Customer",
        verbose_name="Покупатель",
        related_name="order",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(
        verbose_name="Время создания заказа", auto_now_add=True
    )
    paid = models.IntegerField(verbose_name="Оплачен", choices=PAID_CHOICES, default=0)
    total_sum = models.DecimalField(
        verbose_name="Сумма Заказа с возможными скидками",
        null=True,
        decimal_places=2,
        max_digits=8,
    )

    class Meta:
        verbose_name = "ЗАКАЗ"
        verbose_name_plural = "ЗАКАЗЫ"
        ordering = ("-created",)

    def __str__(self):
        # return f'Покупатель: {self.customer.customer_name}. Телефон: {self.customer.phone_number}.'
        return ""


class OrderItem(models.Model):
    """Заказанные товары"""

    order = models.ForeignKey(
        "Order", related_name="items", verbose_name="Заказ", on_delete=models.CASCADE
    )
    article_number = models.ForeignKey(
        "ProductOptions",
        to_field="article_number",
        verbose_name="Товар",
        related_name="order_items",
        on_delete=models.CASCADE,
        null=True,
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return ""

    class Meta:
        verbose_name = "ЗАКАЗАННЫЙ ТОВАР"
        verbose_name_plural = "ЗАКАЗАННЫЕ ТОВАРЫ"


# class Discount(models.Model):
#     title = models.CharField(verbose_name='Название/Описание скидки', max_length=200, null=True, blank=True)
#     is_active = models.BooleanField(verbose_name='Активно', default=False)
#     discount_amount = models.PositiveIntegerField(verbose_name='Процент скидки', default=0,
#                                                   help_text='Процент скидки не должен быть меньше 1% и превышать 90%',
#                                                   validators=[MinValueValidator(1), MaxValueValidator(90)])
#
#     class Meta:
#         abstract = True
#         verbose_name = 'СКИДКА НА ТОВАР'
#         verbose_name_plural = 'СКИДКИ НА ТОВАРЫ'
#
#     def __str__(self):
#         return f'{self.title}, {self.discount_amount}'


# class DiscountProduct(Discount):
#     """Скидка на Продукт(группу товаров)"""
#     product = models.OneToOneField('Product', related_name='discount_product', verbose_name='Продукты',
#                                    on_delete=models.CASCADE, null=True)
#
#     class Meta:
#         verbose_name = 'СКИДКА НА ТОВАР'
#         verbose_name_plural = 'СКИДКИ НА ТОВАРЫ'
#
#     def __str__(self):
#         return f'{self.title}, {self.product}, {self.discount_amount}%'


class DiscountByProductOption(models.Model):
    """Скидки по варианту фасовки продукта"""

    title = models.CharField(
        verbose_name="Название/Описание скидки", max_length=200, null=True, blank=True
    )
    is_active = models.BooleanField(verbose_name="Активно", default=False)
    discount_amount = models.PositiveIntegerField(
        verbose_name="Процент скидки",
        default=0,
        help_text="Процент скидки не должен быть меньше 1% и превышать 90%",
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )

    def __str__(self):
        return f"{self.title},{self.discount_amount}%"

    class Meta:
        verbose_name = "Скидка на вариант товара"
        verbose_name_plural = "СКИДКИ НА ВАРИАНТЫ ТОВАРОВ"


# class DiscountProductOption(Discount):
#     """Скидка на опцию товара"""
#     product_option = models.OneToOneField('ProductOptions', verbose_name='Вариант Фасовки',
#                                           related_name='discount_option', on_delete=models.CASCADE,
#                                           null=True)
#
#     def __str__(self):
#         return f'{self.title}, {self.product_option}, {self.discount_amount}%'
#
#     class Meta:
#         verbose_name = 'Скидка на фасовку товара'
#         verbose_name_plural = "СКИДКИ НА ВАРИАНТЫ ФАСОВКИ"


class DiscountBySubCategory(models.Model):
    """Скидка на категорию товаров"""

    subcategory = models.OneToOneField(
        "SubCategory",
        related_name="discount_subcategory",
        verbose_name="Подкатегория",
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name="Название/Описание скидки", max_length=200, null=True, blank=True
    )
    is_active = models.BooleanField(verbose_name="Активно", default=False)
    discount_amount = models.PositiveIntegerField(
        verbose_name="Процент скидки",
        default=0,
        help_text="Процент скидки не должен быть меньше 1% и превышать 90%",
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )

    def __str__(self):
        return f"Скидка {self.discount_amount}% на - {self.subcategory.name}"

    class Meta:
        verbose_name = "Скидка на подкатегорию товаров"
        verbose_name_plural = "СКИДКИ НА ПОДКАТЕГОРИИ ТОВАРОВ"


class DiscountByDay(models.Model):
    DAYS_DISCOUNT_CHOICES = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресение"),
    ]
    title = models.TextField(
        verbose_name="Название/Описание скидки", max_length=250, null=True
    )
    is_active = models.BooleanField(verbose_name="Активно", default=False)
    week_days = ArrayField(
        models.IntegerField(choices=DAYS_DISCOUNT_CHOICES, null=True), null=True
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Скидка по дням недели"
        verbose_name_plural = "Скидки по дням недели"


class DiscountByDayOptions(models.Model):
    """Скидки по дням недели"""

    discount_by_day = models.ForeignKey(
        "DiscountByDay", related_name="options", on_delete=models.CASCADE
    )
    min_price_for_discount = models.PositiveIntegerField(
        verbose_name="Сумма покупок, от которой считается скидка"
    )
    discount_amount = models.PositiveIntegerField(
        verbose_name="Процент скидки",
        default=0,
        help_text="Процент скидки не должен быть меньше 1% и превышать 90%",
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )

    def __str__(self):
        return f"Мин. сумма для скидки: {self.min_price_for_discount}, Скидка: {self.discount_amount}%"

    class Meta:
        verbose_name = "Сумма покупок для скидки и размер скидки"
        verbose_name_plural = "СУММЫ ПОКУПОК ДЛЯ СКИДОК И РАЗМЕР СКИДОК"
        ordering = ("-min_price_for_discount",)


class Banner(models.Model):
    """Рекламные Баннеры"""

    title = models.CharField(verbose_name="Описание баннера", max_length=150, null=True)
    color = ColorField(
        verbose_name="Цвет фона баннера",
        help_text="Выберите цвет для фона баннера",
        default="#30FFE9",
    )
    image = ProcessedImageField(
        verbose_name="Изображение",
        help_text="Для загрузки изображения с фоном баннера, загружайте файлы в формате PNG",
        options={"quality": 50},
        null=True,
        blank=True,
        upload_to="photos_banner/",
    )
    is_active = models.BooleanField(verbose_name="Активно", default=False)
    info_shop = models.ForeignKey(
        "InfoShop", related_name="banners", on_delete=models.CASCADE, null=True
    )

    # default=InfoShop.objects.all().first().id)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Рекламный Баннер"
        verbose_name_plural = "РЕКЛАМНЫЕ БАННЕРЫ"
