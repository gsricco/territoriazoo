from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.html import strip_tags
from rest_framework import serializers

from .models import (
    Animal,
    Article,
    Banner,
    Brand,
    Category,
    Comments,
    Consultation,
    Customer,
    DiscountByDay,
    DiscountByDayOptions,
    DiscountByProductOption,
    DiscountBySubCategory,
    InfoShop,
    InfoShopBlock,
    InfoShopMainPage,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductOptions,
    SubCategory,
    Units,
)
from .validators import name_validator, phone_validator


class DiscountByProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountByProductOption
        fields = ("discount_amount",)


class DiscountBySubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountBySubCategory
        fields = ("discount_amount",)


class UnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        exclude = ("id",)


class ProductOptionsSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(default=1)
    discount_by_option = serializers.SerializerMethodField()
    units = UnitsSerializer()

    class Meta:
        model = ProductOptions
        fields = (
            "id",
            "is_active",
            "discount_by_option",
            "article_number",
            "units",
            "quantity",
            "partial",
            "price",
            "size",
            "stock_balance",
        )
        depth = 1

    def get_discount_by_option(self, obj):
        try:
            ser = DiscountByProductOptionSerializer(obj.discount_by_product_option)
            return ser.data["discount_amount"]
        except ObjectDoesNotExist:
            return None


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = (
            "id",
            "product",
        )


class SubCategorySerializer(serializers.ModelSerializer):
    discount_subcategory = DiscountBySubCategorySerializer()

    class Meta:
        model = SubCategory
        fields = (
            "id",
            "name",
            "discount_subcategory",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("discount_subcategory") is not None:
            data["discount_subcategory"] = data["discount_subcategory"][
                "discount_amount"
            ]
        return data


class CategorySerializer(serializers.ModelSerializer):
    subcategory = SubCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "animal",
            "subcategory",
        )


class ProductSerializer(serializers.ModelSerializer):
    options = ProductOptionsSerializer(many=True)
    # chosen_option = serializers.SerializerMethodField()
    discount_by_subcategory = serializers.IntegerField()
    greatest_discount = serializers.IntegerField()
    min_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    min_price_options = serializers.DecimalField(max_digits=8, decimal_places=2)
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "min_price_options",
            "greatest_discount",
            "min_price",
            "discount_by_subcategory",
            "name",
            # "chosen_option",
            "options",
            "images",
        )
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("options"):
            data["chosen_option"] = data.get("options")[0]
            return data


class ProductDetailSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "greatest_discount",
            "discount_by_subcategory",
            "name",
            "brand",
            # "chosen_option",
            "options",
            "images",
            "description",
            "features",
            "composition",
            "additives",
            "analysis",
        )
        depth = 1


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            "id",
            "name",
            "image",
        )


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = (
            "id",
            "name",
            "image",
        )


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"


class CommentsCreateSerializer(serializers.ModelSerializer):
    name_author = serializers.CharField(validators=[name_validator])
    phone_number = serializers.CharField(validators=[phone_validator])
    name_animal = serializers.CharField(validators=[name_validator])

    class Meta:
        model = Comments
        exclude = (
            "date_added",
            "published",
        )


class CommentsListSerializer(serializers.ModelSerializer):
    name_author = serializers.CharField(validators=[name_validator])
    name_animal = serializers.CharField(validators=[name_validator])

    class Meta:
        model = Comments
        exclude = (
            "phone_number",
            "date_added",
            "published",
        )


class InfoShopBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoShopBlock
        fields = (
            "id",
            "info_title",
            "info_text",
        )


class InfoShopMainPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoShopMainPage
        fields = (
            "main_title",
            "option_one",
            "option_two",
            "photo_main_page",
        )


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = (
            "title",
            "color",
            "image",
        )


class InfoShopSerializer(serializers.ModelSerializer):
    info_main_page = InfoShopMainPageSerializer(read_only=True)
    second_info = InfoShopBlockSerializer(read_only=True, many=True)
    description_shop = serializers.SerializerMethodField()
    banners = BannerSerializer(many=True, read_only=True)

    def get_description_shop(self, obj):
        return {"title": obj.title, "main_info": obj.main_info}

    class Meta:
        model = InfoShop
        fields = (
            "info_main_page",
            "address",
            "metro",
            "time_weekdays",
            "time_weekend",
            "phone_number",
            "social",
            "maps",
            "photo",
            "description_shop",
            "second_info",
            "personal_data_politics",
            "banners",
        )


class CustomerSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(validators=[name_validator])
    phone_number = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Customer
        fields = (
            "phone_number",
            "customer_name",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "article_number",
            "quantity",
        )


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True, many=False)
    items = OrderItemSerializer(
        many=True,
    )

    class Meta:
        model = Order
        fields = (
            "customer",
            "paid",
            "items",
        )


class ConsultationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(validators=[name_validator])
    phone_number = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Consultation
        fields = (
            "customer_name",
            "phone_number",
        )


class DiscountByDayOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountByDayOptions
        fields = ("min_price_for_discount", "discount_amount")


class DiscountByDaySerializer(serializers.ModelSerializer):
    options = DiscountByDayOptionsSerializer(many=True)

    class Meta:
        model = DiscountByDay
        fields = (
            "title",
            "options",
        )
