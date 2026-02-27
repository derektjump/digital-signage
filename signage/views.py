"""
Digital Signage Views

This module provides views for the digital signage design and data management portal.

Views:
    MAIN INTERFACE:
    - OverviewView: Main dashboard with statistics
    - ScreenDesignListView: List all screen designs
    - ScreenDesignUpdateView: Create/edit screen designs
    - ScreenDesignPreviewView: Preview a screen design

    DEVICE MANAGEMENT:
    - DeviceDetailView: Individual device management page
    - DeviceDeleteView: Delete a device with confirmation

    PLAYLIST MANAGEMENT:
    - PlaylistCreateView: Create new playlists
    - PlaylistUpdateView: Edit existing playlists
    - PlaylistDeleteView: Delete a playlist

    AJAX ENDPOINTS:
    - register_device_with_code: Register a device using its code
    - assign_device_content: Assign playlist or screen to a device
    - upload_media: Upload media files
    - create_folder: Create media folder
    - create_device_group: Create device group
    - update_device_group: Update device group assignment

    API ENDPOINTS FOR FIRE TV DEVICES:
    - device_request_code: Request registration code
    - device_register: Mark device as registered
    - device_config: Get device configuration
    - screen_player: Public player for Fire TV devices
    - media_player: Public media player
    - get_sales_data_api: Get sales data as JSON
"""

from django.views.generic import ListView, UpdateView, CreateView, DeleteView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.cache import cache
from datetime import timedelta
from django.db.models import Q, F
from django.contrib import messages
from pathlib import Path
from .models import (
    ScreenDesign, Screen, SalesData, KPI, Device, DeviceGroup, Playlist, PlaylistItem,
    MediaFolder, MediaAsset, DesignFolder, ScreenTemplate, generate_registration_code
)
from .data_services import get_sales_data, get_employee_data, get_all_data, clear_sales_cache, clear_employee_cache, get_available_data_variables
import json
import os


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def index(request):
    """Landing page - redirects to overview if authenticated."""
    if request.user.is_authenticated:
        return redirect('signage:overview')
    return redirect('signage:auth_login')


def test(request):
    """Simple test page to verify app is running."""
    return HttpResponse("""
        <html>
        <head><title>Digital Signage - Test</title></head>
        <body style="background:#0a0a0b;color:#01ffff;font-family:sans-serif;padding:2rem;">
            <h1>Digital Signage is running!</h1>
            <p style="color:#e4e8ec;">The app is working. <a href="/login/" style="color:#01ffff;">Click here to login</a></p>
        </body>
        </html>
    """)


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

class OverviewView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard with statistics and quick actions.

    Provides an overview of:
    - Total designs, devices, playlists
    - Device status (online/recent/offline)
    - Recent activity
    """

    template_name = 'signage/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get only registered devices and calculate status counts
        devices = Device.objects.filter(registered=True)
        online_count = sum(1 for d in devices if d.status == 'online')
        recent_count = sum(1 for d in devices if d.status == 'recent')
        offline_count = sum(1 for d in devices if d.status == 'offline')

        # Statistics
        context['stats'] = {
            'total_designs': ScreenDesign.objects.filter(is_active=True).count(),
            'devices_online': online_count,
            'devices_recent': recent_count,
            'devices_offline': offline_count,
            'total_playlists': Playlist.objects.filter(is_active=True).count(),
        }

        # Data for dashboard
        context['devices'] = devices.order_by('-last_seen')[:10]
        context['designs'] = ScreenDesign.objects.filter(is_active=True).order_by('-updated_at')[:10]
        context['playlists'] = Playlist.objects.filter(is_active=True).order_by('name')[:10]

        # Media stats
        context['media_stats'] = {
            'total': MediaAsset.objects.filter(is_active=True).count(),
            'images': MediaAsset.objects.filter(is_active=True, asset_type='image').count(),
            'videos': MediaAsset.objects.filter(is_active=True, asset_type='video').count(),
        }

        # Device groups
        context['device_groups'] = DeviceGroup.objects.filter(is_active=True).order_by('name')

        return context


# ============================================================================
# SCREEN DESIGN MANAGEMENT
# ============================================================================

class ScreenDesignListView(LoginRequiredMixin, ListView):
    """List all screen designs."""

    model = ScreenDesign
    template_name = 'signage/screen_design_list.html'
    context_object_name = 'designs'

    def get_queryset(self):
        queryset = ScreenDesign.objects.all().order_by('-updated_at')
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        # Filter by folder
        folder = self.request.GET.get('folder')
        if folder == 'unfiled':
            queryset = queryset.filter(folder__isnull=True)
        elif folder:
            queryset = queryset.filter(folder__slug=folder)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['design_folders'] = DesignFolder.objects.all().order_by('name')
        context['total_count'] = ScreenDesign.objects.count()
        context['active_count'] = ScreenDesign.objects.filter(is_active=True).count()
        return context


class ScreenDesignUpdateView(LoginRequiredMixin, UpdateView):
    """Create or edit a screen design."""

    model = ScreenDesign
    template_name = 'signage/screen_design_form.html'
    fields = ['name', 'slug', 'description', 'folder', 'html_code', 'css_code', 'js_code', 'notes', 'is_active',
              'store_filter_id', 'date_filter_mode', 'page_duration']
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """Return existing object or None for new design."""
        slug = self.kwargs.get('slug')
        if slug:
            return get_object_or_404(ScreenDesign, slug=slug)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = self.object is None
        context['design_folders'] = DesignFolder.objects.all().order_by('name')

        # Get available stores for the filter dropdown
        try:
            from .models import SalesBoardSummary
            context['available_stores'] = SalesBoardSummary.objects.using('data_connect').values(
                'store_id', 'store_name'
            ).distinct().order_by('store_name')
        except Exception:
            context['available_stores'] = []

        return context

    def form_valid(self, form):
        if self.object is None:
            # Creating new design
            self.object = form.save(commit=False)
            if not self.object.slug:
                self.object.slug = slugify(self.object.name)
            self.object.save()
        else:
            form.save()
        return redirect('signage:screen_design_list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            form = self.get_form_class()(request.POST)
        else:
            form = self.get_form_class()(request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class ScreenDesignPreviewView(LoginRequiredMixin, DetailView):
    """Preview a screen design (internal use, requires login)."""

    model = ScreenDesign
    template_name = 'signage/screen_design_preview.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ScreenDesignDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a screen design with confirmation."""

    model = ScreenDesign
    template_name = 'signage/screen_design_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('signage:screen_design_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        design = self.get_object()
        context['device_count'] = Device.objects.filter(assigned_screen=design).count()
        context['playlist_count'] = PlaylistItem.objects.filter(screen=design).count()
        return context


# ============================================================================
# TEMPLATE LIBRARY
# ============================================================================

@login_required
def template_gallery(request):
    """
    Display gallery of available templates with filtering by type.
    """
    template_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')

    templates = ScreenTemplate.objects.filter(is_active=True)

    if template_type:
        templates = templates.filter(template_type=template_type)

    if search_query:
        templates = templates.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'templates': templates,
        'featured_templates': ScreenTemplate.objects.filter(is_active=True, is_featured=True)[:4],
        'template_types': ScreenTemplate.TemplateType.choices,
        'selected_type': template_type,
        'search_query': search_query,
        'total_templates': templates.count(),
    }

    return render(request, 'signage/template_gallery.html', context)


@login_required
def template_detail(request, slug):
    """View template details."""
    template = get_object_or_404(ScreenTemplate, slug=slug, is_active=True)
    context = {
        'template': template,
    }
    return render(request, 'signage/template_detail.html', context)


def template_preview(request, slug):
    """
    Preview a template with optional branding customization.
    This is a public endpoint (no login required) for iframe embedding.
    """
    template = get_object_or_404(ScreenTemplate, slug=slug)

    # Get branding overrides from query params (for live preview)
    branding_overrides = {}
    for key in ['primary_color', 'secondary_color', 'accent_color',
                'background_color', 'text_color', 'heading_font', 'body_font']:
        if request.GET.get(key):
            branding_overrides[key] = request.GET.get(key)

    # Merge with template's default branding
    effective_branding = {**template.branding_config, **branding_overrides}

    # Generate branding CSS
    branding_css = ''
    if effective_branding:
        css_vars = []
        mappings = {
            'primary_color': '--brand-primary',
            'secondary_color': '--brand-secondary',
            'accent_color': '--brand-accent',
            'background_color': '--brand-bg',
            'text_color': '--brand-text',
            'heading_font': '--brand-heading-font',
            'body_font': '--brand-body-font',
        }
        for key, css_var in mappings.items():
            if key in effective_branding and effective_branding[key]:
                css_vars.append(f'    {css_var}: {effective_branding[key]};')
        if css_vars:
            branding_css = ':root {\n' + '\n'.join(css_vars) + '\n}\n'

    context = {
        'template': template,
        'branding_config': effective_branding,
        'branding_css': branding_css,
    }

    return render(request, 'signage/template_preview.html', context)


@login_required
def save_as_template(request, slug):
    """
    Save an existing screen design as a reusable template.
    """
    design = get_object_or_404(ScreenDesign, slug=slug)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        template_type = request.POST.get('template_type', 'custom')

        if not name:
            messages.error(request, 'Template name is required.')
            return redirect('signage:save_as_template', slug=slug)

        # Generate slug
        template_slug = slugify(name)
        base_slug = template_slug
        counter = 1
        while ScreenTemplate.objects.filter(slug=template_slug).exists():
            template_slug = f"{base_slug}-{counter}"
            counter += 1

        # Parse branding config from form
        branding_config = {}
        for key in ['primary_color', 'secondary_color', 'accent_color',
                    'background_color', 'text_color', 'heading_font', 'body_font']:
            value = request.POST.get(key, '').strip()
            if value:
                branding_config[key] = value

        # Create template
        template = ScreenTemplate.objects.create(
            name=name,
            slug=template_slug,
            description=description,
            template_type=template_type,
            html_code=design.html_code,
            css_code=design.css_code,
            js_code=design.js_code,
            branding_config=branding_config,
            source_design=design,
        )

        messages.success(request, f'Template "{template.name}" created successfully!')
        return redirect('signage:template_gallery')

    # GET request - show form
    context = {
        'design': design,
        'template_types': ScreenTemplate.TemplateType.choices,
    }
    return render(request, 'signage/save_as_template.html', context)


