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
]