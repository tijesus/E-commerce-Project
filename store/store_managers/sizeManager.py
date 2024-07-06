from django.db.models import Manager

class UndeletedSizeManager(Manager):
    """
    returns the sizes of all undeleted products
    """
    def get_queryset(self):
        return super().get_queryset().select_related('product').filter(product__is_deleted=False)