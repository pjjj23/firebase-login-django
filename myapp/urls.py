from django.urls import path
from . import views 
from django.conf import settings

urlpatterns=[
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('user/userhomepage', views.userhomepage, name='userhomepage'),
    path("logout/", views.logout_view, name="logout"),
    path("OTPVerification/", views.OTPVerification, name="OTPVerification"),
    path("adminhomepage/", views.adminhomepage, name="adminhomepage"),
]