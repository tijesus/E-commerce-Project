from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<uuid:product_id>/add_to_cart/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('products/<uuid:product_id>/review/', views.ReviewCreateView.as_view(), name='review'),
    path('products/<uuid:product_id>/toggle_like/', views.ToggleLikeView.as_view(), name='toggle-like'),
    path('products/<uuid:product_id>/toggle_dislike/', views.ToggleDislikeView.as_view(), name='toggle-dislike'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/<uuid:cart_item_id>/increase/', views.IncreaseQuantityView.as_view(), name='increase-cart-item'),
    path('cart/<uuid:cart_item_id>/decrease/', views.DecreaseQuantityView.as_view(), name='decrease-cart-item'),
    path('cart/<uuid:cart_item_id>/delete/', views.DeleteCartItemView.as_view(), name='delete-cart-item'),
    path('cart/shipping_address/', views.shippingAddressView, name='shipping-address'),
    path('callback_url/', views.callback, name='callback'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
]