from django.contrib import admin
from django.urls import path,include
from django.contrib.sitemaps.views import sitemap

from mainapp.sitemaps import BlogSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('',include('mainapp.urls')),
]   
