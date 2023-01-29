from django.urls import path
from django.conf import settings
from .import views
# this is for prevent user from access home page without logout
from django.contrib.auth.views import LogoutView
from .views import CheckUserSubscription
urlpatterns = [
    path('TaroosGame/', views.homePage, name='index'),
    path('Game/', views.GamePage,name='game'),
    path('', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('password/', views.updatePassword, name='password'),
    path('register/', views.RegisterPage, name='register'),
    path('plan/', views.planDetails, name='plan'),
    path('checkout', views.checkOut, name='checkout'),
    path('success/', views.checkOutSucess, name='success'),
    path('profile/', views.Profile, name='profile'),
]
CheckUserSubscription()
