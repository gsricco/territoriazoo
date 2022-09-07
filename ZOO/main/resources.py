from django.db.models import QuerySet
from import_export import resources, fields
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget, CharWidget, DecimalWidget, IntegerWidget, \
    BooleanWidget
from .models import Product, Animal, Category, Brand, ProductOptions, Units


class ForeignKeyWidgetWithCreation(ForeignKeyWidget):
    def __init__(self, model, field="pk", create=False, **kwargs):
        self.model = model
        self.field = field
        self.create = create
        super(ForeignKeyWidgetWithCreation, self).__init__(model, field=field, **kwargs)

    def clean(self, value, **kwargs):
        if not value:
            return None
        if self.create:
            self.model.objects.get_or_create(**{self.field: value})
        val = super(ForeignKeyWidgetWithCreation, self).clean(value, **kwargs)
        return self.model.objects.get(**{self.field: val}) if val else None


class ManyToManyWidgetWithCreation(ManyToManyWidget):
    def __init__(self, model, field="pk", create=False, **kwargs):
        self.model = model
        self.field = field
        self.create = create
        super(ManyToManyWidgetWithCreation, self).__init__(model, field=field, **kwargs)

    def clean(self, value, **kwargs):
        if not value:
            return self.model.objects.none()
        cleaned_value: QuerySet = super(ManyToManyWidgetWithCreation, self).clean(value, **kwargs)
        object_list = value.split(self.separator)
        if len(cleaned_value.all()) == len(object_list):
            return cleaned_value
        if self.create:
            for object_value in object_list:
                _instance, _new = self.model.objects.get_or_create(**{self.field: object_value})
        model_objects = self.model.objects.filter(**{f"{self.field}__in": object_list})
        return model_objects


class ProductOptionsAdminResource(resources.ModelResource):
    article_number = Field(column_name='Артикул', attribute='article_number')
    product = fields.Field(column_name='Название продукта', attribute='product',
                           widget=ForeignKeyWidgetWithCreation(Product, field='name', create=True))
    price = Field(column_name='Цена', attribute='price')
    size = Field(column_name='Объём', attribute='size')
    stock_balance = Field(column_name='Остаток на складе', attribute='stock_balance')
    units = fields.Field(column_name='Единицы измерения', attribute='units',
                         widget=ForeignKeyWidgetWithCreation(Units, field='unit_name', create=True))
    is_active = Field(column_name='Активно', attribute='is_active', default=True)
    partial = Field(column_name='На развес', attribute='partial', default=False)

    class Meta:
        model = ProductOptions
        widgets = {
            'article_number': CharWidget,
            'price': DecimalWidget,
            'size': IntegerWidget,
            'stock_balance': IntegerWidget,
            'is_active': BooleanWidget,
            'partial': BooleanWidget
        }
        fields = ('article_number', 'product', 'price', 'size', 'stock_balance', 'units', 'is_active', 'partial')
        export_order = ('article_number', 'product', 'price', 'size', 'stock_balance', 'units', 'is_active', 'partial')
        import_id_fields = ('article_number',)  # поля для определения идентификатора
        exclude = ('id', 'date_created', 'date_updated',)  # поля для исключения

    def before_import_row(self, row, row_number=None, **kwargs):
        if row['На развес'] == 'True' or row['На развес'] == '1':
            row['Объём'] = '1000'
            row['Единицы измерения'] = 'грамм'


class ProductAdminResource(resources.ModelResource):
    name = Field(column_name='Название товара', attribute='name')
    description = Field(column_name='Описание товара', attribute='description')
    features = Field(column_name='Ключевые особенности', attribute='features')
    composition = Field(column_name='Состав', attribute='composition')
    additives = Field(column_name='Пищевые добавки', attribute='additives')
    analysis = Field(column_name='Гарантированный анализ', attribute='analysis')
    is_active = Field(column_name='Активен', attribute='is_active', default=False)
    animal = fields.Field(column_name='Животные', attribute='animal',
                          widget=ManyToManyWidgetWithCreation(Animal, field='name', separator=', ', create=True))
    brand = fields.Field(column_name='Бренды', attribute='brand',
                         widget=ForeignKeyWidgetWithCreation(Brand, field='name', create=True))
    category = fields.Field(column_name='Категории', attribute='category',
                            widget=ForeignKeyWidgetWithCreation(Category, field='name', create=True))

    class Meta:
        model = Product
        widgets = {
            'name': CharWidget,
            'description': CharWidget,
            'features': CharWidget,
            'composition': CharWidget,
            'additives': CharWidget,
            'analysis': CharWidget,
            'is_active': BooleanWidget,
        }
        fields = (
            'name', 'description', 'features', 'composition', 'additives', 'analysis', 'animal', 'brand', 'category',
            'is_active'
        )
        # порядок экспорта полей
        export_order = (
            'name', 'description', 'features', 'composition', 'additives', 'analysis', 'animal', 'brand', 'category',
            'is_active'
        )
        import_id_fields = ('name',)  # поля для определения идентификатора
        exclude = ('id', 'date_added', 'popular')  # поля для исключения
