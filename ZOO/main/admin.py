from django.contrib import admin
from django.db import models
from django import forms
from django.forms import TextInput, ModelForm
from django.shortcuts import render
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from .models import (Product, Brand, Animal, Category, ProductOptions, ProductImage, Article, Comments, InfoShop,
                     Consultation, Customer, Order, OrderItem, InfoShopBlock, Units,
                     DiscountProduct, DiscountByCategory, DiscountProductOption, DiscountByDay, DiscountByDayOptions,
                     InfoShopMainPage, Banner)
from .resources import ProductOptionsAdminResource, ProductAdminResource


admin.site.site_header = "Территория ZOO"  # Надпись в админке сайта
admin.site.site_title = "Территория ZOO"
admin.site.index_title = ""


class ProductImageInline(admin.TabularInline):
    """Изображение товара"""
    model = ProductImage
    extra = 2
    readonly_fields = 'preview',

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="100" height="100">')

    preview.short_description = 'Превью изображения'


@admin.register(ProductOptions)
class ProductOptionsAdmin(ImportExportModelAdmin):
    """Опции продукта"""
    list_display = 'article_number', 'product', 'price', 'stock_balance', 'size', 'units', 'is_active', 'partial'
    list_filter = (
        'is_active', 'partial', 'units',
        'price',
        'size',
        'stock_balance',
    )
    search_fields = 'article_number', 'stock_balance', 'price'
    list_editable = 'price', 'size', 'stock_balance', 'units', 'partial', 'is_active'
    resource_class = ProductOptionsAdminResource
    change_list_template = "admin/model_change_list_product_options.html"
    list_per_page = 20


class ProductOptionsInline(admin.TabularInline):
    """Опции продукта"""
    model = ProductOptions
    extra = 1


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    """Товары магазина"""
    formfield_overrides = {models.CharField: {'widget': TextInput(attrs={'size': '90'})}}
    fieldsets = (
        ('ОСНОВНЫЕ ДАННЫЕ', {'fields': ('name', 'brand', 'animal', 'category', 'popular',)}),
        ('ИНФОРМАЦИЯ О ТОВАРЕ', {'fields': ('description', 'features', 'composition', 'additives', 'analysis',),
                                 'classes': ['collapse', ]}),
    )
    list_display = ('name', 'brand', 'category', 'date_added', 'popular', 'is_active', 'product_options',)
    list_editable = ('is_active', 'popular')
    list_filter = ('date_added', 'animal', 'brand', 'category', 'is_active', 'popular',)
    exclude = 'unique_name',
    inlines = [ProductOptionsInline, ProductImageInline]
    resource_class = ProductAdminResource
    change_list_template = "admin/model_change_list_product.html"
    list_per_page = 20


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    """Типы животных"""
    list_display = 'name', 'image_img',
    search_fields = 'name',
    readonly_fields = 'preview',
    list_per_page = 20

    def image_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80">')
        else:
            return 'Нет изображения'

    image_img.short_description = 'Изображение'

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="100" height="100">')

    preview.short_description = 'Превью изображения'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Бренды товаров"""
    list_display = 'name', 'image_img', 'count_prod',
    search_fields = 'name',
    readonly_fields = 'preview',
    list_per_page = 20

    def image_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80">')
        else:
            return 'Нет изображения'

    image_img.short_description = 'Изображение'

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="100" height="100">')

    preview.short_description = 'Превью изображения'


@admin.register(Category)
class Category(admin.ModelAdmin):
    """Категории товара"""
    list_display = 'name', 'is_active', 'count_prod',
    list_editable = 'is_active',


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Полезные статьи"""
    list_display = 'title', 'animals', 'image_img', 'body_description', 'date_added', 'time_read', 'is_active',
    list_editable = 'is_active',
    list_filter = 'date_added', 'animals', 'time_read', 'is_active',
    search_fields = 'title', 'body_description',
    list_per_page = 20
    readonly_fields = 'preview',

    def image_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80">')
        else:
            return 'Нет изображения'

    image_img.short_description = 'Изображение'

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="100" height="100">')

    preview.short_description = 'Превью изображения'


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    """Отзыв о магазине"""
    list_display = ('name_author', 'body_description', 'phone_number', 'date_added', 'published',)
    list_editable = ('published',)
    list_filter = ('date_added', 'published',)
    list_per_page = 20


