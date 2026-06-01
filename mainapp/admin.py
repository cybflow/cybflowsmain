from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------ list
    list_display = (
        "title",
        "status_badge",
        "published_at",
        "updated_at",
        "view_on_site_link",
    )
    list_filter = ("status", "published_at", "updated_at")
    search_fields = ("title", "slug", "excerpt", "content", "meta_description")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    list_per_page = 25
    actions = ["make_published", "make_draft"]

    # ------------------------------------------------------------------ form
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "is_published_display")
    fieldsets = (
        (
            "Content",
            {
                "fields": ("title", "slug", "excerpt", "content", "status"),
            },
        ),
        (
            "SEO",
            {
                "fields": ("seo_title", "meta_description"),
                "description": (
                    "Leave blank to fall back to the post title / excerpt. "
                    "SEO title ≤ 60 chars; meta description ≤ 160 chars recommended."
                ),
            },
        ),
        (
            "Publishing",
            {
                "fields": ("published_at", "is_published_display"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # ------------------------------------------------------------------ helpers
    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        if obj.status == BlogPost.PUBLISHED and obj.published_at <= timezone.now():
            colour = "#16a34a"
            label = "Live"
        elif obj.status == BlogPost.PUBLISHED:
            colour = "#f97316"
            label = "Scheduled"
        else:
            colour = "#64748b"
            label = "Draft"
        return format_html(
            '<span style="'
            "display:inline-block;padding:2px 10px;border-radius:999px;"
            "font-size:0.8rem;font-weight:600;"
            "background:{bg};color:#fff;"
            '">{label}</span>',
            bg=colour,
            label=label,
        )

    @admin.display(description="View")
    def view_on_site_link(self, obj):
        if obj.is_published:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">'
                "↗ Visit"
                "</a>",
                obj.get_absolute_url(),
            )
        return "—"

    @admin.display(description="Currently visible to public?", boolean=True)
    def is_published_display(self, obj):
        return obj.is_published

    # ------------------------------------------------------------------ bulk actions
    @admin.action(description="Publish selected posts")
    def make_published(self, request, queryset):
        updated = queryset.update(status=BlogPost.PUBLISHED)
        self.message_user(request, f"{updated} post(s) marked as published.")

    @admin.action(description="Revert selected posts to draft")
    def make_draft(self, request, queryset):
        updated = queryset.update(status=BlogPost.DRAFT)
        self.message_user(request, f"{updated} post(s) reverted to draft.")
