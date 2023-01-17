from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('logout', LogoutView.as_view()),
    path('accounts/', include('allauth.urls')),
    path('accounts/',include('accounts.urls')),
    path('',include('main.urls')),
]
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)