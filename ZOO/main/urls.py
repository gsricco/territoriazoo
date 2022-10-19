from rest_framework.routers import SimpleRouter, DefaultRouter
from django.urls import path
from main.views import (ProductViewSet, BrandViewSet, AnimalViewSet, CategoryViewSet,
                        ArticleViewSet, CommentsView, InfoShopView, OrderViewSet,
                        DiscountByDayViewSet,)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='products')
router.register(r'brands', BrandViewSet, basename='brands')
router.register(r'animals', AnimalViewSet, basename='animals')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'comments', CommentsView, basename='comments')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'shop-info', InfoShopView, basename='shop_info')
router.register(r'discounts', DiscountByDayViewSet, basename='discounts')
urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls
