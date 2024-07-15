from django.contrib import admin
from django import forms
from .forms import ProductForm, CategoryForm, GenderForm
from .models import Product, Size, Category, Gender, Order, OrderItem, CartItem, Product_Image, Review, Like

class SizeInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_quantity = 0
        product_inventory = self.instance.inventory if hasattr(self.instance, 'inventory') else 0

        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                quantity = form.cleaned_data.get('quantity', 0)
                total_quantity += quantity

        # Example validation: Total quantity should not exceed product's inventory
        if total_quantity > product_inventory:
            raise forms.ValidationError("Total quantity exceeds the product's inventory ---")



class ProductImageInline(admin.TabularInline):
    model = Product_Image
    extra = 1

class SizeInline(admin.TabularInline):
    model = Size
    extra = 1
    formset = SizeInlineFormSet

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'unit_price', 'inventory')
    list_filter = ('categories', 'genders', 'brand', 'is_deleted')
    search_fields = ('name', 'description', 'brand')
    inlines = [SizeInline, ProductImageInline]
    # readonly_fields = ('total_likes', 'total_dislikes', 'total_reviews')
    form = ProductForm

    # def save_related(self, request, form, formsets, change):
    #     """
    #     This method is overridden to ensure that the Product instance is saved
    #     before any related Size instances.
    #     """
    #     form.instance.save()
    #     super().save_related(request, form, formsets, change)


    # def delete_queryset(self, request, queryset):
    #     queryset.update(is_deleted=True)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class GenderAdmin(admin.ModelAdmin):
    list_display = ('sex',)
    search_fields = ('sex',)

class SizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'quantity')
    search_fields = ('product__name', 'size')

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

    # def product_is_deleted(self, obj):
    #     return obj.product.is_deleted
    #
    # product_is_deleted.admin_order_field = 'product__is_deleted'  # Allows column sorting
    # product_is_deleted.short_description = 'Product has been deleted'
    #
    # def get_queryset(self, request):
    #     return self.model.objects.all()


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Product_Image, ProductImageAdmin)
admin.site.register((Order, OrderItem, CartItem, Review, Like))
