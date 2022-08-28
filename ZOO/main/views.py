import datetime
from collections import OrderedDict
from decimal import Decimal
from django.db.models import F, Min, Max, Q, Prefetch, FilteredRelation
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import (Animal, Brand, Category, Product, ProductOptions, Article, Comments, InfoShop, Consultation, Order,
                     Customer, DiscountProductOption, DiscountByDay, Banner)
from .recommendations import Recommend
from .serializers import (AnimalSerializer, BrandSerializer, CategorySerializer,
                          ProductSerializer, ProductOptionsSerializer, ArticleSerializer,
                          InfoShopSerializer, CommentsSerializer, OrderSerializer, CustomerSerializer,
                          OrderItemSerializer, DiscountProductOptionSerializer, ProductDetailSerializer,
                          DiscountByDaySerializer, ConsultationSerializer,)
from .services import send_order_bot, basket_counter, call_back_bot, bot_comment


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        self.get_count_qs = queryset.count()
        return super(Pagination, self).paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page_number', self.page.number),
            ('products_on_page', self.page.end_index() - self.page.start_index() + 1),
            ('total_products', self.get_count_qs),
            ('total_pages', self.page.paginator.num_pages),
            ('max_products_on_page', self.get_page_size(self.request)),
            ('results', data),
        ]))


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True). \
        prefetch_related(Prefetch('options', queryset=ProductOptions.objects.filter(is_active=True))). \
        prefetch_related(Prefetch('options__discount_option',
                                  queryset=DiscountProductOption.objects.filter(is_active=True))). \
        prefetch_related('options__units', 'images', ). \
        select_related('brand', 'category', 'discount_product', ). \
        filter(category__is_active=True). \
        annotate(discount_by_category_true=FilteredRelation('category__discount_category',
                                                            condition=Q(
                                                                category__discount_category__is_active=True)), ). \
        annotate(discount_by_category=F('discount_by_category_true__discount_amount')). \
        annotate(discount_by_product_true=FilteredRelation('discount_product',
                                                           condition=Q(
                                                               discount_product__is_active=True)), ). \
        annotate(discount_by_product=F('discount_by_product_true__discount_amount')). \
        annotate(min_price=Min('options__price', filter=Q(options__partial=False) & Q(options__is_active=True)))

    serializer_class = ProductSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('animal', 'category',)
    search_fields = ('name',)
    ordering_fields = ('name', 'min_price', 'popular', 'date_added',)
    ordering = ('name',)

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        if len(response.data['results']) == 0:
            response.status_code = 400
        return response

    def get_queryset(self):
        queryset = self.queryset
        brands = self.request.query_params.getlist('brand')
        if brands:
            brand_list = brands[0].split(',')
            queryset = queryset.filter(brand_id__in=brand_list)
        return queryset

    # @method_decorator(cache_page(60 * 60))
    def dispatch(self, *args, **kwargs):
        return super(ProductViewSet, self).dispatch(*args, **kwargs)

    def get_object(self):
        self.serializer_class = ProductDetailSerializer
        return super(ProductViewSet, self).get_object()

    @action(methods=['GET'], detail=True)
    def accompanying_goods(self, request, pk=None):
        print(self.pagination_class)
        r = Recommend()
        product_ids = r.suggest_products_for(pk)
        queryset = self.queryset.filter(id__in=product_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class AnimalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer

    # @action(detail=True, methods=['GET'], url_path='popular', name='popular_product_by_pet')
    # def popular_by_pet(self, request, pk=None):
    #     instance_set = Product.objects.filter(animal=pk).order_by('-popular')
    #     if len(instance_set) < 16:
    #         serializer = ProductSerializer(instance_set, many=True)
    #     else:
    #         serializer = ProductSerializer(instance_set[:16], many=True)
    #     return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).\
        annotate(discount_category_true=FilteredRelation('discount_category',
                                                         condition=Q(discount_category__is_active=True))).\
        annotate(discount_by_category=F('discount_category_true__discount_amount'))
    serializer_class = CategorySerializer


class ProductOptionsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductOptions.objects.filter(is_active=True)
    serializer_class = ProductOptionsSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_active=True)
    serializer_class = ArticleSerializer


