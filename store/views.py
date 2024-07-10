from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils.text import gettext_lazy as _
from store.models import Product, CartItem, Review
from django.urls import reverse
from django.contrib import messages


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()

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
        # Add any additional context variables here if needed
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = self.object.reviews.filter(user=self.request.user).exists()
        context['total_likes'] = self.object.likes.filter(like=True).count()
        context['total_dislikes'] = self.object.likes.filter(dislike=True).count()
        context['has_liked'] = self.object.likes.filter(user=self.request.user, like=True).exists()
        context['has_disliked'] = self.object.likes.filter(user=self.request.user, dislike=True).exists()
        print(context['total_likes'], context['total_dislikes'], '-------------------')
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
        print("Toggle dislike view called")
        return render(request, 'partials/likes_partial.html', context=context)
            