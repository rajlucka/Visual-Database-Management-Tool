"""ocr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import os
from django.contrib import admin
from django.urls import path
from mysite import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('test', views.test,name='test'),
    path('home', views.home,name='home'),
    path('', views.login,name='login'),
    path('logout', views.logout,name='logout'),
    path('project', views.project,name='project'),
    path('template', views.template,name='template'),
    path('project_template/<int:project_id>', views.project_template,name='project_template'),
    path('add_project', views.add_project,name='add_project'),
    path('add_template', views.add_template,name='add_template'),
    path('delete_project/<int:project_id>', views.delete_project,name='delete_project'),
    path('delete_template/<int:template_id>', views.delete_template,name='delete_template'),
    path('update_project/<int:project_id>', views.update_project,name='update_project'),
    path('update_template/<int:template_id>', views.update_template,name='update_template'),
    path('display_template_file/<int:template_id>', views.display_template_file,name='display_template_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

