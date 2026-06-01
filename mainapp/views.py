import ipaddress
import socket
from urllib.parse import urlparse

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import BlogPost


# ---------------------------------------------------------------------------
# Static service page data
# ---------------------------------------------------------------------------
SERVICE_PAGES = {
    "cloud-hosting": {
        "title": "Cloud Hosting",
        "eyebrow": "Elastic infrastructure",
        "description": "Deploy on scalable cloud infrastructure tuned for growing businesses, product teams, and high-traffic websites that need room to expand.",
        "summary": "Cybflows Cloud Hosting gives you managed performance, resilient resources, fast provisioning, and simple scaling without the operational weight of maintaining your own cloud stack.",
        "stats": [("40 GB+", "NVMe storage"), ("2 TB+", "Bandwidth"), ("99.99%", "Uptime target")],
        "panel_note": "Optional cPanel/WHM with LiteSpeed for teams that want managed cloud performance with familiar controls.",
        "cpanel_features": ["LiteSpeed Web Server", "LSCache acceleration", "cPanel/WHM optional", "AutoSSL", "Backups", "Resource graphs", "DNS tools", "PHP selector"],
        "benefits": [
            "Scale CPU, memory, and storage as demand grows.",
            "Built-in snapshots and managed infrastructure updates.",
            "Low-latency routing for business-critical workloads.",
            "Priority support from a technical hosting team.",
        ],
        "plans": [
            {"name": "Starter", "price": "$49", "period": "/mo", "discount": "62% Off", "term": "Renews monthly, billed as cloud VPS hosting.", "ram": "8 GB RAM", "vcores": "4 vCores", "storage": "120 GB NVMe", "bandwidth": "5 TB", "panel": "Optional cPanel + LiteSpeed", "best_for": "Growing apps", "features": ["8 GB RAM", "4 vCores", "120 GB NVMe", "5 TB bandwidth", "Optional cPanel", "LiteSpeed ready"]},
            {"name": "Business", "price": "$89", "period": "/mo", "discount": "70% Off", "label": "Most Popular", "term": "Best value for production workloads.", "ram": "16 GB RAM", "vcores": "8 vCores", "storage": "240 GB NVMe", "bandwidth": "10 TB", "panel": "cPanel/WHM + LiteSpeed", "best_for": "Production workloads", "featured": True, "features": ["16 GB RAM", "8 vCores", "240 GB NVMe", "10 TB bandwidth", "cPanel/WHM", "LiteSpeed included"]},
            {"name": "Enterprise", "price": "Custom", "period": "", "discount": "Custom Deal", "term": "Designed around traffic, compliance, and scale.", "ram": "16 GB+ RAM", "vcores": "8+ vCores", "storage": "Custom NVMe", "bandwidth": "Custom", "panel": "Managed stack + LiteSpeed", "best_for": "High-scale teams", "features": ["16 GB+ RAM", "8+ vCores", "Custom NVMe", "Custom bandwidth", "Managed stack", "LiteSpeed architecture"]},
        ],
    },
    "vps-hosting": {
        "title": "VPS Hosting",
        "eyebrow": "Dedicated control",
        "description": "Run demanding applications on virtual private servers with dedicated resources, root access, and performance isolation.",
        "summary": "Cybflows VPS Hosting is designed for developers and teams that want control without sacrificing reliability, security, or support.",
        "stats": [("Root", "Access"), ("60 GB+", "NVMe storage"), ("3 TB+", "Bandwidth")],
        "panel_note": "VPS plans focus on isolated compute. cPanel/WHM and LiteSpeed can be added for managed web workloads.",
        "cpanel_features": ["Optional cPanel/WHM", "LiteSpeed add-on", "Root access", "Firewall controls", "Dedicated IP", "Snapshots", "DNS tools", "PHP selector"],
        "benefits": [
            "Dedicated resources for predictable application performance.",
            "Root access for custom runtime and server configuration.",
            "Firewall, backups, and dedicated IP options.",
            "Upgrade capacity quickly as workloads mature.",
        ],
        "plans": [
            {"name": "Starter", "price": "$22", "period": "/mo", "discount": "55% Off", "term": "Flexible monthly VPS billing.", "ram": "4 GB RAM", "vcores": "2 vCores", "storage": "60 GB NVMe", "bandwidth": "3 TB", "panel": "Optional cPanel", "best_for": "Dev servers", "features": ["4 GB RAM", "2 vCores", "60 GB NVMe", "3 TB bandwidth", "Root access", "Optional cPanel"]},
            {"name": "Business", "price": "$48", "period": "/mo", "discount": "64% Off", "label": "Most Popular", "term": "Balanced power for web apps.", "ram": "8 GB RAM", "vcores": "4 vCores", "storage": "160 GB NVMe", "bandwidth": "6 TB", "panel": "Optional cPanel + LiteSpeed", "best_for": "Web apps", "featured": True, "features": ["8 GB RAM", "4 vCores", "160 GB NVMe", "6 TB bandwidth", "Dedicated IP", "LiteSpeed add-on"]},
            {"name": "Enterprise", "price": "$119", "period": "/mo", "discount": "Custom Scale", "term": "For heavier isolated workloads.", "ram": "16 GB RAM", "vcores": "8 vCores", "storage": "400 GB NVMe", "bandwidth": "12 TB", "panel": "Managed stack optional", "best_for": "Heavy workloads", "features": ["16 GB RAM", "8 vCores", "400 GB NVMe", "12 TB bandwidth", "High availability", "Managed options"]},
        ],
    },
    "web-hosting": {
        "title": "Web Hosting",
        "eyebrow": "Fast websites",
        "description": "Reliable hosting for websites, landing pages, portfolios, and business sites that need speed without complexity.",
        "summary": "Cybflows Web Hosting includes the essentials teams expect: SSL, daily backups, optimized caching, clean management, and support that responds quickly.",
        "stats": [("SSL", "Included"), ("20 GB+", "SSD storage"), ("Daily", "Backups")],
        "panel_note": "Web Hosting includes the complete cPanel experience with LiteSpeed acceleration for fast business websites.",
        "cpanel_features": ["cPanel included", "LiteSpeed Web Server", "LSCache", "WordPress Toolkit", "Softaculous", "Email accounts", "AutoSSL", "File Manager", "MySQL databases", "PHP selector", "Cron jobs", "Visitor metrics"],
        "benefits": [
            "Simple control panel for managing websites and domains.",
            "Optimized caching for fast page delivery.",
            "Daily backups and SSL included as standard.",
            "Transparent pricing for personal and business websites.",
        ],
        "plans": [
            {"name": "Starter", "price": "$8", "period": "/mo", "discount": "83% Off", "term": "Billed yearly for simple websites.", "ram": "2 GB RAM", "vcores": "1 vCore", "storage": "20 GB SSD", "bandwidth": "Unlimited", "panel": "cPanel + LiteSpeed", "best_for": "Personal sites", "features": ["Free domain for 1 year", "2 GB RAM", "1 vCore", "20 GB SSD", "cPanel included", "LiteSpeed server"]},
            {"name": "Premium", "price": "$18", "period": "/mo", "discount": "76% Off", "label": "Most Popular", "term": "Billed yearly for growing sites.", "ram": "2 GB RAM", "vcores": "2 vCores", "storage": "80 GB SSD", "bandwidth": "Unlimited", "panel": "cPanel + LiteSpeed + LSCache", "best_for": "Business sites", "featured": True, "features": ["Free domain for 1 year", "2 GB RAM", "2 vCores", "80 GB SSD", "Daily backups", "LiteSpeed + LSCache"]},
            {"name": "Business", "price": "$39", "period": "/mo", "discount": "68% Off", "term": "Billed yearly for higher traffic.", "ram": "4 GB RAM", "vcores": "2 vCores", "storage": "200 GB SSD", "bandwidth": "Unlimited", "panel": "Full cPanel + LiteSpeed", "best_for": "High-traffic sites", "features": ["Free domain for 1 year", "4 GB RAM", "2 vCores", "200 GB SSD", "Priority support", "Full LiteSpeed stack"]},
        ],
    },
    "reseller-hosting": {
        "title": "Reseller Hosting",
        "eyebrow": "Launch your hosting brand",
        "description": "Sell hosting under your own brand with white-label tools, private nameservers, and scalable account management.",
        "summary": "Cybflows Reseller Hosting helps agencies, freelancers, and entrepreneurs package reliable infrastructure as their own managed service.",
        "stats": [("White", "Label"), ("WHM", "Included"), ("Unlimited", "Bandwidth")],
        "panel_note": "Reseller Hosting includes WHM, cPanel account management, and LiteSpeed performance for client websites.",
        "cpanel_features": ["WHM included", "Client cPanel accounts", "LiteSpeed Web Server", "LSCache", "Private nameservers", "AutoSSL", "Package manager", "Account backups", "Email hosting", "DNS zones", "PHP selector", "Usage reporting"],
        "benefits": [
            "White-label hosting built for client delivery.",
            "WHM/cPanel tooling for easy account management.",
            "Private nameservers and brand-friendly workflows.",
            "Predictable plans with room to grow client revenue.",
        ],
        "plans": [
            {"name": "Starter", "price": "$15", "period": "/mo", "discount": "70% Off", "term": "Launch a small reseller business.", "ram": "2 GB RAM", "vcores": "1 vCore", "storage": "50 GB SSD", "bandwidth": "Unlimited", "panel": "WHM + cPanel + LiteSpeed", "best_for": "New resellers", "features": ["WHM included", "2 GB RAM", "1 vCore", "50 GB SSD", "Client cPanel accounts", "LiteSpeed server"]},
            {"name": "Premium", "price": "$34", "period": "/mo", "discount": "74% Off", "label": "Most Popular", "term": "Built for agencies and recurring clients.", "ram": "2 GB RAM", "vcores": "2 vCores", "storage": "140 GB SSD", "bandwidth": "Unlimited", "panel": "WHM + cPanel + LSCache", "best_for": "Agencies", "featured": True, "features": ["Private nameservers", "2 GB RAM", "2 vCores", "140 GB SSD", "Daily backups", "LiteSpeed + LSCache"]},
            {"name": "Business", "price": "$74", "period": "/mo", "discount": "65% Off", "term": "For established hosting brands.", "ram": "4 GB RAM", "vcores": "2 vCores", "storage": "320 GB SSD", "bandwidth": "Unlimited", "panel": "Full WHM/cPanel + LiteSpeed", "best_for": "Hosting brands", "features": ["Advanced branding", "4 GB RAM", "2 vCores", "320 GB SSD", "Priority support", "Full WHM/cPanel"]},
        ],
    },
    "managed-wordpress-hosting": {
        "title": "Managed WordPress Hosting",
        "eyebrow": "WordPress, refined",
        "description": "Optimized managed WordPress hosting for content teams, agencies, and businesses that need fast pages and fewer maintenance chores.",
        "summary": "Cybflows Managed WordPress Hosting combines tuned caching, security hardening, updates, backups, and migration support for serious WordPress sites.",
        "stats": [("1-click", "Staging"), ("Daily", "Backups"), ("Managed", "Updates")],
        "panel_note": "Managed WordPress uses cPanel controls with LiteSpeed and LSCache tuned specifically for WordPress speed.",
        "cpanel_features": ["cPanel included", "LiteSpeed Web Server", "LSCache for WordPress", "WordPress Toolkit", "Staging", "AutoSSL", "Daily backups", "Malware scanning", "PHP selector", "MySQL databases", "Email accounts", "Metrics"],
        "benefits": [
            "WordPress-tuned performance and caching.",
            "Managed updates, backups, SSL, and security monitoring.",
            "Staging workflows for safer content and theme changes.",
            "Expert migration help for existing WordPress sites.",
        ],
        "plans": [
            {"name": "Starter", "price": "$12", "period": "/mo", "discount": "78% Off", "term": "For one optimized WordPress site.", "ram": "2 GB RAM", "vcores": "1 vCore", "storage": "30 GB SSD", "bandwidth": "Unlimited", "panel": "cPanel + LiteSpeed + LSCache", "best_for": "1 WordPress site", "features": ["WordPress Toolkit", "2 GB RAM", "1 vCore", "30 GB SSD", "Daily backups", "LSCache for WordPress"]},
            {"name": "Premium", "price": "$29", "period": "/mo", "discount": "72% Off", "label": "Most Popular", "term": "For growing WordPress sites.", "ram": "2 GB RAM", "vcores": "2 vCores", "storage": "120 GB SSD", "bandwidth": "Unlimited", "panel": "cPanel + WP Toolkit + LiteSpeed", "best_for": "Growing WordPress", "featured": True, "features": ["Staging tools", "2 GB RAM", "2 vCores", "120 GB SSD", "Managed updates", "LiteSpeed + LSCache"]},
            {"name": "Business", "price": "Custom", "period": "", "discount": "Scale Deal", "term": "For high-traffic WordPress operations.", "ram": "4 GB RAM", "vcores": "2 vCores", "storage": "Custom SSD", "bandwidth": "Unlimited", "panel": "Managed WordPress stack", "best_for": "High-traffic WordPress", "features": ["Custom architecture", "4 GB RAM", "2 vCores", "Custom SSD", "Priority support", "Managed LiteSpeed stack"]},
        ],
    },
}


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def home(request):
    return render(request, "home.html")


def service_page(request, slug):
    service = SERVICE_PAGES.get(slug)
    if service is None:
        raise Http404(f"No service page found for slug: {slug!r}")
    return render(request, "service_page.html", {"service": service, "slug": slug})


# ---------------------------------------------------------------------------
# WHOIS — safe, no server internals exposed
# ---------------------------------------------------------------------------

_PRIVATE_NETS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),   # link-local / AWS metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
)


def _is_public_ip(ip_str: str) -> bool:
    """Return True only for globally routable unicast addresses."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return not any(ip in net for net in _PRIVATE_NETS) and ip.is_global
    except ValueError:
        return False


def _clean_lookup_target(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"//{value}")
    host = parsed.hostname or value
    return host.strip().strip("[]")


def _whois_query(server: str, query: str) -> str:
    try:
        with socket.create_connection((server, 43), timeout=5) as sock:
            sock.settimeout(5)
            sock.sendall((query + "\r\n").encode("utf-8", errors="ignore"))
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
    except OSError as exc:
        return f"WHOIS lookup failed at {server}: {exc}"
    return b"".join(chunks).decode("utf-8", errors="replace")


def _lookup_whois(ip_address: str) -> str:
    iana_response = _whois_query("whois.iana.org", ip_address)
    referral = ""
    for line in iana_response.splitlines():
        if line.lower().startswith("whois:"):
            referral = line.split(":", 1)[1].strip()
            break
    if referral:
        rir_response = _whois_query(referral, ip_address)
        return f"{iana_response.strip()}\n\n--- {referral} ---\n{rir_response.strip()}"
    return iana_response.strip()


def _parse_location(whois_text: str) -> dict:
    fields: dict = {}
    interesting = {"country", "city", "stateprov", "state", "region", "org", "org-name", "netname"}
    for line in whois_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key in interesting and value and key not in fields:
            fields[key] = value
    location_parts = [
        fields.get("city"),
        fields.get("stateprov") or fields.get("state") or fields.get("region"),
        fields.get("country"),
    ]
    return {
        "location": ", ".join(p for p in location_parts if p) or "Not available in WHOIS records",
        "organization": fields.get("org-name") or fields.get("org") or fields.get("netname") or "Not available",
    }


def whois_lookup(request):
    query = request.GET.get("q", "")
    result = None
    error = ""
    target = _clean_lookup_target(query)

    if target:
        try:
            ipaddress.ip_address(target)
            resolved_ip = target
        except ValueError:
            try:
                resolved_ip = socket.gethostbyname(target)
            except OSError as exc:
                resolved_ip = ""
                error = f"Could not resolve {target!r}: {exc}"

        if resolved_ip:
            if not _is_public_ip(resolved_ip):
                error = "Only publicly routable IP addresses can be looked up."
                resolved_ip = ""

        if resolved_ip:
            whois_text = _lookup_whois(resolved_ip)
            geo = _parse_location(whois_text)
            try:
                reverse_dns = socket.gethostbyaddr(resolved_ip)[0]
            except OSError:
                reverse_dns = "No reverse DNS record found"
            result = {
                "target": target,
                "ip_address": resolved_ip,
                "reverse_dns": reverse_dns,
                "location": geo["location"],
                "organization": geo["organization"],
                "whois": whois_text[:12000],
            }

    return render(request, "whois.html", {"query": query, "result": result, "error": error})


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

def blog_list(request):
    posts = BlogPost.objects.filter(
        status=BlogPost.PUBLISHED,
        published_at__lte=timezone.now(),
    )
    return render(request, "blog_list.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        status=BlogPost.PUBLISHED,
        published_at__lte=timezone.now(),
    )
    return render(request, "blog_detail.html", {"post": post})
