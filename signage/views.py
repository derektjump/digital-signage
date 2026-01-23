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
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.cache import cache
from datetime import timedelta
from .models import (
    ScreenDesign, Screen, SalesData, KPI, Device, DeviceGroup, Playlist, PlaylistItem,
    MediaFolder, MediaAsset, DesignFolder, generate_registration_code
)
from .data_services import get_sales_data, clear_sales_cache, get_available_data_variables
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
    fields = ['name', 'slug', 'description', 'folder', 'html_code', 'css_code', 'js_code', 'notes', 'is_active']
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
# DEVICE MANAGEMENT
# ============================================================================

class DeviceListView(LoginRequiredMixin, ListView):
    """List all devices."""

    model = Device
    template_name = 'signage/device_list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        return Device.objects.all().select_related('group', 'assigned_playlist', 'assigned_screen').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registered_count'] = Device.objects.filter(registered=True).count()
        context['online_count'] = len([d for d in Device.objects.all() if d.status == 'online'])
        context['total_count'] = Device.objects.count()
        context['device_groups'] = DeviceGroup.objects.filter(is_active=True).order_by('name')
        return context


class DeviceDetailView(LoginRequiredMixin, UpdateView):
    """Individual device management page."""

    model = Device
    template_name = 'signage/device_detail.html'
    fields = ['name', 'group', 'location', 'assigned_playlist', 'assigned_screen', 'notes']
    success_url = reverse_lazy('signage:overview')

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
    success_url = reverse_lazy('signage:overview')


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
    success_url = reverse_lazy('signage:overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context['available_designs'] = ScreenDesign.objects.filter(is_active=True).order_by('name')
        context['media_assets'] = MediaAsset.objects.filter(is_active=True).order_by('name')
        return context


class PlaylistUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing playlist."""

    model = Playlist
    template_name = 'signage/playlist_form.html'
    fields = ['name', 'is_active']
    success_url = reverse_lazy('signage:overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['available_designs'] = ScreenDesign.objects.filter(is_active=True).order_by('name')
        context['media_assets'] = MediaAsset.objects.filter(is_active=True).order_by('name')
        context['playlist_items'] = self.object.items.all().order_by('order')
        return context


class PlaylistDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a playlist with confirmation."""

    model = Playlist
    template_name = 'signage/playlist_confirm_delete.html'
    success_url = reverse_lazy('signage:overview')

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
        device.save()

        return JsonResponse({
            'success': True,
            'device': {
                'id': str(device.id),
                'name': device.name or f'Device {code}',
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
        # Generate unique registration code
        code = generate_registration_code()
        while Device.objects.filter(registration_code=code).exists():
            code = generate_registration_code()

        # Create new device with code
        device = Device(registration_code=code, registered=False)
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
    """Get device configuration (assigned content)."""
    try:
        device = get_object_or_404(Device, id=device_id)

        # Update last_seen
        device.last_seen = timezone.now()
        device.save(update_fields=['last_seen'])

        # Check cache first
        cache_key = f'device_config_{device_id}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse(cached)

        # Build configuration
        config = {
            'device_id': str(device.id),
            'name': device.name,
            'registered': device.registered,
            'content_type': None,
            'content': None,
        }

        if device.assigned_playlist:
            items = []
            for item in device.assigned_playlist.items.order_by('order'):
                if item.item_type == 'screen' and item.screen:
                    items.append({
                        'type': 'screen',
                        'slug': item.screen.slug,
                        'name': item.screen.name,
                        'duration': item.effective_duration,
                        'url': reverse('signage:screen_player', kwargs={'slug': item.screen.slug})
                    })
                elif item.item_type == 'media' and item.media_asset:
                    items.append({
                        'type': 'media',
                        'slug': item.media_asset.slug,
                        'name': item.media_asset.name,
                        'duration': item.effective_duration,
                        'url': reverse('signage:media_player', kwargs={'slug': item.media_asset.slug})
                    })

            config['content_type'] = 'playlist'
            config['content'] = {
                'name': device.assigned_playlist.name,
                'items': items
            }

        elif device.assigned_screen:
            config['content_type'] = 'screen'
            config['content'] = {
                'name': device.assigned_screen.name,
                'slug': device.assigned_screen.slug,
                'url': reverse('signage:screen_player', kwargs={'slug': device.assigned_screen.slug})
            }

        # Cache for 60 seconds
        cache.set(cache_key, config, 60)
        return JsonResponse(config)

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