@login_required
def create_from_template(request, slug):
    """
    Create a new screen design from a template.
    """
    template = get_object_or_404(ScreenTemplate, slug=slug, is_active=True)

    # Get available stores for the filter dropdown
    available_stores = []
    try:
        from .models import SalesBoardSummary
        available_stores = list(
            SalesBoardSummary.objects.using('data_connect')
            .values('store_id', 'store_name')
            .distinct().order_by('store_name')
        )
    except Exception:
        pass

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        folder_id = request.POST.get('folder', '').strip()
        store_filter_id = request.POST.get('store_filter_id', '').strip()
        date_filter_mode = request.POST.get('date_filter_mode', 'current').strip()
        page_duration_str = request.POST.get('page_duration', '').strip()

        if not name:
            messages.error(request, 'Design name is required.')
            return redirect('signage:create_from_template', slug=slug)

        # Generate slug for the new design
        design_slug = slugify(name)
        base_slug = design_slug
        counter = 1
        while ScreenDesign.objects.filter(slug=design_slug).exists():
            design_slug = f"{base_slug}-{counter}"
            counter += 1

        # Parse branding config from form and generate CSS
        branding_config = {}
        for key in ['primary_color', 'secondary_color', 'accent_color',
                    'background_color', 'text_color', 'heading_font', 'body_font']:
            value = request.POST.get(key, '').strip()
            if value:
                branding_config[key] = value

        # Generate branding CSS block
        css_code = template.css_code or ''
        if branding_config:
            css_vars = []
            mappings = {
                'primary_color': '--brand-primary',
                'secondary_color': '--brand-secondary',
                'accent_color': '--brand-accent',
                'background_color': '--brand-bg',
                'text_color': '--brand-text',
                'heading_font': '--brand-heading-font',
                'body_font': '--brand-body-font',
            }
            for key, css_var in mappings.items():
                if key in branding_config and branding_config[key]:
                    css_vars.append(f'    {css_var}: {branding_config[key]};')
            if css_vars:
                branding_css = '/* Branding Variables (from template) */\n:root {\n' + '\n'.join(css_vars) + '\n}\n\n'
                css_code = branding_css + css_code

        # Get folder if specified
        folder = None
        if folder_id:
            try:
                folder = DesignFolder.objects.get(id=folder_id)
            except DesignFolder.DoesNotExist:
                pass

        # Parse page duration
        page_duration = None
        if page_duration_str:
            try:
                page_duration = int(page_duration_str)
            except ValueError:
                pass

        # Create new design with store filter
        design = ScreenDesign.objects.create(
            name=name,
            slug=design_slug,
            description=description,
            html_code=template.html_code,
            css_code=css_code,
            js_code=template.js_code,
            folder=folder,
            store_filter_id=int(store_filter_id) if store_filter_id else None,
            date_filter_mode=date_filter_mode,
            page_duration=page_duration,
        )

        # Increment template usage count
        ScreenTemplate.objects.filter(id=template.id).update(usage_count=F('usage_count') + 1)

        messages.success(request, f'Design "{design.name}" created from template!')
        return redirect('signage:screen_design_update', slug=design.slug)

    # GET request - show form
    context = {
        'template': template,
        'design_folders': DesignFolder.objects.all().order_by('name'),
        'available_stores': available_stores,
    }
    return render(request, 'signage/create_from_template.html', context)


@login_required
def template_edit(request, slug):
    """
    Edit an existing template.
    """
    template = get_object_or_404(ScreenTemplate, slug=slug)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        template_type = request.POST.get('template_type', 'custom')

        if not name:
            messages.error(request, 'Template name is required.')
            return redirect('signage:template_edit', slug=slug)

        # Update template
        template.name = name
        template.description = description
        template.template_type = template_type

        # Parse branding config from form
        branding_config = {}
        for key in ['primary_color', 'secondary_color', 'accent_color',
                    'background_color', 'text_color', 'heading_font', 'body_font']:
            value = request.POST.get(key, '').strip()
            if value:
                branding_config[key] = value

        template.branding_config = branding_config
        template.is_featured = request.POST.get('is_featured') == 'on'
        template.is_active = request.POST.get('is_active') == 'on'

        # Handle thumbnail upload
        if 'thumbnail' in request.FILES:
            template.thumbnail = request.FILES['thumbnail']

        template.save()

        messages.success(request, f'Template "{template.name}" updated successfully!')
        return redirect('signage:template_gallery')

    # GET request - show form
    context = {
        'template': template,
        'template_types': ScreenTemplate.TemplateType.choices,
    }
    return render(request, 'signage/template_edit.html', context)


@login_required
def template_delete(request, slug):
    """
    Delete a template with confirmation.
    """
    template = get_object_or_404(ScreenTemplate, slug=slug)

    if request.method == 'POST':
        name = template.name
        template.delete()
        messages.success(request, f'Template "{name}" deleted successfully!')
        return redirect('signage:template_gallery')

    # GET request - show confirmation
    context = {
        'template': template,
    }
    return render(request, 'signage/template_confirm_delete.html', context)


