"""
URL configuration for neofi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chatapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/register", views.register, name="register"),
    path("api/login", views.login, name="login"),
    path("api/online-users", views.online_users, name="online_users"),
    path("api/chat/start", views.chat_start, name="chat_start"),
    path("api/chat/send", views.chat_send, name="chat_send"),
    path("api/suggested-friends/<int:user_id>", views.suggested_friends, name="chat_send"),
]
