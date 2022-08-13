from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index,name="index"),
    path('payment/', views.order_payment,name="payment"),
    path("callback/", views.callback, name="callback"),

]