import datetime
from collections import OrderedDict
from decimal import Decimal
from django.db.models import Case, F, Min, OuterRef, Prefetch, Q, Subquery, When
from django.db.models.functions import Greatest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

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
    InfoShop,
    Order,
    Product,
    ProductOptions,
    SubCategory,
)
from .recommendations import Recommend
from .serializers import (
    AnimalSerializer,
    ArticleSerializer,
    BrandSerializer,
    CategorySerializer,
    CommentsCreateSerializer,
    CommentsListSerializer,
    ConsultationSerializer,
    CustomerSerializer,
    DiscountByDaySerializer,
    InfoShopSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductDetailSerializer,
    ProductOptionsSerializer,
    ProductSerializer,
)
from .services import bot_comment, call_back_bot, send_order_bot


class Pagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_size = 10

    def paginate_queryset(self, queryset, request, view=None):
        self.get_count_qs = queryset.count()
        return super(Pagination, self).paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("page_number", self.page.number),
                    (
                        "products_on_page",
                        self.page.end_index() - self.page.start_index() + 1,
                    ),
                    ("total_products", self.get_count_qs),
                    ("total_pages", self.page.paginator.num_pages),
                    ("max_products_on_page", self.get_page_size(self.request)),
                    ("results", data),
                ]
            )
        )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Product.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "options",
                queryset=ProductOptions.objects.filter(is_active=True)
                .select_related("units", "discount_by_product_option")
                .defer("date_created", "date_updated"),
            )
        )
        .prefetch_related(
            Prefetch(
                "subcategory",
                queryset=SubCategory.objects.select_related("discount_subcategory"),
            ),
            "images",
        )
        .annotate(
            discount_by_subcategory=F(
                "subcategory__discount_subcategory__discount_amount"
            )
        )
        .annotate(
            min_price_options=Min(
                "options__price",
            )
        )
        .annotate(min_price_options=Subquery(
            ProductOptions.objects.filter(
                product=OuterRef("pk"))[:1]
            .values("price")
        )
        )
        .annotate(
            first_option_discount=Subquery(
                ProductOptions.objects.filter(
                    product=OuterRef("pk"),
                    is_active=True,
                    discount_by_product_option__is_active=True,
                )[:1]
                .annotate(min_discount=F("discount_by_product_option__discount_amount"))
                .values("min_discount")
            )
        )
        .annotate(
            greatest_discount=Greatest(
                "discount_by_subcategory", "first_option_discount"
            )
        )
        .annotate(
            min_price=Case(
                When(greatest_discount=None, then=F("min_price_options")),
                When(
                    greatest_discount__gte=0,
                    then=F("min_price_options") * (100 - F("greatest_discount")) / 100,
                ),
            )
        )
    )

    serializer_class = ProductSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name", "popular", "date_added", "min_price")
    ordering = ("name",)

    @method_decorator(cache_page(60, key_prefix="PRODUCTS_LIST"))
    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        if len(response.data["results"]) == 0:
            response.status_code = 400
        return response

    def get_queryset(self):
        queryset = self.queryset
        animal = self.request.query_params.get("animal")
        if animal:
            queryset = queryset.filter(animal_ids__overlap=[animal])
        brands = self.request.query_params.getlist("brand")
        if brands:
            brand_list = brands[0].split(",")
            queryset = queryset.filter(brand_id__in=brand_list)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_ids__overlap=[category])
        subcategory = self.request.query_params.getlist("subcategory")
        if subcategory:
            subcategory_list = subcategory[0].split(",")
            queryset = queryset.filter(subcategory_ids__overlap=subcategory_list)
        on_discount = self.request.query_params.get("on_discount")
        if on_discount:
            queryset = queryset.filter(greatest_discount__gt=0)
        return queryset

    def get_object(self):
        self.serializer_class = ProductDetailSerializer
        return super(ProductViewSet, self).get_object()

    @action(methods=["GET"], detail=True)
    def accompanying_goods(self, request, pk=None):
        r = Recommend()
        product_ids = r.suggest_products_for(pk)
        queryset = self.queryset.filter(id__in=product_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer

    @method_decorator(cache_page(60, key_prefix="BRANDS_LIST"))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    def get_queryset(self):
        qs = Brand.objects.all()
        animal = self.request.query_params.get("animal")
        category = self.request.query_params.get("category")
        if animal:
            qs = qs.filter(products__animal_ids__overlap=[animal]).distinct()
            if category:
                qs = qs.filter(products__category_ids__overlap=[category]).distinct()
        return qs


class AnimalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Category.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "subcategory",
                queryset=SubCategory.objects.filter(is_active=True).select_related(
                    "discount_subcategory"
                ),
            )
        )
        .select_related("animal")
    )
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("animal",)

    @method_decorator(cache_page(60, key_prefix="CATEGORY_LIST"))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response


class ProductOptionsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductOptions.objects.filter(is_active=True)
    serializer_class = ProductOptionsSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_active=True).select_related("animals")
    serializer_class = ArticleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("animals",)

    @method_decorator(cache_page(60, key_prefix="ARTICLE_LIST"))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response


