from django.urls import path

from . import admin_views as views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('m/<slug:module>/', views.module_list, name='admin_panel_list'),
    path('m/<slug:module>/add/', views.module_create, name='admin_panel_create'),
    path('m/<slug:module>/<int:pk>/edit/', views.module_edit, name='admin_panel_edit'),
    path('m/<slug:module>/<int:pk>/delete/', views.module_delete, name='admin_panel_delete'),
]