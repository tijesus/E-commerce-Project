from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils.text import gettext_lazy as _
from store.models import Product, CartItem, Review, Order, OrderItem, Size
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .paystack import initiate_transaction, verify_transaction
from functools import reduce


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().filter(inventory__gt=0)

        category = self.request.GET.get('category', None)
        gender = self.request.GET.get('gender', None)
        search_query = self.request.GET.get('q', '')


        if category and gender:
            queryset = queryset.filter(categories__name__iexact=category, genders__sex__iexact=gender)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__icontains=search_query)
            )

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['categories'] = Category.objects.all()  # Assuming you have a Category model
        context['search_query'] = self.request.GET.get('q', '')  # Add the search query to the context
        return context
    def get_template_names(self):
        if self.request.htmx and self.request.GET.get('to', None) == 'home':
            return ['partials/home_partial.html']
        if self.request.htmx:
            return ['partials/product_list_partial.html']
        return [self.template_name]

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if self.get_paginate_by(self.object_list) is not None:
                # When paginate_by is specified, we check whether there are any items to paginate.
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list

            if is_empty:
                # Display empty list if it is allowed.
                if not self.get_allow_empty():
                    raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                                  % {'class_name': self.__class__.__name__})
                return self.render_to_response(self.get_context_data())

        context = self.get_context_data()
        return self.render_to_response(context)



class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    # template_name = 'partials/product_detail_partial.html'  # Default template for htmx requests
    success_url = reverse_lazy("product_list")  # Redirect URL for non-htmx requests (optional)

    def get_template_names(self):
        if self.request.htmx:
            return ['partials/product_detail_partial.html']  # Template for htmx requests
        return ['product_detail.html']  # Template for non-htmx requests

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['user_has_reviewed'] = context['has_liked'] = context['has_disliked'] = context['user_has_bought'] = None

        
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = self.object.reviews.filter(user=self.request.user).exists()
            context['has_liked'] = self.object.likes.filter(user=self.request.user, like=True).exists()
            context['has_disliked'] = self.object.likes.filter(user=self.request.user, dislike=True).exists()
            context['user_has_bought'] = Order.objects.filter(user=self.request.user,
                                                              payment_status__iexact="PAID",
                                                              order_items__product=self.object).exists()
            print(context['user_has_bought'])
        context['total_likes'] = self.object.likes.filter(like=True).count()
        context['total_dislikes'] = self.object.likes.filter(dislike=True).count()
        
        return context

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            login_url = reverse('account:login')  + f'?next={self.request.path.replace("add_to_cart/", "")}'
            response = HttpResponse(status=200)
            response['HX-Location'] = login_url
            return response
        product_id = self.kwargs.get('product_id')
        size = request.POST.get('size')

        # if that product is already in the user's cart, just raise its quantity
        # by one
        if CartItem.objects.filter(user=request.user, product_id=product_id, size=size).exists():
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id, size=size)
            # ensure that the quantity does not exceed the product's inventory
            if cart_item.quantity + 1 > cart_item.product.inventory:
                messages.error(request, _("Not enough inventory"))
                return render(request, 'partials/flash_message_partial.html')
            else:
                cart_item.quantity += 1
                cart_item.save(update_fields=['quantity'])
        else:
            CartItem.objects.create(
                product_id=product_id,
                size=size,
                user=request.user
            )
        messages.success(request, _("Added to cart"))
        return render(request, 'partials/flash_message_partial.html')


class ReviewCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        review = request.POST.get('review')
        review = Review.objects.create(
            product_id=product_id,
            review=review,
            user=request.user
        )
        product = Product.objects.get(id=product_id)
        product.save(update_fields=['total_reviews'])
        reviews = Review.objects.filter(product_id=product_id)
        return render(request, 'partials/review_partial.html', {'reviews': reviews, 'product': product})


