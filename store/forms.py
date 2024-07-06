from django import forms
from store.models import (Product, Size, Gender,
                          Category, Product_Image, CartItem,
                          Order, OrderItem)


class ProductForm(forms.ModelForm):
    """
    Product Form Class
    """
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
            "genders": forms.CheckboxSelectMultiple(),
        }


class SizeForm(forms.ModelForm):
    """
    Size Form Class
    """
    class Meta:
        model = Size
        fields = '__all__'

class GenderForm(forms.ModelForm):
    """
    Gender Form Class
    """
    class Meta:
        model = Gender
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    """
    Category Form Class
    """
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageForm(forms.ModelForm):
    """
    Product Image Form Class
    """
    class Meta:
        model = Product_Image
        fields = '__all__'

class CartItemForm(forms.ModelForm):
    """
    CartItem Form Class
    """
    class Meta:
        fields = "__all__"
        model = CartItem

class OrderForm(forms.ModelForm):
    """
    Order Form Class
    """
    class Meta:
        fields = "__all__"
        model = Order

class OrderItemForm(forms.ModelForm):
    """
    Order Item Form Class
    """
    class Meta:
        fields = "__all__"
        model = OrderItem