class InfoShopBlockAdminInline(admin.TabularInline):
    """Блок о магазине"""
    list_display = 'info_title', 'info_text',
    model = InfoShopBlock
    extra = 0
    min_num = 3
    max_num = 3


class InfoShopInfoShopMainPageAdminInline(admin.TabularInline):
    """Блок о магазине"""
    list_display = 'main_title', 'option_one', 'option_two', 'photo_main_page'
    model = InfoShopMainPage
    extra = 0
    min_num = 1
    max_num = 1


@admin.register(InfoShop)
class InfoShopAdmin(admin.ModelAdmin):
    """Информация о магазине"""
    list_display = ('address', 'time_weekdays', 'time_weekend', 'phone_number',)  # 'published',
    list_editable = ('time_weekdays', 'time_weekend', 'phone_number',)  # 'published',
    inlines = (InfoShopInfoShopMainPageAdminInline, InfoShopBlockAdminInline,)

    def add_view(self, request):
        if request.method == "POST":
            mess_1 = 'Доступен только один адрес, измените существующий!'
            if InfoShop.objects.count() >= 1:
                context = {"mess_1": mess_1}
                return render(request, 'admin/error.html', context)
        return super(InfoShopAdmin, self).add_view(request)

    # def has_add_permission(self, request):
    #     return False

    #
    # # def has_change_permission(self, request, obj=None):
    # #     return False
    #
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Консультация"""
    list_display = 'customer_name', 'phone_number', 'date_update', 'date_added',
    list_display_links = 'customer_name',
    search_fields = 'customer_name', 'phone_number',
    list_filter = 'customer_name', 'phone_number', 'date_added', 'date_update',


class OrderInlineAdmin(admin.TabularInline):
    """Заказы"""
    model = Order
    extra = 0
    readonly_fields = 'total_sum',


class OrderItemInlineAdmin(admin.TabularInline):
    """Товар в заказе"""
    model = OrderItem
    extra = 0
    max_num = 0
    readonly_fields = ('article_number', 'quantity',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Покупатель"""
    formfield_overrides = {models.TextField: {'widget': TextInput(attrs={'size': '30'})}}
    list_display = 'customer_name', 'phone_number', 'last_order_date'
    list_display_links = 'customer_name',
    list_filter = 'customer_name', 'phone_number',
    list_per_page = 20
    inlines = [OrderInlineAdmin]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = 'customer', 'total_sum', 'paid', 'created',
    list_display = ('customer', 'total_sum', 'paid', 'created',)
    list_editable = ('paid',)
    readonly_fields = ('customer', 'total_sum', 'created',)
    list_filter = ('customer', 'total_sum', 'paid', 'created',)
    list_per_page = 20
    inlines = [OrderItemInlineAdmin]


@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    list_display = 'unit_name', 'count_prod',


@admin.register(DiscountProduct)
class DiscountProductAdmin(admin.ModelAdmin):
    fields = 'title', 'product', 'discount_amount', 'is_active',
    list_display = 'title', 'product', 'discount_amount', 'is_active',
    list_editable = 'is_active', 'discount_amount',
    list_filter = 'is_active', 'discount_amount',


@admin.register(DiscountByCategory)
class DiscountByCategoryAdmin(admin.ModelAdmin):
    fields = 'title', 'category', 'discount_amount', 'is_active',
    list_display = 'title', 'category', 'discount_amount', 'is_active',
    list_editable = 'is_active', 'discount_amount',
    list_filter = 'is_active', 'discount_amount',


@admin.register(DiscountProductOption)
class DiscountProductOptionAdmin(admin.ModelAdmin):
    fields = 'title', 'product_option', 'discount_amount', 'is_active',
    list_display = 'title', 'product_option', 'discount_amount', 'is_active',
    list_editable = 'is_active', 'discount_amount',
    list_filter = 'is_active', 'discount_amount',


class DiscountByDayOptionsAdminInline(admin.TabularInline):
    """Товар в заказе"""
    model = DiscountByDayOptions
    extra = 1
    min_num = 1
    max_num = 10


