from django.db import models


# Create your models here.

class Customers(models.Model):
    customer_id = models.IntegerField(name= 'customer_id',
                                      primary_key=True
                                      )
    class Meta:
        db_table= 'customers'

class ProductDetails(models.Model):
    product_id = models.IntegerField(name='product_id', primary_key=True)
    category = models.CharField(name='category',
                                max_length= 255
                                )
    price = models.FloatField(name='price')
    ratings = models.FloatField(name='ratings')

    class Meta:
        db_table= 'product_details'

class CustomerInteractions(models.Model):
    customer_id= models.ForeignKey(Customers,
                                   name= 'customer',
                                   on_delete=models.CASCADE
                                   )

    page_views= models.FloatField(name= 'page_views')
    time_spent= models.FloatField(name= 'time_spent')

    class Meta:
        db_table= 'customer_interactions'

class PurchaseHistory(models.Model):
    customer_id= models.ForeignKey(Customers,
                                   name= 'customer',
                                   on_delete=models.CASCADE
                                   )

    product_id= models.ForeignKey(ProductDetails,
                                  name= 'product',
                                  on_delete=models.CASCADE
                                  )

    purchase_date= models.DateField(name='purchase_date')

    class Meta:
        db_table= 'purchase_history'