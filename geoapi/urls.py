from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('login/', views.login_view, name='login_view'),
    path('signup/', views.signup_view, name='signup_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('upload/', views.upload_view, name='upload_view'),
    path('visualize', views.visualise_data, name='visualise'),
    path('datasets', views.dataset_explorer, name='dataset'),
    path('datasets/view/<str:layer_name>/', views.view_dataset, name='view_dataset'),
    path('datasets/metadata/<str:layer_name>/', views.view_metadata, name='view_metadata'),
    path('geo-chat/', views.geo_llm_chat, name='geo_chat'), 
]
