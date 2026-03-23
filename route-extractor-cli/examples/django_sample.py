# Sample Django urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/<int:pk>/", views.UserDetail.as_view(), name="user-detail"),
    path("items/", views.ItemList.as_view(), name="item-list"),
]
