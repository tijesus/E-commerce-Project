# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review, Product

@receiver(post_save, sender=Review)
def increment_review_count(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.total_reviews += 1
        product.save()
        print('Review count incremented')

@receiver(post_delete, sender=Review)
def decrement_review_count(sender, instance, **kwargs):
    product = instance.product
    if product.total_reviews > 0:
        product.total_reviews -= 1
        product.save()