class MyPerms(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST" and request.user and request.user.is_authenticated:
            return True
        elif request.method == "GET":
            return True
        else:
            return False


class CommentsView(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Comments.objects.filter(published=True)
    permission_classes = (MyPerms,)
    serializer_class = CommentsListSerializer

    @method_decorator(cache_page(60*2, key_prefix="COMMENTS_LIST"))
    def list(self, request, *args, **kwargs):
        comments = Comments.objects.filter(published=True)
        serializer = CommentsListSerializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CommentsCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            bot_comment(request.data)
            return Response(status=201)
        else:
            return Response(status=401)


class InfoShopView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        InfoShop.objects.all()
        .prefetch_related(
            "second_info",
        )
        .prefetch_related(
            Prefetch("banners", queryset=Banner.objects.filter(is_active=True))
        )
        .select_related(
            "info_main_page",
        )
    )
    serializer_class = InfoShopSerializer

    @method_decorator(cache_page(60*2, key_prefix="SHOP_INFO"))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)


class OrderViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = (
        Order.objects.all()
        .prefetch_related("items", "items__article_number")
        .select_related("customer")
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        items_basket = request.data["orderInfo"]["productsInBasket"]
        customer = {
            "phone_number": request.data["phone_number"],
            "customer_name": request.data["customer_name"],
        }
        # sum_check = basket_counter(items_basket, request.data['discountForBasket'])
        # if sum_check == Decimal(request.data["orderInfo"]["basketCountWithDiscount"]):
        order_items_list = []
        articles_numbers = []
        not_sellable = []
        for item in items_basket:
            articles_numbers.append(item["chosen_option"]["article_number"])
            order_items_list.append(
                {
                    "article_number": item["chosen_option"]["article_number"],
                    "quantity": item["chosen_option"]["quantity"],
                    "stock_balance": item["chosen_option"]["stock_balance"],
                    "price": item["chosen_option"]["price"],
                }
            )
            # if Decimal(item["chosen_option"]["stock_balance"]) < Decimal(item["chosen_option"]["quantity"]):
            #     not_sellable.append(item)
            if (ProductOptions.objects.get(article_number=item["chosen_option"]["article_number"]).stock_balance
                    < Decimal(item["chosen_option"]["quantity"])):
                not_sellable.append(item)
        if not_sellable:
            return Response(not_sellable, status=402)
        try:
            obj_customer = Customer.objects.get(phone_number=customer["phone_number"])
            serializer_customer = CustomerSerializer(obj_customer, data=customer)
            if serializer_customer.is_valid(raise_exception=True):
                serializer_customer.save()
                order_obj = Order.objects.create(
                    customer_id=obj_customer.id,
                    total_sum=request.data["orderInfo"]["basketCountWithDiscount"],
                )
            else:
                return Response("Wrong Customer", status=400)
        except:
            serializer_customer = CustomerSerializer(data=customer)
            if serializer_customer.is_valid():
                instance = serializer_customer.save()
                order_obj = Order.objects.create(
                    customer_id=instance.id,
                    total_sum=request.data["orderInfo"]["basketCountWithDiscount"],
                )
            else:
                return Response("Wrong Customer", status=400)
        # order_items_list = []
        # articles_numbers = []
        # for item in items_basket:
        #     articles_numbers.append(item["chosen_option"]["article_number"])
        #     order_items_list.append(
        #         {
        #             "article_number": item["chosen_option"]["article_number"],
        #             "quantity": item["chosen_option"]["quantity"],
        #             "stock_balance": item["chosen_option"]["stock_balance"],
        #             "price": item["chosen_option"]["price"],
        #         }
        #     )
        # TODO: for updating stock_balance in ProductOption

        po_objects = ProductOptions.objects.filter(article_number__in=articles_numbers)
        # one_more_list = []
        for item in order_items_list:
            obj_to_update = po_objects.get(article_number=item["article_number"])
            obj_to_update.stock_balance = Decimal(item["stock_balance"]) - Decimal(item["quantity"])
            obj_to_update.save()
            # one_more_list.append(obj_to_update)
        # updating = ProductOptions.objects.bulk_update(one_more_list, ["stock_balance"])
        items_order_serializer = OrderItemSerializer(data=order_items_list, many=True)
        if items_order_serializer.is_valid():
            items_order_serializer.save(order_id=order_obj.id)
            r = Recommend()
            r.products_bought(items_basket)
            send_order_bot(
                {
                    "total_with_discount": request.data["orderInfo"][
                        "basketCountWithDiscount"
                    ],
                    "total_no_discount": request.data["orderInfo"]["basketCount"],
                    "items": order_items_list,
                    "customer": customer,
                }
            )
            return Response(status=201)
        else:
            return Response("Wrong Items", status=400)

    @action(methods=["POST"], detail=False, url_path="call_back", name="call_back")
    def call_back(self, request):
        customer = {
            "phone_number": request.data["phone_number"],
            "customer_name": request.data["customer_name"],
        }
        try:
            obj_consultation = Consultation.objects.get(
                phone_number=customer["phone_number"]
            )
            serializer = ConsultationSerializer(obj_consultation, data=customer)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(status=400)
        except:
            serializer = ConsultationSerializer(data=customer)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(status=400)
        call_back_bot(request.data)
        return Response(status=201)


class DiscountByDayViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DiscountByDaySerializer

    def get_queryset(self):
        queryset = (
            DiscountByDay.objects.filter(is_active=True)
            .prefetch_related(
                "options",
            )
            .filter(week_days__contains=[datetime.datetime.now().weekday()])
        )
        return queryset