# ============================================================================
# DEVICE MANAGEMENT
# ============================================================================

class DeviceListView(LoginRequiredMixin, ListView):
    """List all devices."""

    model = Device
    template_name = 'signage/device_list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        return Device.objects.filter(registered=True).select_related('group', 'assigned_playlist', 'assigned_screen').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registered_devices = Device.objects.filter(registered=True)
        context['registered_count'] = registered_devices.count()
        context['online_count'] = len([d for d in registered_devices if d.status == 'online'])
        context['total_count'] = registered_devices.count()
        context['device_groups'] = DeviceGroup.objects.filter(is_active=True).order_by('name')
        return context


class DeviceDetailView(LoginRequiredMixin, UpdateView):
    """Individual device management page."""

    model = Device
    template_name = 'signage/device_detail.html'
    fields = ['name', 'group', 'location', 'assigned_playlist', 'assigned_screen', 'notes']
    success_url = reverse_lazy('signage:device_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device_status'] = self.object.status
        context['available_playlists'] = Playlist.objects.filter(is_active=True)
        context['available_designs'] = ScreenDesign.objects.filter(is_active=True)
        context['device_groups'] = DeviceGroup.objects.filter(is_active=True).order_by('name')
        return context


class DeviceDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a device with confirmation."""

    model = Device
    template_name = 'signage/device_confirm_delete.html'
    success_url = reverse_lazy('signage:device_list')


# ============================================================================
# PLAYLIST MANAGEMENT
# ============================================================================

class PlaylistListView(LoginRequiredMixin, ListView):
    """List all playlists."""

    model = Playlist
    template_name = 'signage/playlist_list.html'
    context_object_name = 'playlists'

    def get_queryset(self):
        return Playlist.objects.all().order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_count'] = Playlist.objects.filter(is_active=True).count()
        context['total_count'] = Playlist.objects.count()
        return context


class PlaylistCreateView(LoginRequiredMixin, CreateView):
    """Create a new playlist."""

    model = Playlist
    template_name = 'signage/playlist_form.html'
    fields = ['name', 'is_active']
    success_url = reverse_lazy('signage:playlist_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context['available_designs'] = ScreenDesign.objects.filter(is_active=True).order_by('name')
        context['media_assets'] = MediaAsset.objects.filter(is_active=True).order_by('name')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_playlist_items(self.object, self.request.POST.getlist('items[]'))
        return response

    def _save_playlist_items(self, playlist, items_data):
        """Parse items[] form data and create PlaylistItem objects."""
        playlist.items.all().delete()
        for order, item_str in enumerate(items_data):
            try:
                parts = item_str.split(':')
                if len(parts) != 3:
                    continue
                item_type, item_id, duration = parts
                item_kwargs = {
                    'playlist': playlist,
                    'item_type': item_type,
                    'order': order,
                    'duration_seconds': int(duration),
                }
                if item_type == 'screen':
                    item_kwargs['screen_id'] = item_id
                elif item_type == 'media':
                    item_kwargs['media_asset_id'] = item_id
                else:
                    continue
                PlaylistItem.objects.create(**item_kwargs)
            except (ValueError, TypeError):
                continue


class PlaylistUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing playlist."""

    model = Playlist
    template_name = 'signage/playlist_form.html'
    fields = ['name', 'is_active']
    success_url = reverse_lazy('signage:playlist_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['available_designs'] = ScreenDesign.objects.filter(is_active=True).order_by('name')
        context['media_assets'] = MediaAsset.objects.filter(is_active=True).order_by('name')
        context['playlist_items'] = self.object.items.all().order_by('order')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_playlist_items(self.object, self.request.POST.getlist('items[]'))
        return response

    def _save_playlist_items(self, playlist, items_data):
        """Parse items[] form data and create PlaylistItem objects."""
        playlist.items.all().delete()
        for order, item_str in enumerate(items_data):
            try:
                parts = item_str.split(':')
                if len(parts) != 3:
                    continue
                item_type, item_id, duration = parts
                item_kwargs = {
                    'playlist': playlist,
                    'item_type': item_type,
                    'order': order,
                    'duration_seconds': int(duration),
                }
                if item_type == 'screen':
                    item_kwargs['screen_id'] = item_id
                elif item_type == 'media':
                    item_kwargs['media_asset_id'] = item_id
                else:
                    continue
                PlaylistItem.objects.create(**item_kwargs)
            except (ValueError, TypeError):
                continue


class PlaylistDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a playlist with confirmation."""

    model = Playlist
    template_name = 'signage/playlist_confirm_delete.html'
    success_url = reverse_lazy('signage:playlist_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.get_object()
        context['device_count'] = Device.objects.filter(assigned_playlist=playlist).count()
        return context


# ============================================================================
# MEDIA LIBRARY
# ============================================================================

class MediaAssetListView(LoginRequiredMixin, ListView):
    """List all media assets (images and videos)."""

    model = MediaAsset
    template_name = 'signage/media_list.html'
    context_object_name = 'media_assets'

    def get_queryset(self):
        queryset = MediaAsset.objects.all().select_related('folder').order_by('-created_at')

        # Filter by folder if specified
        folder_slug = self.request.GET.get('folder')
        if folder_slug:
            queryset = queryset.filter(folder__slug=folder_slug)

        # Filter by type if specified
        asset_type = self.request.GET.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folders'] = MediaFolder.objects.all().order_by('name')

        # Get the actual queryset being displayed (unfiltered base)
        all_assets = MediaAsset.objects.all()
        context['image_count'] = all_assets.filter(asset_type='image').count()
        context['video_count'] = all_assets.filter(asset_type='video').count()
        context['total_count'] = all_assets.count()

        context['current_folder'] = self.request.GET.get('folder', '')
        context['current_type'] = self.request.GET.get('type', '')
        return context


# ============================================================================
# AJAX ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def register_device_with_code(request):
    """Register a device using its registration code."""
    try:
        data = json.loads(request.body) if request.body else {}
        code = data.get('code', '').strip().upper()

        if not code:
            return JsonResponse({'success': False, 'error': 'Registration code is required'}, status=400)

        try:
            device = Device.objects.get(registration_code=code)
        except Device.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'No device found with code: {code}'}, status=404)

        device.registered = True

        # Save name and group if provided (from admin registration modal)
        name = data.get('name', '').strip()
        if name:
            device.name = name
        elif not device.name:
            device.name = f'Device {code}'

        group_id = data.get('group_id')
        if group_id:
            try:
                device.group = DeviceGroup.objects.get(id=group_id)
            except DeviceGroup.DoesNotExist:
                pass

        device.save()

        return JsonResponse({
            'success': True,
            'device': {
                'id': str(device.id),
                'name': device.name,
                'registration_code': device.registration_code,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def assign_device_content(request, pk):
    """Assign playlist or screen to a device."""
    try:
        device = get_object_or_404(Device, id=pk)
        data = json.loads(request.body) if request.body else {}

        playlist_id = data.get('playlist_id')
        screen_id = data.get('screen_id')

        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id)
            device.assigned_playlist = playlist
            device.assigned_screen = None
            device.save()
            return JsonResponse({'success': True, 'assigned_type': 'playlist', 'assigned_name': playlist.name})

        if screen_id:
            screen = get_object_or_404(ScreenDesign, id=screen_id)
            device.assigned_screen = screen
            device.assigned_playlist = None
            device.save()
            return JsonResponse({'success': True, 'assigned_type': 'screen', 'assigned_name': screen.name})

        return JsonResponse({'success': False, 'error': 'playlist_id or screen_id required'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def upload_media(request):
    """Upload media files (images/videos)."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({'success': False, 'error': 'No files provided'}, status=400)

    folder = None
    folder_id = request.POST.get('folder')
    if folder_id:
        try:
            folder = MediaFolder.objects.get(id=folder_id)
        except MediaFolder.DoesNotExist:
            pass

    uploaded = []
    for f in files:
        name = os.path.splitext(f.name)[0]
        slug = slugify(name)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while MediaAsset.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        asset = MediaAsset(name=name, slug=slug, folder=folder, file=f)
        asset.file_size = f.size
        asset.save()
        uploaded.append({'id': str(asset.id), 'name': asset.name, 'type': asset.asset_type})

    return JsonResponse({'success': True, 'uploaded_count': len(uploaded), 'assets': uploaded})


@csrf_exempt
@require_http_methods(["POST"])
def create_folder(request):
    """Create a media folder."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body) if request.body else {}
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Folder name required'}, status=400)

        folder = MediaFolder(name=name, slug=slugify(name))
        folder.save()
        return JsonResponse({'success': True, 'folder': {'id': str(folder.id), 'name': folder.name}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_design_folder(request):
    """Create a design folder."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body) if request.body else {}
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Folder name required'}, status=400)

        folder = DesignFolder(name=name, slug=slugify(name))
        folder.save()
        return JsonResponse({'success': True, 'folder': {'id': str(folder.id), 'name': folder.name}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_device_group(request):
    """Create a device group."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body) if request.body else {}
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Group name required'}, status=400)

        group = DeviceGroup(name=name, slug=slugify(name))
        group.save()
        return JsonResponse({'success': True, 'group': {'id': str(group.id), 'name': group.name}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_device_group(request, device_id):
    """Update device group assignment."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        device = get_object_or_404(Device, id=device_id)
        data = json.loads(request.body) if request.body else {}
        group_id = data.get('group_id')

        if group_id:
            group = get_object_or_404(DeviceGroup, id=group_id)
            device.group = group
        else:
            device.group = None

        device.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_design_folder(request, design_id):
    """Update design folder assignment."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        design = get_object_or_404(ScreenDesign, id=design_id)
        data = json.loads(request.body) if request.body else {}
        folder_id = data.get('folder_id')

        if folder_id:
            folder = get_object_or_404(DesignFolder, id=folder_id)
            design.folder = folder
        else:
            design.folder = None

        design.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_media(request, media_id):
    """Get media asset details."""
    asset = get_object_or_404(MediaAsset, id=media_id)
    return JsonResponse({
        'id': str(asset.id),
        'name': asset.name,
        'slug': asset.slug,
        'type': asset.asset_type,
        'url': asset.file.url if asset.file else None,
        'folder': str(asset.folder.id) if asset.folder else None,
    })


@csrf_exempt
@require_http_methods(["POST"])
def update_media(request, media_id):
    """Update media asset."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        asset = get_object_or_404(MediaAsset, id=media_id)
        data = json.loads(request.body) if request.body else {}

        if 'name' in data:
            asset.name = data['name']
        if 'folder_id' in data:
            if data['folder_id']:
                asset.folder = get_object_or_404(MediaFolder, id=data['folder_id'])
            else:
                asset.folder = None

        asset.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_media(request, media_id):
    """Delete media asset."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        asset = get_object_or_404(MediaAsset, id=media_id)
        asset.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# DEVICE API ENDPOINTS (for Fire TV devices)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def device_request_code(request):
    """Request a registration code for a new device."""
    try:
        # Parse request body for optional device name
        try:
            data = json.loads(request.body) if request.body else {}
        except (json.JSONDecodeError, ValueError):
            data = {}
        device_name = data.get('device_name', '').strip()

        # Generate unique registration code
        code = generate_registration_code()
        while Device.objects.filter(registration_code=code).exists():
            code = generate_registration_code()

        # Create new device with code
        device = Device(registration_code=code, registered=False)
        if device_name:
            device.name = device_name
        device.save()

        return JsonResponse({
            'success': True,
            'device_id': str(device.id),
            'registration_code': code
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def device_register(request, device_id):
    """Mark device as registered."""
    try:
        device = get_object_or_404(Device, id=device_id)
        device.registered = True
        device.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def device_config(request, device_id):
    """Get device configuration (assigned content).

    Returns format expected by Fire TV app:
    {
        "success": true,
        "registered": true/false,
        "config": {
            "type": "playlist" | "screen" | "none",
            "playlist_id": "...",       // for playlists
            "screen_id": "...",         // for screens
            "items": [{                 // for playlists
                "player_url": "https://...",
                "duration_seconds": 30
            }],
            "player_url": "https://..." // for single screens
        }
    }
    """
    try:
        device = get_object_or_404(Device, id=device_id)

        # Update last_seen
        device.last_seen = timezone.now()
        device.save(update_fields=['last_seen'])

        # Build base URL for absolute player URLs
        base_url = request.build_absolute_uri('/').rstrip('/')

        # Build configuration in format expected by Fire TV app
        config = {'type': 'none'}

        if device.assigned_playlist:
            items = []
            for item in device.assigned_playlist.items.order_by('order'):
                if item.item_type == 'screen' and item.screen:
                    duration = item.effective_duration
                    # For screens with page_duration, calculate dynamic duration
                    # based on actual employee/page count
                    if item.screen.page_duration:
                        try:
                            emp_data = get_employee_data(store_id=item.screen.store_filter_id)
                            if emp_data and emp_data.get('employees'):
                                page_count = len(emp_data['employees'])
                                if page_count > 0:
                                    duration = page_count * item.screen.page_duration
                        except Exception:
                            pass  # Fall back to static duration
                    items.append({
                        'player_url': base_url + reverse('signage:screen_player', kwargs={'slug': item.screen.slug}),
                        'duration_seconds': duration,
                    })
                elif item.item_type == 'media' and item.media_asset:
                    items.append({
                        'player_url': base_url + reverse('signage:media_player', kwargs={'slug': item.media_asset.slug}),
                        'duration_seconds': item.effective_duration,
                    })

            config = {
                'type': 'playlist',
                'playlist_id': str(device.assigned_playlist.id),
                'items': items,
            }

        elif device.assigned_screen:
            config = {
                'type': 'screen',
                'screen_id': str(device.assigned_screen.id),
                'player_url': base_url + reverse('signage:screen_player', kwargs={'slug': device.assigned_screen.slug}),
            }

        response_data = {
            'success': True,
            'registered': device.registered,
            'config': config,
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def device_config_by_code(request, code):
    """Get device configuration by registration code."""
    try:
        device = get_object_or_404(Device, registration_code=code.upper())
        return device_config(request, device.id)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# PUBLIC PLAYER ENDPOINTS (no authentication)
# ============================================================================

def screen_player(request, slug):
    """Full-screen player for Fire TV devices."""
    design = get_object_or_404(ScreenDesign, slug=slug)
    return render(request, 'signage/player.html', {'design': design})


def screen_design_api(request, slug):
    """API endpoint to get screen design as JSON."""
    design = get_object_or_404(ScreenDesign, slug=slug)
    return JsonResponse({
        'name': design.name,
        'slug': design.slug,
        'html': design.html_code,
        'css': design.css_code,
        'js': design.js_code,
        'store_filter_id': design.store_filter_id,
        'date_filter_mode': design.date_filter_mode,
        'page_duration': design.page_duration,
    })


def media_player(request, slug):
    """Full-screen media player for Fire TV devices."""
    asset = get_object_or_404(MediaAsset, slug=slug)
    return render(request, 'signage/media_player.html', {'asset': asset})


# ============================================================================
# DATA API ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_sales_data_api(request):
    """Get sales data as JSON for screen templates."""
    try:
        data = get_sales_data()
        return JsonResponse({'success': True, 'sales': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_data_variables_api(request):
    """Get available data variables for templates."""
    variables = get_available_data_variables()
    return JsonResponse({'success': True, 'variables': variables})


@login_required
@require_http_methods(["POST"])
def clear_sales_cache_api(request):
    """Clear sales data cache."""
    clear_sales_cache()
    return JsonResponse({'success': True, 'message': 'Cache cleared'})


@csrf_exempt
@require_http_methods(["GET"])
def get_employee_data_api(request):
    """Get employee-level sales data as JSON for screen templates."""
    try:
        store_id = request.GET.get('store_id')
        if store_id:
            store_id = int(store_id)
        data = get_employee_data(store_id=store_id)
        return JsonResponse({'success': True, 'employees': data})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid store_id'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_all_data_api(request):
    """Get both store and employee sales data in one call."""
    try:
        store_id = request.GET.get('store_id')
        if store_id:
            store_id = int(store_id)
        data = get_all_data(store_id=store_id)
        return JsonResponse({'success': True, **data})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid store_id'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_data_registry_api(request):
    """
    Get data field registry for the visual data picker.

    Returns the complete catalog of available data fields with
    descriptions, examples, and type information for the screen builder.
    """
    from .data_registry import DataFieldRegistry
    registry = DataFieldRegistry()
    return JsonResponse({
        'success': True,
        'registry': registry.to_json()
    })


# ============================================================================
# VISUAL BUILDER
# ============================================================================

@login_required
def visual_builder_create(request):
    """
    Visual Builder for creating new screen designs.
    """
    from .component_registry import get_component_registry_json
    from .data_registry import DataFieldRegistry

    registry = DataFieldRegistry()

    context = {
        'is_new': True,
        'design': None,
        'component_registry_json': get_component_registry_json(),
        'data_registry_json': json.dumps(registry.to_json()),
    }
    return render(request, 'signage/visual_builder.html', context)


@login_required
def visual_builder_update(request, slug):
    """
    Visual Builder for editing existing screen designs.
    """
    from .component_registry import get_component_registry_json
    from .data_registry import DataFieldRegistry

    design = get_object_or_404(ScreenDesign, slug=slug)
    registry = DataFieldRegistry()

    context = {
        'is_new': False,
        'design': design,
        'component_registry_json': get_component_registry_json(),
        'data_registry_json': json.dumps(registry.to_json()),
    }
    return render(request, 'signage/visual_builder.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def visual_builder_create_save(request):
    """
    Save a new design from Visual Builder.
    """
    try:
        name = request.POST.get('name', 'Untitled Design').strip()
        html_code = request.POST.get('html_code', '')
        css_code = request.POST.get('css_code', '')
        js_code = request.POST.get('js_code', '')
        visual_data = request.POST.get('visual_builder_data', '')

        # Generate slug
        base_slug = slugify(name) or 'design'
        slug = base_slug
        counter = 1
        while ScreenDesign.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create design
        design = ScreenDesign.objects.create(
            name=name,
            slug=slug,
            html_code=html_code,
            css_code=css_code,
            js_code=js_code,
            is_active=True,
        )

        # Store visual builder data if model supports it
        if hasattr(design, 'visual_builder_data') and visual_data:
            try:
                design.visual_builder_data = json.loads(visual_data)
                design.save()
            except json.JSONDecodeError:
                pass

        return JsonResponse({
            'success': True,
            'slug': design.slug,
            'redirect': reverse('signage:visual_builder_update', args=[design.slug])
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def visual_builder_save(request, slug):
    """
    Save an existing design from Visual Builder.
    """
    try:
        design = get_object_or_404(ScreenDesign, slug=slug)

        name = request.POST.get('name', design.name).strip()
        html_code = request.POST.get('html_code', design.html_code)
        css_code = request.POST.get('css_code', design.css_code)
        js_code = request.POST.get('js_code', design.js_code)
        visual_data = request.POST.get('visual_builder_data', '')

        design.name = name
        design.html_code = html_code
        design.css_code = css_code
        design.js_code = js_code

        # Store visual builder data if model supports it
        if hasattr(design, 'visual_builder_data') and visual_data:
            try:
                design.visual_builder_data = json.loads(visual_data)
            except json.JSONDecodeError:
                pass

        design.save()

        return JsonResponse({
            'success': True,
            'slug': design.slug,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_component_registry_api(request):
    """
    Get component registry for Visual Builder.
    """
    from .component_registry import get_component_registry
    return JsonResponse({
        'success': True,
        'components': get_component_registry()
    })


# ============================================================================
# FIRE TV APP DOWNLOAD
# ============================================================================

APK_FILENAME = 'the-grid-signage.apk'
APK_BLOB_NAME = 'apk/the-grid-signage.apk'


def _get_blob_client():
    """Get Azure Blob Storage client, or None if not configured."""
    account_name = getattr(settings, 'AZURE_STORAGE_ACCOUNT_NAME', '')
    account_key = getattr(settings, 'AZURE_STORAGE_ACCOUNT_KEY', '')
    container = getattr(settings, 'AZURE_STORAGE_CONTAINER', 'digital-signage')

    if not account_name or not account_key:
        return None

    from azure.storage.blob import BlobServiceClient
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={account_name};"
        f"AccountKey={account_key};"
        f"EndpointSuffix=core.windows.net"
    )
    service = BlobServiceClient.from_connection_string(connection_string)
    container_client = service.get_container_client(container)

    # Ensure container exists
    try:
        container_client.get_container_properties()
    except Exception:
        container_client.create_container(public_access='blob')

    return container_client.get_blob_client(APK_BLOB_NAME)


def _get_apk_info():
    """
    Check APK availability. Returns (available, size_str, download_url).
    Uses Azure Blob Storage in production, local file in development.
    """
    blob_client = _get_blob_client()

    if blob_client:
        # Azure Blob Storage
        try:
            props = blob_client.get_blob_properties()
            size_str = f"{props.size / (1024 * 1024):.1f} MB"
            return True, size_str, blob_client.url
        except Exception:
            return False, None, None
    else:
        # Local file fallback (development)
        apk_path = Path(settings.MEDIA_ROOT) / 'signage' / 'apk' / APK_FILENAME
        if apk_path.exists():
            size_str = f"{apk_path.stat().st_size / (1024 * 1024):.1f} MB"
            return True, size_str, None
        return False, None, None


def firetv_download(request):
    """
    Fire TV app download landing page.

    Public page (no auth) so Fire TV's Downloader app can access it.
    Shows install instructions and a download button.
    """
    apk_available, apk_size, blob_url = _get_apk_info()

    context = {
        'apk_available': apk_available,
        'apk_size': apk_size,
        'apk_filename': APK_FILENAME,
        'blob_url': blob_url,
    }
    return render(request, 'signage/firetv_download.html', context)


def firetv_apk_download(request):
    """
    Serve the Fire TV APK file for download.

    Redirects to Azure Blob URL in production, serves local file in development.
    """
    blob_client = _get_blob_client()

    if blob_client:
        # Redirect to Azure Blob Storage URL
        try:
            blob_client.get_blob_properties()
            from django.shortcuts import redirect as redir
            return redir(blob_client.url)
        except Exception:
            raise Http404("APK file not found in Azure Blob Storage.")
    else:
        # Local file fallback
        apk_path = Path(settings.MEDIA_ROOT) / 'signage' / 'apk' / APK_FILENAME
        if not apk_path.exists():
            raise Http404("APK file not found. Build and upload the APK first.")

        return FileResponse(
            open(apk_path, 'rb'),
            content_type='application/vnd.android.package-archive',
            as_attachment=True,
            filename=APK_FILENAME,
        )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def firetv_upload_apk(request):
    """
    Upload a new APK file via the admin interface.
    Uploads to Azure Blob Storage in production, local file in development.
    """
    if 'apk_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No APK file provided'}, status=400)

    apk_file = request.FILES['apk_file']
    if not apk_file.name.endswith('.apk'):
        return JsonResponse({'success': False, 'error': 'File must be an .apk file'}, status=400)

    blob_client = _get_blob_client()

    if blob_client:
        # Upload to Azure Blob Storage
        from azure.storage.blob import ContentSettings
        blob_client.upload_blob(
            apk_file.read(),
            overwrite=True,
            content_settings=ContentSettings(
                content_type='application/vnd.android.package-archive'
            ),
        )
        props = blob_client.get_blob_properties()
        size_str = f"{props.size / (1024 * 1024):.1f} MB"
    else:
        # Local file fallback
        apk_dir = Path(settings.MEDIA_ROOT) / 'signage' / 'apk'
        apk_dir.mkdir(parents=True, exist_ok=True)
        apk_path = apk_dir / APK_FILENAME

        with open(apk_path, 'wb') as f:
            for chunk in apk_file.chunks():
                f.write(chunk)

        size_str = f"{apk_path.stat().st_size / (1024 * 1024):.1f} MB"

    return JsonResponse({'success': True, 'size': size_str})


# ============================================================================
# DEPRECATED VIEWS (kept for backward compatibility)
# ============================================================================

class ScreenPlayView(TemplateView):
    """DEPRECATED: Legacy ScreenCloud player."""
    template_name = 'signage/screen_test_play.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['screen'] = get_object_or_404(Screen, slug=kwargs['slug'], is_active=True)
        return context


class SalesDataListView(LoginRequiredMixin, ListView):
    """DEPRECATED: Sales data display."""
    model = SalesData
    template_name = 'signage/sales_data_list.html'
    context_object_name = 'sales_data'
    ordering = ['-date', 'store', 'employee']


class KPIListView(LoginRequiredMixin, ListView):
    """DEPRECATED: KPI display."""
    model = KPI
    template_name = 'signage/kpi_list.html'
    context_object_name = 'kpis'
    ordering = ['-date', 'store', 'employee']


class DisplayDashboardView(LoginRequiredMixin, TemplateView):
    """DEPRECATED: Combined dashboard."""
    template_name = 'signage/display_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales_data'] = SalesData.objects.order_by('-date', 'store')[:20]
        context['kpis'] = KPI.objects.order_by('-date', 'store')[:20]
        return context