class MyForm(ModelForm):
    DAYS_DISCOUNT_CHOICES = (
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресение'),
    )
    week_days = forms.TypedMultipleChoiceField(choices=DAYS_DISCOUNT_CHOICES, coerce=int, label='По каким дням недели')

    class Meta:
        model = DiscountByDay
        fields = 'title', 'is_active', 'week_days'


# @admin.register(WeekDays)
# class WeekDaysAdmin(admin.ModelAdmin):
#     list_display = 'days_discount',
#
#     def add_view(self, request):
#         if request.method == "POST":
#             mess_1 = 'Дней недели не может быть больше 7!'
#             if WeekDays.objects.count() >= 7:
#                 context = {"mess_1": mess_1}
#                 return render(request, 'admin/error.html', context)
#         return super(WeekDaysAdmin, self).add_view(request)


@admin.register(DiscountByDay)
class DiscountByDayAdmin(admin.ModelAdmin):
    """Скидки по дням недели и сумме заказа"""
    list_display = 'title', 'is_active',
    list_editable = 'is_active',
    list_filter = 'title', 'is_active'
    inlines = (DiscountByDayOptionsAdminInline,)
    form = MyForm

    def add_view(self, request):
        if request.method == "POST":
            days_list = request.POST.getlist('week_days')
            conflict_obj = DiscountByDay.objects.filter(week_days__overlap=days_list).prefetch_related('options')
            mess_1 = 'На этот день недели уже существует скидка! Доступтна только одна скидка на один день недели!'
            if conflict_obj:
                context = {"conflict_obj": conflict_obj,
                           "mess_1": mess_1,
                           }
                return render(request, 'admin/error.html', context)
        return super(DiscountByDayAdmin, self).add_view(request)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.POST:
            days_list = request.POST.getlist('week_days')
            conflict_obj = DiscountByDay.objects.filter(week_days__overlap=days_list).exclude(id=object_id)
            mess_1 = 'На этот день недели уже существует скидка! Доступтна только одна скидка на один день недели!'
            if conflict_obj:
                context = {"conflict_obj": conflict_obj,
                           "mess_1": mess_1,
                           }
                return render(request, 'admin/error.html', context)
        return super(DiscountByDayAdmin, self).change_view(request, object_id)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    fields = 'title', 'color', 'image', 'preview', 'is_active',
    list_display = 'title', 'image_img', 'color', 'is_active',
    list_editable = 'color', 'is_active'
    list_filter = 'is_active',
    readonly_fields = 'preview',

    def image_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80">')
        else:
            return 'Нет изображения'

    image_img.short_description = 'Изображение'

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="100" height="100">')

    preview.short_description = 'Превью изображения'

    def add_view(self, request):
        if request.method == "POST":
            mess_1 = 'Одновременно активных Баннеров может быть только 2!'
            if request.POST.get('is_active') == 'on' and Banner.objects.filter(is_active=True).count() > 1:
                context = {"mess_1": mess_1}
                return render(request, 'admin/error.html', context)
        return super(BannerAdmin, self).add_view(request)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.method == "POST":
            if request.POST.get('is_active') is not None:
                mess_1 = 'Одновременно активных Баннеров может быть только 2!'
                if request.POST['is_active'] == 'on' and Banner.objects.filter(is_active=True). \
                        exclude(id=object_id).count() > 1:
                    context = {"mess_1": mess_1}
                    return render(request, 'admin/error.html', context)
            else:
                if Banner.objects.filter(is_active=True).count() < 3:
                    return super(BannerAdmin, self).change_view(request, object_id)
        return super(BannerAdmin, self).change_view(request, object_id)

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST":
            counter = 0
            mess_1 = 'Одновременно активных Баннеров может быть только 2!'
            if request.POST.get('form-TOTAL_FORMS') is not None:
                for i in range(int(request.POST['form-TOTAL_FORMS'])):
                    if request.POST.get(f'form-{i}-is_active') is not None:
                        counter += 1
                if counter > 2:
                    context = {"mess_1": mess_1}
                    return render(request, 'admin/error.html', context)
        return super(BannerAdmin, self).changelist_view(request)
