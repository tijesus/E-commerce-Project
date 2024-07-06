from django.db import models

class UndeletedProductManager(models.Manager):
    """
    returns all undeleted products
    """
    def get_queryset(self):
        return super().get_queryset().prefetch_related('sizes', 'categories').filter(is_deleted=False)