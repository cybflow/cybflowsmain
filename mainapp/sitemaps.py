from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .models import BlogPost


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "blog_list",
            "whois",
            "cloud_hosting",
            "vps_hosting",
            "web_hosting",
            "reseller_hosting",
            "managed_wordpress_hosting",
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(
            status=BlogPost.PUBLISHED,
            published_at__lte=timezone.now(),
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