class ToggleLikeView(View):
    def post(self, request, *args, **kwargs):
        
        if not self.request.user.is_authenticated:
            login_url = reverse('account:login')  + f'?next={self.request.path.replace("toggle_like/", "")}'
            response = HttpResponse(status=200)
            response['HX-Location'] = login_url
            return response
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        
        # check if a record already exists for the user
        if product.likes.filter(user=request.user).exists():
            # if the user has already liked the product, unlike it
            if product.likes.filter(user=request.user, like=True).exists():
                product.likes.filter(user=request.user).update(like=False, dislike=None)
            # if the user has unliked the product, like it
            else:
                product.likes.filter(user=request.user).update(like=True, dislike=None)
        else:
            product.likes.create(user=request.user, like=True, dislike=None)
            
        context = {'total_likes': product.likes.filter(like=True).count(),
                   'total_dislikes': product.likes.filter(dislike=True).count(),
                   'has_liked': product.likes.filter(user=request.user, like=True).exists(),
                   'has_disliked': product.likes.filter(user=request.user, dislike=True).exists(),
                   'product': product}
        print('Toggle like view called')
        return render(request, 'partials/likes_partial.html', context=context)

class ToggleDislikeView(View):
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            login_url = reverse('account:login')  + f'?next={self.request.path.replace("toggle_dislike/", "")}'
            response = HttpResponse(status=200)
            response['HX-Location'] = login_url
            return response
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        
        # check if a record already exists for the user
        if product.likes.filter(user=request.user).exists():
            # if the user has already disliked the product, remove the dislike
            if product.likes.filter(user=request.user, dislike=True).exists():
                product.likes.filter(user=request.user).update(dislike=False, like=None)
            # if the user has removed the dislike, dislike the product
            else:
                product.likes.filter(user=request.user).update(dislike=True, like=None)
        else:
            product.likes.create(user=request.user, dislike=True, like=None)
            
        context = {'total_likes': product.likes.filter(like=True).count(),
                   'total_dislikes': product.likes.filter(dislike=True).count(),
                   'has_liked': product.likes.filter(user=request.user, like=True).exists(),
                   'has_disliked': product.likes.filter(user=request.user, dislike=True).exists(),
                   'product': product}
        return render(request, 'partials/likes_partial.html', context=context)

class CartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')

        cart_item_with_images = []
        total_price = 0

        for cart_item in cart_items:
            # ensure each cart Item doesn't exceed the product's inventory
            if cart_item.quantity > cart_item.product.inventory:
                cart_item.quantity = cart_item.product.inventory
                cart_item.save(update_fields=['quantity'])

        cart_items = CartItem.objects.filter(user=request.user).select_related('product')

        for cart_item in cart_items:

            cart_item_with_images.append({
                'cart_item': cart_item,
                'image': cart_item.product.images.first().image.url
            })
            total_price += cart_item.total_price
        return render(request, 'cart.html', {'cart_items': cart_item_with_images, 'total_price': total_price})
    

class IncreaseQuantityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart_item_id = self.kwargs.get('cart_item_id')
        cart_item = CartItem.objects.get(id=cart_item_id)
        if cart_item.quantity + 1 > cart_item.product.inventory:
            messages.error(request, _("Not enough inventory"))
            return render(request, 'partials/flash_message_partial.html')
        cart_item.quantity += 1
        cart_item.save(update_fields=['quantity'])
        cart_items = CartItem.objects.filter(user=request.user, product__inventory__gt=0)
        
        total_price = 0
        for _cart_item in cart_items:
            total_price += _cart_item.total_price

        updated_cart_item = CartItem.objects.get(id=cart_item_id)
        context = {'total_price': total_price, 'cart_item': updated_cart_item}
        
        return render(request, 'partials/checkout_partial.html', context=context)
        

class DecreaseQuantityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart_item_id = self.kwargs.get('cart_item_id')
        cart_item = CartItem.objects.get(id=cart_item_id)
        if cart_item.quantity - 1 < 1:
            messages.warning(request, _("Minimum quantity is 1"))
            return render(request, 'partials/flash_message_partial.html')
        
        cart_item.quantity -= 1
        cart_item.save(update_fields=['quantity'])
        cart_items = CartItem.objects.filter(user=request.user, product__inventory__gt=0)
        
        total_price = 0
        for _cart_item in cart_items:
            total_price += _cart_item.total_price

        updated_cart_item = CartItem.objects.get(id=cart_item_id)
        context = {'total_price': total_price, 'cart_item': updated_cart_item}
        
        return render(request, 'partials/checkout_partial.html', context=context)


