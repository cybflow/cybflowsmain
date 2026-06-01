from django.urls import path
from . import views as view

urlpatterns = [
    path('', view.home),
    path('cloud-hosting/', view.service_page, {"slug": "cloud-hosting"}, name="cloud_hosting"),
    path('vps-hosting/', view.service_page, {"slug": "vps-hosting"}, name="vps_hosting"),
    path('web-hosting/', view.service_page, {"slug": "web-hosting"}, name="web_hosting"),
    path('reseller-hosting/', view.service_page, {"slug": "reseller-hosting"}, name="reseller_hosting"),
    path('managed-wordpress-hosting/', view.service_page, {"slug": "managed-wordpress-hosting"}, name="managed_wordpress_hosting"),
    path('whois/', view.whois_lookup, name="whois"),
    path('blog/', view.blog_list, name="blog_list"),
    path('blog/<slug:slug>/', view.blog_detail, name="blog_detail"),
]
