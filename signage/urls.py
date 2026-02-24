"""
URL configuration for Digital Signage application.
"""

from django.urls import path
from . import views, auth_views

app_name = 'signage'

urlpatterns = [
    # =========================================================================
    # MAIN PAGES
    # =========================================================================
    path('', views.OverviewView.as_view(), name='overview'),
    path('test/', views.test, name='test'),

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    path('login/', auth_views.login_view, name='auth_login'),
    path('callback/', auth_views.callback_view, name='auth_callback'),
    path('logout/', auth_views.logout_view, name='auth_logout'),

    # =========================================================================
    # SCREEN DESIGNS
    # =========================================================================
    path('designs/', views.ScreenDesignListView.as_view(), name='screen_design_list'),
    path('designs/new/', views.ScreenDesignUpdateView.as_view(), name='screen_design_create'),
    path('designs/<slug:slug>/edit/', views.ScreenDesignUpdateView.as_view(), name='screen_design_update'),
    path('designs/<slug:slug>/delete/', views.ScreenDesignDeleteView.as_view(), name='screen_design_delete'),
    path('designs/<slug:slug>/preview/', views.ScreenDesignPreviewView.as_view(), name='screen_design_preview'),
    path('designs/<slug:slug>/save-as-template/', views.save_as_template, name='save_as_template'),

    # =========================================================================
    # VISUAL BUILDER
    # =========================================================================
    path('designs/new/visual/', views.visual_builder_create, name='visual_builder_create'),
    path('designs/<slug:slug>/visual/', views.visual_builder_update, name='visual_builder_update'),
    path('api/visual-builder/save/', views.visual_builder_create_save, name='visual_builder_create_save'),
    path('api/visual-builder/<slug:slug>/save/', views.visual_builder_save, name='visual_builder_save'),
    path('api/components/', views.get_component_registry_api, name='component_registry_api'),

    # =========================================================================
    # TEMPLATES
    # =========================================================================
    path('templates/', views.template_gallery, name='template_gallery'),
    path('templates/<slug:slug>/', views.template_detail, name='template_detail'),
    path('templates/<slug:slug>/preview/', views.template_preview, name='template_preview'),
    path('templates/<slug:slug>/use/', views.create_from_template, name='create_from_template'),
    path('templates/<slug:slug>/edit/', views.template_edit, name='template_edit'),
    path('templates/<slug:slug>/delete/', views.template_delete, name='template_delete'),

    # =========================================================================
    # PLAYLISTS
    # =========================================================================
    path('playlists/', views.PlaylistListView.as_view(), name='playlist_list'),
    path('playlists/create/', views.PlaylistCreateView.as_view(), name='playlist_create'),
    path('playlists/<uuid:pk>/edit/', views.PlaylistUpdateView.as_view(), name='playlist_update'),
    path('playlists/<uuid:pk>/delete/', views.PlaylistDeleteView.as_view(), name='playlist_delete'),

    # =========================================================================
    # DEVICES
    # =========================================================================
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/<uuid:pk>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('devices/<uuid:pk>/delete/', views.DeviceDeleteView.as_view(), name='device_delete'),

    # =========================================================================
    # MEDIA LIBRARY
    # =========================================================================
    path('media-library/', views.MediaAssetListView.as_view(), name='media_list'),

    # =========================================================================
    # PUBLIC PLAYER ENDPOINTS (no authentication)
    # =========================================================================
    path('player/<slug:slug>/', views.screen_player, name='screen_player'),
    path('media/<slug:slug>/', views.media_player, name='media_player'),

    # =========================================================================
    # API ENDPOINTS - Screen Designs
    # =========================================================================
    path('api/designs/<slug:slug>/', views.screen_design_api, name='screen_design_api'),

    # =========================================================================
    # API ENDPOINTS - Device Management (for Fire TV)
    # =========================================================================
    path('api/devices/request-code/', views.device_request_code, name='device_request_code'),
    path('api/devices/<uuid:device_id>/register/', views.device_register, name='device_register'),
    path('api/devices/<uuid:device_id>/config/', views.device_config, name='device_config'),
    path('api/devices/by-code/<str:code>/config/', views.device_config_by_code, name='device_config_by_code'),

    # =========================================================================
    # API ENDPOINTS - Data
    # =========================================================================
    path('api/data/sales/', views.get_sales_data_api, name='get_sales_data_api'),
    path('api/data/variables/', views.get_data_variables_api, name='get_data_variables_api'),
    path('api/data/registry/', views.get_data_registry_api, name='get_data_registry_api'),
    path('api/data/sales/clear-cache/', views.clear_sales_cache_api, name='clear_sales_cache_api'),

    # =========================================================================
    # AJAX ENDPOINTS - Device Registration & Assignment
    # =========================================================================
    path('ajax/devices/register-with-code/', views.register_device_with_code, name='register_device_with_code'),
    path('ajax/devices/<uuid:pk>/assign-content/', views.assign_device_content, name='assign_device_content'),
    path('ajax/devices/<uuid:device_id>/update-group/', views.update_device_group, name='update_device_group'),
    path('ajax/device-groups/create/', views.create_device_group, name='create_device_group'),

    # =========================================================================
    # AJAX ENDPOINTS - Media Library
    # =========================================================================
    path('ajax/media/upload/', views.upload_media, name='upload_media'),
    path('ajax/media/<uuid:media_id>/', views.get_media, name='get_media'),
    path('ajax/media/<uuid:media_id>/update/', views.update_media, name='update_media'),
    path('ajax/media/<uuid:media_id>/delete/', views.delete_media, name='delete_media'),
    path('ajax/folders/create/', views.create_folder, name='create_folder'),

    # =========================================================================
    # AJAX ENDPOINTS - Design Folders
    # =========================================================================
    path('ajax/design-folders/create/', views.create_design_folder, name='create_design_folder'),
    path('ajax/designs/<uuid:design_id>/update-folder/', views.update_design_folder, name='update_design_folder'),

    # =========================================================================
    # FIRE TV APP DOWNLOAD
    # =========================================================================
    path('firetv/', views.firetv_download, name='firetv_download'),
    path('firetv/download/', views.firetv_apk_download, name='firetv_apk_download'),
    path('firetv/upload/', views.firetv_upload_apk, name='firetv_upload_apk'),

    # =========================================================================
    # BACKWARD-COMPATIBLE API ROUTES (Fire TV APKs with /digital-signage/ prefix)
    # =========================================================================
    path('digital-signage/api/devices/request-code/', views.device_request_code, name='device_request_code_compat'),
    path('digital-signage/api/devices/<uuid:device_id>/register/', views.device_register, name='device_register_compat'),
    path('digital-signage/api/devices/<uuid:device_id>/config/', views.device_config, name='device_config_compat'),
    path('digital-signage/api/devices/by-code/<str:code>/config/', views.device_config_by_code, name='device_config_by_code_compat'),

    # =========================================================================
    # DEPRECATED ROUTES (kept for backward compatibility)
    # =========================================================================
    path('play/<slug:slug>/', views.ScreenPlayView.as_view(), name='screen_play'),
    path('dashboard/', views.DisplayDashboardView.as_view(), name='display_dashboard'),
    path('sales/', views.SalesDataListView.as_view(), name='sales_data_list'),
    path('kpi/', views.KPIListView.as_view(), name='kpi_list'),
]