class CommentsView(mixins.CreateModelMixin, mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Comments.objects.filter(published=True)
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        comments = self.queryset
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = CommentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            bot_comment(request.data)
            return Response(status=201)
        else:
            print(serializer.errors)
            return Response(status=401)


class InfoShopView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = InfoShop.objects.all().prefetch_related('second_info',).\
        prefetch_related(Prefetch('banners', queryset=Banner.objects.filter(is_active=True))).\
        select_related('info_main_page',)
    serializer_class = InfoShopSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Order.objects.all().prefetch_related('items', 'items__article_number').select_related('customer')
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        items_basket = request.data['orderInfo']['productsInBasket']
        customer = {'phone_number': request.data['phone_number'], 'customer_name': request.data['customer_name']}
        sum_check = basket_counter(items_basket, request.data['discountForBasket'])
        if sum_check == Decimal(request.data["orderInfo"]["basketCountWithDiscount"]):
            try:
                obj_customer = Customer.objects.get(phone_number=customer['phone_number'])
                serializer_customer = CustomerSerializer(obj_customer, data=customer)
                if serializer_customer.is_valid(raise_exception=True):
                    serializer_customer.save()
                    order_obj = Order.objects.create(customer_id=obj_customer.id,
                                                     total_sum=request.data["orderInfo"]["basketCountWithDiscount"])
                else:
                    return Response("Wrong Customer", status=400)
            except:
                serializer_customer = CustomerSerializer(data=customer)
                if serializer_customer.is_valid():
                    instance = serializer_customer.save()
                    order_obj = Order.objects.create(customer_id=instance.id,
                                                     total_sum=request.data["orderInfo"]["basketCountWithDiscount"])
                else:
                    return Response("Wrong Customer", status=400)
            order_items_list = []
            # articles_numbers = []
            for item in items_basket:
                # articles_numbers.append(item['chosen_option']['article_number'])
                order_items_list.append({'article_number': item['chosen_option']['article_number'],
                                         'quantity': item['chosen_option']['quantity'],
                                         'stock_balance': item['chosen_option']['stock_balance'],
                                         'price': item['chosen_option']['price']})
            # TODO: for updating stock_balance in ProductOption
            # print(articles_numbers)
            # po_objects = ProductOptions.objects.filter(article_number__in=articles_numbers)
            # print(po_objects)
            # print(order_items_list)
            # one_more_list = []
            # for item in order_items_list:
            #     obj_to_update = po_objects.get(article_number=item['article_number'])
            #     # print(obj_to_update)
            #     obj_to_update.stock_balance = item['stock_balance'] - item['quantity']
            #     one_more_list.append(obj_to_update)
            # updating = ProductOptions.objects.bulk_update(one_more_list, ['stock_balance'])
            items_order_serializer = OrderItemSerializer(data=order_items_list, many=True)
            if items_order_serializer.is_valid():
                items_order_serializer.save(order_id=order_obj.id)
                r = Recommend()
                r.products_bought(items_basket)
                send_order_bot({"total_with_discount": request.data["orderInfo"]["basketCountWithDiscount"],
                                "total_no_discount": request.data["orderInfo"]["basketCount"],
                                'items': order_items_list,
                                'customer': customer})
                return Response(status=201)
            else:
                return Response("Wrong Items", status=400)
        else:
            return Response("Wrong Basket", status=400)

    # TODO: delete this method later
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_path='call_back', name='call_back')
    def call_back(self, request):
        customer = {'phone_number': request.data['phone_number'], 'customer_name': request.data['customer_name']}
        try:
            obj_consultation = Consultation.objects.get(phone_number=customer['phone_number'])
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
    queryset = DiscountByDay.objects.filter(is_active=True). \
                prefetch_related('options', ).\
                filter(week_days__contains=[datetime.datetime.now().weekday()])
    serializer_class = DiscountByDaySerializer
