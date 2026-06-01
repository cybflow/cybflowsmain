from django.db import models
from django.urls import reverse
from django.utils import timezone


class BlogPost(models.Model):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField(max_length=320, blank=True)
    content = models.TextField(
        help_text="Supports plain text. Use blank lines to separate paragraphs."
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=DRAFT,
        db_index=True,
    )
    # SEO
    seo_title = models.CharField(
        max_length=180,
        blank=True,
        help_text="Overrides <title> tag. Leave blank to use the post title.",
    )
    meta_description = models.CharField(
        max_length=220,
        blank=True,
        help_text="Overrides meta description. Leave blank to use the excerpt.",
    )
    # Dates
    published_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Controls when the post becomes publicly visible.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Blog post"
        verbose_name_plural = "Blog posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == self.PUBLISHED and self.published_at <= timezone.now()

    # Convenience helpers used in templates
    @property
    def display_title(self):
        """SEO title if set, else post title."""
        return self.seo_title or self.title

    @property
    def display_description(self):
        """Meta description if set, else excerpt."""
        return self.meta_description or self.excerpt
