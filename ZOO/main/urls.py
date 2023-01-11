from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (
    AnimalViewSet,
    ArticleViewSet,
    BrandViewSet,
    CategoryViewSet,
    CommentsView,
    DiscountByDayViewSet,
    InfoShopView,
    OrderViewSet,
    ProductViewSet,
)

router = SimpleRouter()

router.register(r"products", ProductViewSet, basename="products")
router.register(r"brands", BrandViewSet, basename="brands")
router.register(r"animals", AnimalViewSet, basename="animals")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"articles", ArticleViewSet, basename="articles")
router.register(r"comments", CommentsView, basename="comments")
router.register(r"order", OrderViewSet, basename="order")
router.register(r"shop-info", InfoShopView, basename="shop_info")
router.register(r"discounts", DiscountByDayViewSet, basename="discounts")
urlpatterns = []
urlpatterns += router.urls
