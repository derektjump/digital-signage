"""
Admin configuration for Digital Signage application.
"""

from django.contrib import admin
from .models import (
    UserSession, ScreenDesign, DesignFolder, Screen, ScreenTemplate,
    Playlist, PlaylistItem, Device, DeviceGroup,
    MediaFolder, MediaAsset, SalesData, KPI, DataSource
)


# =============================================================================
# AUTHENTICATION
# =============================================================================

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_valid', 'created_at', 'updated_at')
    list_filter = ('is_valid', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


# =============================================================================
# SCREEN DESIGNS
# =============================================================================

@admin.register(DesignFolder)
class DesignFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'design_count', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ScreenDesign)
class ScreenDesignAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'folder', 'is_active', 'updated_at')
    list_filter = ('is_active', 'folder', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'folder', 'is_active')
        }),
        ('Code', {
            'fields': ('html_code', 'css_code', 'js_code'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ScreenTemplate)
class ScreenTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'is_featured', 'usage_count', 'created_at')
    list_filter = ('template_type', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'usage_count', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'template_type', 'is_active', 'is_featured')
        }),
        ('Thumbnail', {
            'fields': ('thumbnail',),
        }),
        ('Code', {
            'fields': ('html_code', 'css_code', 'js_code'),
            'classes': ('collapse',)
        }),
        ('Branding', {
            'fields': ('branding_config',),
            'classes': ('collapse',)
        }),
        ('Source', {
            'fields': ('source_design',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('id', 'usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    """DEPRECATED: Legacy Screen model admin."""
    list_display = ('name', 'slug', 'layout_type', 'is_active', 'updated_at')
    list_filter = ('is_active', 'layout_type')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


# =============================================================================
# PLAYLISTS
# =============================================================================

class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 1
    ordering = ['order']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'device_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlaylistItemInline]


@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'item_type', 'content_name', 'order', 'duration_seconds')
    list_filter = ('playlist', 'item_type')
    ordering = ['playlist', 'order']


# =============================================================================
# DEVICES
# =============================================================================

@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'device_count', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description', 'address')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_code', 'group', 'registered', 'status', 'last_seen')
    list_filter = ('registered', 'group', 'created_at')
    search_fields = ('name', 'registration_code', 'location', 'notes')
    readonly_fields = ('id', 'last_seen', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'registration_code', 'registered')
        }),
        ('Assignment', {
            'fields': ('assigned_playlist', 'assigned_screen')
        }),
        ('Location', {
            'fields': ('group', 'location')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_seen', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# MEDIA LIBRARY
# =============================================================================

@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'asset_count', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'asset_type', 'folder', 'is_active', 'created_at')
    list_filter = ('asset_type', 'is_active', 'folder')
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('id', 'file_size', 'width', 'height', 'duration_seconds', 'created_at', 'updated_at')


# =============================================================================
# SALES DATA
# =============================================================================

@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('store', 'employee', 'date', 'total_sales')
    list_filter = ('store', 'date')
    search_fields = ('store', 'employee')
    date_hierarchy = 'date'


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('store', 'employee', 'date', 'sales_target', 'actual_sales', 'is_on_target')
    list_filter = ('store', 'date')
    search_fields = ('store', 'employee')
    date_hierarchy = 'date'


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'data_type', 'is_active', 'refresh_interval')
    list_filter = ('data_type', 'is_active')
    search_fields = ('name', 'key', 'description')
    prepopulated_fields = {'key': ('name',)}
