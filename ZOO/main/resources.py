
from import_export import fields, resources, widgets

from import_export.instance_loaders import CachedInstanceLoader
from .models import Animal, Brand, Category, Product, ProductOptions, SubCategory, Units


class ProductOptionsResource(resources.ModelResource):
    article_number = fields.Field(column_name="Артикул", attribute="article_number",
                                  widget=widgets.CharWidget())
    weight = fields.Field(
        column_name="Вес объем длина",
    )
    price = fields.Field(column_name="Цена", attribute="price")
    units = fields.Field(column_name="Ед.изм.", attribute="units1")
    partial = fields.Field(column_name="Ед изм", attribute="is_partial")
    product = fields.Field(column_name="Номенклатура", attribute="product1")
    stock_balance = fields.Field(column_name="Остаток", attribute="stock_balance")
    brand = fields.Field(column_name="Бренд", attribute="brand")
    animal = fields.Field(column_name="Животное", attribute="animal")
    category = fields.Field(column_name="Категория товаров", attribute="category")
    sub_category = fields.Field(
        column_name="Подкатегория товаров", attribute="sub_category"
    )
    size = fields.Field()
    is_active = fields.Field()

    class Meta:
        model = ProductOptions
        fields = (
            "article_number",
            "size",
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
        batch_size = 250
        use_bulk = True
        instance_loader_class = CachedInstanceLoader

    def before_import_row(self, row, row_number=None, **kwargs):
        self.brand = row["Бренд"].strip()
        self.animal = row["Животное"].strip()
        self.category = row["Категория товаров"].strip()
        self.sub_category = row["Подкатегория товаров"].strip()
        self.product = row["Номенклатура"].strip()
        self.partial = row["Ед изм"].strip()
        self.units = row["Ед.изм."]
        self.stock_balance = row["Остаток"]
        weight = row["Вес объем длина"]
        if weight is not None and weight != '':
            self.size = weight
        else:
            self.size = 1
            self.units = self.partial
        if self.partial == "кг":
            self.size = 1000
            self.units = "г"
            self.stock_balance *= 1000

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
                )
            product.brand = brand
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
                name=self.product
            )
            product.brand = brand
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
        if self.partial == "кг":
            unit_for_partial, created_unit = Units.objects.get_or_create(
                unit_name="г"
            )
            instance.partial = 1
            instance.units = unit_for_partial
            instance.size = 1000
            instance.stock_balance = self.stock_balance * 1000
        else:
            instance.units = unit_instance
            instance.size = self.size
        instance.product = product

    def get_bulk_update_fields(self):
        not_bulk_fields = (
            "article_number",
            "weight",
            "partial",
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