class DeleteCartItemView(LoginRequiredMixin, View):
    def delete(self, request, *args, **kwargs):
        cart_item_id = self.kwargs.get('cart_item_id')
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
        
        total_price = 0
        cart_items = CartItem.objects.filter(user=request.user)
        for _cart_item in cart_items:
            total_price += _cart_item.total_price
        
        return render(request, 'partials/total_price_partial.html', {'total_price': total_price, 'cart_item_id': cart_item_id})

@login_required
def shippingAddressView(request):
    if request.method == 'POST':
        address = request.POST.get('address')

        user_cart_items = CartItem.objects.filter(user=request.user, product__inventory__gt=0)
        total_price = 0

        # check if this user has items in their cart
        if user_cart_items:
            for _cart_item in user_cart_items:
                total_price += _cart_item.total_price
            # create an order with this address
            order = Order.objects.create(user=request.user, total_amount=total_price,
                                         shipping_address=address)
            order_number = order.order_number

            #create order_items for each of the cart_items
            for _cart_item in user_cart_items:
                print(_cart_item.size)
                order.order_items.create(product=_cart_item.product, quantity=_cart_item.quantity,
                                      unit_price=_cart_item.product.unit_price, total_price=_cart_item.total_price,
                                      size=_cart_item.size)

            response = initiate_transaction({
                "email": str(request.user.email),
                "amount": str(total_price * 100),
                "currency": "NGN",
                "callback_url": "http://localhost:8000/store/callback_url",
                "reference": str(order_number)
            })

            if response.status_code == 200:
                return redirect(response.json()["data"]["authorization_url"])
            else:
                return HttpResponse("status code:", response.status_code)


    if request.method == 'GET':
        response = render(request, 'shipping_address_form.html')
        response.headers['Cache-Control'] = 'no-store'
        return response


def update_inventory(cart_item):
    product = cart_item.product
    product.inventory -= cart_item.quantity
    product.save(update_fields=['inventory'])
    return cart_item

def update_sizes(cart_item):
    '''
    update the product's size quantity
    '''
    if cart_item.size:
        size_obj = Size.objects.get(product=cart_item.product, size__iexact=cart_item.size)
        size_obj.quantity -= cart_item.quantity


        if not size_obj.quantity:
            size_obj.delete()
        else:
            new = size_obj.save(update_fields=['quantity'])

    return cart_item

@login_required
def callback(request):
    reference = request.GET.get('reference')
    response = verify_transaction(reference)
    total_price = reduce(lambda acc, cart_item: acc + cart_item.total_price,
                         CartItem.objects.filter(user=request.user, product__inventory__gt=0), 0)

    if (response.status_code == 200) and (total_price * 100 == response.json()['data']['amount']):

        # reduce each product's inventory accordingly and the product's size quantity
        list(map(update_inventory, CartItem.objects.filter(user=request.user)))
        list(map(update_sizes, CartItem.objects.filter(user=request.user)))

        # clear this user's cart
        CartItem.objects.filter(user=request.user).delete()
        # TODO send an email to the user and admin concerning the payment
        # set the user's payment status to paid
        Order.objects.filter(order_number=reference).update(payment_status='PAID')
        messages.success(request, _("Payment successful!"))
        return redirect(reverse('store:product-list'))
    else:
        # the payment was unsuccessful
        Order.objects.filter(order_number=reference).delete()
        messages.error(request, "Something went wrong")
        return redirect(reverse('store:shipping-address'))

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items.filter(product__inventory=0).exists():
        messages.warning(request, _("Some products are out of stock!"))
        return render(request, 'partials/flash_message_partial.html')
    if cart_items.exists():
        response = HttpResponse()
        if request.htmx:
            response.headers['HX-Redirect'] = reverse('store:shipping-address')
            return response

    return HttpResponse()


class OrderListView(LoginRequiredMixin, ListView):
    model = OrderItem
    paginate_by = 5
    context_object_name = 'order_items'


    def get_template_names(self):
        if self.request.htmx:
            return ['partials/order_list_partial.html']  # Template for htmx requests
        return ['orders_list.html']  # Template for non-htmx requests

    def get_queryset(self):
        orders = OrderItem.objects.filter(order__user=self.request.user, order__payment_status='PAID')

        return orders
