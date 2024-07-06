from django.db.models import Manager

class UndeletedProductImageManager(Manager):
    """
    Manager for undeleted product.
    """
    def get_queryset(self):
        """
        overides the default get_queryset to return undeleted products.
        """
        return super().get_queryset().select_related("product").filter(product__is_deleted=False)
