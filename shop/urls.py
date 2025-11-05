from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("register/", views.shop_register, name="shop_register"),
    path("profile/", views.shop_profile, name="shop_profile"),
    path("update/", views.shop_update, name="shop_update"),
    path("item_list/", views.item_list, name="item_list"),
    path("item_list/<pk>/delete/", views.item_list_delete, name="item_list_delete"),
    path("item_list/<pk>/update/", views.item_update, name="item_update"),
    
    path("price/", views.price, name="price"),
    path("price/<pk>/delete/", views.price_delete, name="price_delete"),
    path("price/<pk>/update/", views.price_update, name="price_update"),

    path("staffs/", views.staffs, name="staffs"),
    path('staffs/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staffs/<int:pk>/update/', views.staff_update, name='staff_update'),
    path('staffs/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
]   