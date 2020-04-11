
from django.contrib import admin
from django.urls import path,include
from Kameteeapp.API.views import *


urlpatterns = [
    path('',RegisterUser,name='RegisterUser')
    
]
