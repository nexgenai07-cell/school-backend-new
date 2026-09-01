from django.urls import path

from . import portal_views as views

urlpatterns = [
    path('login/', views.login_view, name='portal_login'),
    path('logout/', views.logout_view, name='portal_logout'),
    path('', views.portal_home, name='portal_home'),
    path('<slug:role>/', views.dashboard, name='portal_dashboard'),
    path('<slug:role>/m/<slug:module>/', views.module_list, name='portal_list'),
    path('<slug:role>/m/<slug:module>/<int:pk>/', views.module_detail, name='portal_detail'),
]
