import uuid
from account.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from .store_managers import productManager, sizeManager, productImageManager
from django.core.validators import MinValueValidator
import datetime
import os



def generate_order_number():
    # generate an order number comprising time
    # in the format '%Y%m%d%H%M%S' and a random 10 character string
    # separated by a colon
    time_portion = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_string = str(uuid.uuid4())[:10]
    return f'{time_portion}_{random_string}'


def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    valid_extensions = ['.jpg', '.jpeg', '.png']  # Define valid extensions
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png')

def validate_file_size(value):
    max_file_size = 2 * 1024 * 1024  # 2 MB
    if value.size > max_file_size:
        raise ValidationError(f"File size should not exceed {max_file_size / (1024 * 1024)} MB")

class Product_Image(models.Model):
    """
    Product Image Model
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    image = models.ImageField(upload_to='product_image/',
                              default='product_image/default.jpg',
                              validators=[validate_image_extension, validate_file_size])
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')

    objects = models.Manager()
    # undeleted = productImageManager.UndeletedProductImageManager()


class Product(models.Model):
    """
    Product Model
    """
    categories = models.ManyToManyField('Category', related_name='products')
    genders = models.ManyToManyField('Gender', related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    inventory = models.PositiveIntegerField(default=1)
    total_likes = models.PositiveIntegerField(default=0)
    total_dislikes = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    unit_price = models.PositiveIntegerField(validators=[MinValueValidator(1000)], default=1000)
    is_deleted = models.BooleanField(default=False)
    brand = models.CharField(max_length=100, default="Generic")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    # undeleted = productManager.UndeletedProductManager()
    objects = models.Manager()

    def has_reviews(self) -> bool:
        """
        checks if the product has reviews
        """
        return self.total_reviews > 0

    def has_sizes(self) -> bool:
        """
        checks if the product has sizes
        """
        return self.sizes.all().exists()

    def get_reviews(self) -> QuerySet:
        """
        returns all the reviews of the product
        """
        return self.reviews.all()

    @property
    def in_stock(self):
        return self.inventory > 0


    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        """
        normalizes the name before saving
        """
        self.name = self.name.lower().capitalize()
        self.description = self.description.lower().capitalize()
        self.brand = self.brand.lower().title()
        super().save(*args, **kwargs)


    class Meta:
        # base_manager_name = "undeleted"
        verbose_name_plural = "Products"
        verbose_name = "Product"
        ordering = [
            'name', 'brand'
            ]




class Size(models.Model):
    """
    Size Model
    """

    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='sizes')
    size = models.CharField(max_length=4)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    # undeleted = sizeManager.UndeletedSizeManager()
    objects = models.Manager()

    def clean(self):
        """
        ensures that a products total quantity
        does not exceed the product's inventory
        """
        # TODO fix the validation error bug

        # if not getattr(self, '_skip_clean', False):
        #     inventory = self.product.inventory
        #     total_quantity = self.product.sizes.aggregate(total=models.Sum('quantity'))['total'] or 0
        #     if not self._state.adding:
        #         total_quantity -= Size.objects.get(id=self.id).quantity
        #     if total_quantity + self.quantity > inventory:
        #         raise ValidationError(
        #             message="The product's quantity exceeds the inventory",
        #             code="quantity_exceeded")

    def __str__(self):
        product = self.product
        return f"{self.quantity} units of size {self.size} for {product} {product.brand}"

    def save(self, *args, **kwargs):
        self.size = self.size.upper()
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ['size', 'product']
        # base_manager_name = "undeleted"


class Category(models.Model):
    """
    Category Model
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower().capitalize()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"


class Gender(models.Model):
    """
    Gender Model
    """
    choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    sex = models.CharField(max_length=20, choices=choices, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.sex


class CartItem(models.Model):
    """
    represents each item in a cart
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    size = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    @property
    def total_price(self):
        """
        returns the total price of a cart item
        """
        return self.product.unit_price * self.quantity

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.get_full_name()} {self.product.name} {self.quantity} {self.size}'



class Order(models.Model):
    """
    Order Model
    """
    



    order_number = models.CharField(max_length=25,
                                    unique=True,
                                    default=generate_order_number,
                                    editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    total_amount = models.PositiveIntegerField()
    shipping_address = models.TextField(null=True, blank=True,
                                        help_text='If not provided, your address will be used')
    # billing_address = models.TextField()
    # payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ['created_at']
        unique_together = ['order_number', 'user']

class OrderItem(models.Model):
    """
    Order Item Model
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)
    size = models.CharField(null=True, blank=True, max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

    class Meta:
        ordering = ['created_at']


class Like(models.Model):
    """
    Likes model
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    like = models.BooleanField(null=True, blank=True)
    dislike = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def is_like(self):
        return self.like == 1

    def is_dislike(self):
        return self.dislike == 1

    def __str__(self):
        if self.is_like():
            return "like"
        if self.is_dislike():
            return "dislike"
        return "no vote"
    
    class Meta:
        unique_together = ['user', 'product']


class Review(models.Model):
    """
    Review Model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.review = self.review.lower().capitalize()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

class ImageReviews(models.Model):
    """
    Image Reviews Model
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reviews')
    image = models.ImageField(upload_to='reviews/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
