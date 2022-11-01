from django.db.models import QuerySet
from import_export import fields, resources
from import_export.fields import Field
from import_export.instance_loaders import CachedInstanceLoader
from import_export.widgets import (
    BooleanWidget,
    CharWidget,
    DecimalWidget,
    ForeignKeyWidget,
    IntegerWidget,
    ManyToManyWidget,
)

from .models import Animal, Brand, Category, Product, ProductOptions, SubCategory, Units


# class ForeignKeyWidgetWithCreation(ForeignKeyWidget):
#     def __init__(self, model, field="pk", create=False, **kwargs):
#         self.model = model
#         self.field = field
#         self.create = create
#         super(ForeignKeyWidgetWithCreation, self).__init__(model, field=field, **kwargs)
#
#     def clean(self, value, **kwargs):
#         if not value:
#             return None
#         if self.create:
#             self.model.objects.get_or_create(**{self.field: value})
#         val = super(ForeignKeyWidgetWithCreation, self).clean(value, **kwargs)
#         return self.model.objects.get(**{self.field: val}) if val else None
#
#
# class ManyToManyWidgetWithCreation(ManyToManyWidget):
#     def __init__(self, model, field="pk", create=False, **kwargs):
#         self.model = model
#         self.field = field
#         self.create = create
#         super(ManyToManyWidgetWithCreation, self).__init__(model, field=field, **kwargs)
#
#     def clean(self, value, **kwargs):
#         if not value:
#             return self.model.objects.none()
#         cleaned_value: QuerySet = super(ManyToManyWidgetWithCreation, self).clean(
#             value, **kwargs
#         )
#         object_list = value.split(self.separator)
#         if len(cleaned_value.all()) == len(object_list):
#             return cleaned_value
#         if self.create:
#             for object_value in object_list:
#                 _instance, _new = self.model.objects.get_or_create(
#                     **{self.field: object_value}
#                 )
#         model_objects = self.model.objects.filter(**{f"{self.field}__in": object_list})
#         return model_objects


class ProductOptionsResource(resources.ModelResource):
    article_number = fields.Field(column_name="Артикул", attribute="article_number")
    weight = fields.Field(
        column_name="Вес",
    )
    volume = fields.Field(
        column_name="Объем",
    )
    length = fields.Field(
        column_name="Длина",
    )
    price = fields.Field(column_name="Цена", attribute="price")
    units = fields.Field(column_name="Ед.изм.", attribute="units1")
    # widget=ForeignKeyWidgetWithCreation(Units, field='unit_name', create=True))
    product = fields.Field(column_name="Номенклатура", attribute="product1")
    stock_balance = fields.Field(column_name="Остаток", attribute="stock_balance")
    brand = fields.Field(column_name="Бренд", attribute="brand")
    animal = fields.Field(column_name="Животное", attribute="animal")
    category = fields.Field(column_name="Категория товаров", attribute="category")
    sub_category = fields.Field(
        column_name="Подкатегория товаров", attribute="sub_category"
    )
    is_active = fields.Field()

    class Meta:
        model = ProductOptions
        fields = (
            "article_number",
            "weight",
            "volume",
            "length",
            "price",
            "unit",
            "product",
            "brand",
            "animal",
            "category",
            "sub_category",
            "stock_balance",
        )
        skip_unchanged = True
        report_skipped = True
        use_transactions = True
        import_id_fields = ("article_number",)
        exclude = ("id",)
        # skip_admin_log = True
        batch_size = 100
        use_bulk = True
        # skip_html_diff = True
        instance_loader_class = CachedInstanceLoader

    def before_import_row(self, row, row_number=None, **kwargs):
        self.brand = row["Бренд"]
        self.animal = row["Животное"]
        self.category = row["Категория товаров"]
        self.sub_category = row["Подкатегория товаров"]
        self.product = row["Номенклатура"]
        # self.units = row.pop('Ед.изм.')
        self.units = row["Ед.изм."]
        self.stock_balance = row["Остаток"]
        # weight = row.pop('Вес')
        # length = row.pop('Длина')
        # volume = row.pop('Объем')
        weight = row["Вес"]
        length = row["Длина"]
        volume = row["Объем"]
        if weight is not None:
            self.size = weight
        elif length is not None:
            self.size = length
        elif volume is not None:
            self.size = volume
        if row["Ед.изм."] == "кг":
            row["Вес"] = 1000
            row["Ед.изм."] = "грамм"
            row["Остаток"] = row["Остаток"] * 1000

    def after_import_instance(self, instance, new, row_number=None, **kwargs):

        if "/" in self.animal:
            list_animal = self.animal.split("/")
            animals_list = []
            categories_list = []
            subcat_list = []
            for new_animal in list_animal:
                animal, created = Animal.objects.get_or_create(
                    name=new_animal.capitalize()
                )
                animals_list.append(animal.id)
                category, created = Category.objects.get_or_create(
                    name=self.category, animal=animal
                )
                categories_list.append(category.id)
                sub_category, created = SubCategory.objects.get_or_create(
                    name=self.sub_category, category=category
                )
                subcat_list.append(sub_category.id)
                brand, created = Brand.objects.get_or_create(name=self.brand)
                product, created = Product.objects.get_or_create(
                    name=self.product,
                    brand=brand,
                )
            product.animal.set(animals_list)
            product.category.set(categories_list)
            product.subcategory.set(subcat_list)
            product.animal_ids = animals_list
            product.category_ids = categories_list
            product.subcategory_ids = subcat_list
        else:
            animal, created = Animal.objects.get_or_create(
                name=self.animal.capitalize()
            )
            category, created = Category.objects.get_or_create(
                name=self.category, animal=animal
            )
            sub_category, created = SubCategory.objects.get_or_create(
                name=self.sub_category, category=category
            )
            brand, created = Brand.objects.get_or_create(name=self.brand)
            product, created = Product.objects.get_or_create(
                name=self.product, brand=brand
            )
            product.animal.set((animal,))
            product.category.set((category,))
            product.subcategory.set((sub_category,))
            product.animal_ids = [animal.id]
            product.category_ids = [category.id]
            product.subcategory_ids = [sub_category.id]
        product.save()
        unit_instance, is_created_unit = Units.objects.get_or_create(
            unit_name=self.units
        )
        if self.stock_balance <= 0:
            instance.is_active = False
        if self.units == "кг":
            unit_for_partial, created_unit = Units.objects.get_or_create(
                unit_name="грамм"
            )
            instance.partial = 1
            instance.units = unit_for_partial
            instance.size = 1000
            instance.stock_balance = self.stock_balance * 1000
        else:
            # unit_for_instance, created_unit = Units.objects.get_or_create(unit_name=self.units)
            # print(unit_instance, 'in else statement')

            instance.units = unit_instance
            instance.size = self.size
        instance.product = product

    def bulk_create(self, using_transactions, dry_run, raise_errors, batch_size=None):
        super().bulk_create(using_transactions, dry_run, raise_errors, batch_size=None)

    def get_bulk_update_fields(self):
        not_bulk_fields = (
            "article_number",
            "weight",
            "length",
            "volume",
            "brand",
            "animal",
            "sub_category",
            "category",
        )
        return [f for f in self.fields if f not in not_bulk_fields]

    def bulk_update(self, using_transactions, dry_run, raise_errors, batch_size=None):
        for instance in self.update_instances:
            if instance.stock_balance <= 0:
                instance.is_active = False
            else:
                instance.is_active = True
        super().bulk_update(using_transactions, dry_run, raise_errors, batch_size=None)