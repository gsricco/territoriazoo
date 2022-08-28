import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import strip_tags
from rest_framework import serializers
from .models import (Animal, Article, Brand, Category, Comments, InfoShop,
                     Product, ProductOptions, ProductImage, Order, Customer, OrderItem, Units, Consultation,
                     InfoShopBlock, DiscountProductOption, DiscountProduct, DiscountByCategory, DiscountByDay,
                     DiscountByDayOptions, InfoShopMainPage, Banner, )


def phone_validator(phone_number):
    regular = r'(\+375)?(?:33|44|25|29)?([0-9]{7})'
    if re.fullmatch(regular, phone_number):
        return phone_number
    else:
        raise serializers.ValidationError('wrong phone number')


class DiscountProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountProduct
        fields = ('discount_amount',)


class DiscountProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountProductOption
        fields = ('discount_amount',)


class DiscountByCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountByCategory
        fields = ('discount_amount',)


class UnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        exclude = ('id',)


class ProductOptionsSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(default=1)
    discount_by_option = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptions
        fields = ('id', 'is_active', 'discount_by_option', 'article_number', 'units', 'quantity', 'partial', 'price',
                  'size', 'stock_balance',)
        depth = 1

    def get_discount_by_option(self, obj):
        # if hasattr(obj, 'discount_option'):
        #     print(obj.discount_option)
        # else:
        #     print('no such attributes')
        try:
            ser = DiscountProductOptionSerializer(obj.discount_option)
            return ser.data['discount_amount']
        except ObjectDoesNotExist:
            return None


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ('product',)


class CategorySerializer(serializers.ModelSerializer):
    discount_by_category = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'discount_by_category',)


class ProductSerializer(serializers.ModelSerializer):
    options = ProductOptionsSerializer(many=True)
    chosen_option = serializers.SerializerMethodField()
    discount_by_product = serializers.IntegerField()
    discount_by_category = serializers.IntegerField()
    max_discount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'max_discount',
            'discount_by_product',
            'discount_by_category',
            'name',
            # 'animal', 'brand',
            # 'category',
            'chosen_option',
            'options', 'images',
            # 'description', 'features', 'composition', 'additives', 'analysis', 'min_price'
        )
        depth = 1

    def get_max_discount(self, obj):
        list_discounts = []
        if obj.discount_by_category is not None:
            list_discounts.append(obj.discount_by_category)
        if obj.discount_by_product is not None:
            list_discounts.append(obj.discount_by_product)
        if len(list_discounts) > 0:
            return sorted(list_discounts)[-1]
        else:
            return None

    def get_chosen_option(self, obj):
        option_id = obj.options.all().first()
        serializer = ProductOptionsSerializer(option_id)
        return serializer.data

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     # list_discounts = []
    #     discount_by_product = data.pop('discount_by_product')
    #     discount_by_category = data.pop('discount_by_category')
    #     # if discount_by_product is not None:
    #     #     list_discounts.append(discount_by_product)
    #     # if discount_by_category is not None:
    #     #     list_discounts.append(discount_by_category)
    #     # if len(list_discounts) > 0:
    #     #     data['max_discount'] = max(discount_by_category, discount_by_product)
    #     # else:
    #     #     data['max_discount'] = None
    #     data['discounts'] = {'discount_by_product': discount_by_product,
    #                          'discount_by_category': discount_by_category}
    #     # data['description'] = strip_tags(instance.description)
    #     # data['features'] = strip_tags(instance.features)
    #     # data['composition'] = strip_tags(instance.composition)
    #     # data['additives'] = strip_tags(instance.additives)
    #     # data['analysis'] = strip_tags(instance.analysis)
    #     return data


class ProductDetailSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'max_discount', 'discount_by_product', 'discount_by_category',
            'name', 'brand',
            'chosen_option',
            'options', 'images',
            'description', 'features', 'composition', 'additives', 'analysis',
        )
        depth = 1


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'image',)


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('id', 'name', 'image',)


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        exclude = ('date_added', 'published',)


class InfoShopBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoShopBlock
        fields = ('id', 'info_title', 'info_text',)


class InfoShopMainPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoShopMainPage
        fields = ('main_title', 'option_one', 'option_two', 'photo_main_page',)


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('title', 'color', 'image',)


class InfoShopSerializer(serializers.ModelSerializer):
    info_main_page = InfoShopMainPageSerializer(read_only=True)
    second_info = InfoShopBlockSerializer(read_only=True, many=True)
    description_shop = serializers.SerializerMethodField()
    banners = BannerSerializer(many=True, read_only=True)

    def get_description_shop(self, obj):
        return {"title": obj.title, "main_info": obj.main_info}

    class Meta:
        model = InfoShop
        fields = ('info_main_page', 'address', 'metro', 'time_weekdays', 'time_weekend', 'phone_number', 'social',
                  'maps', 'photo', 'description_shop', 'second_info', 'personal_data_politics', 'banners',)


class CustomerSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Customer
        fields = ('phone_number', 'customer_name',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('article_number', 'quantity',)


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True, many=False)
    items = OrderItemSerializer(many=True, )

    class Meta:
        model = Order
        fields = ('customer', 'paid', 'items',)


class ConsultationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Consultation
        fields = ('customer_name', 'phone_number',)


class DiscountByDayOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountByDayOptions
        fields = ('min_price_for_discount', 'discount_amount')


class DiscountByDaySerializer(serializers.ModelSerializer):
    options = DiscountByDayOptionsSerializer(many=True)

    class Meta:
        model = DiscountByDay
        fields = ('title', 'options',)




