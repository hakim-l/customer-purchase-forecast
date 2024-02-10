from django.urls import path, include
from .dashapp import plot
from . import views

urlpatterns= [
    path('',views.purchase_prediction_view,name='purchase_prediction'),
    path('dash/', include('django_plotly_dash.urls'))
]