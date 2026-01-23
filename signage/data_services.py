"""
Data Services for Digital Signage

Provides functions to fetch and cache data from external sources
for use in dynamic screen content.
"""

import logging
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Cache key prefix for sales data
CACHE_PREFIX = 'signage_data'
DEFAULT_CACHE_TIMEOUT = 300  # 5 minutes


def get_sales_data():
    """
    Fetch all sales data from the sales_board_summary table.
    Returns a comprehensive data structure for use in templates.

    Data is cached for 5 minutes (configurable).

    Returns:
        dict: Structured sales data with totals, rankings, and top performers
    """
    cache_key = f'{CACHE_PREFIX}:sales_all'
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        logger.debug("Returning cached sales data")
        return cached_data

    try:
        data = _fetch_sales_data_from_db()
        cache.set(cache_key, data, DEFAULT_CACHE_TIMEOUT)
        logger.info("Sales data fetched and cached")
        return data
    except Exception as e:
        logger.error(f"Error fetching sales data: {e}")
        return _get_empty_sales_data()


def _fetch_sales_data_from_db():
    """
    Fetch sales data directly from the database.
    This is the internal implementation that queries the data_connect database.
    """
    # Check if data_connect database is configured
    if 'data_connect' not in settings.DATABASES:
        logger.warning("data_connect database not configured, returning empty data")
        return _get_empty_sales_data()

    try:
        from .models import SalesBoardSummary

        # Get all store data - use defer() to exclude new target columns that may not exist
        target_fields = [
            'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending',
            'mtd_activations_target', 'mtd_activations_pct_of_target', 'mtd_activations_trending',
            'mtd_smart_return_target', 'mtd_smart_return_pct_of_target', 'mtd_smart_return_trending',
            'mtd_accessories_target', 'mtd_accessories_pct_of_target', 'mtd_accessories_trending',
        ]

        try:
            # First try to get all data including targets
            stores = list(SalesBoardSummary.objects.using('data_connect').all())
            has_target_columns = True
        except Exception as e:
            # If that fails, try without the target columns
            logger.warning(f"Failed to fetch with target columns, trying without: {e}")
            stores = list(SalesBoardSummary.objects.using('data_connect').defer(*target_fields).all())
            has_target_columns = False

        if not stores:
            logger.warning("No sales data found in database")
            return _get_empty_sales_data()

        # Get the current_day_date from any record (should be same for all)
        current_day_date = stores[0].current_day_date if stores else None

        # Build the data structure
        data = {
            'meta': {
                'current_day_date': str(current_day_date) if current_day_date else None,
                'store_count': len(stores),
                'last_updated': str(stores[0].last_updated) if stores and stores[0].last_updated else None,
                'has_target_data': has_target_columns,
            },
            'today': _build_period_data(stores, 'today'),
            'wtd': _build_period_data(stores, 'wtd'),
            'mtd': _build_period_data(stores, 'mtd', has_target_columns),
        }

        return data

    except Exception as e:
        logger.error(f"Database error fetching sales data: {e}")
        return _get_empty_sales_data()


def _build_period_data(stores, period, has_target_columns=False):
    """
    Build data structure for a specific time period (today, wtd, mtd).

    Args:
        stores: List of SalesBoardSummary objects
        period: 'today', 'wtd', or 'mtd'
        has_target_columns: Whether target columns exist in the data

    Returns:
        dict: Period-specific data with totals, rankings, and top performers
    """
    profit_field = f'{period}_profit'
    devices_field = f'{period}_devices_sold'
    invoiced_field = f'{period}_invoiced'
    invoice_count_field = f'{period}_invoice_count'
    device_profit_field = f'{period}_device_profit'

    # Calculate totals
    total_profit = sum((getattr(s, profit_field) or 0) for s in stores)
    total_devices = sum((getattr(s, devices_field) or 0) for s in stores)
    total_invoiced = sum((getattr(s, invoiced_field) or 0) for s in stores)
    total_invoices = sum((getattr(s, invoice_count_field) or 0) for s in stores)
    total_device_profit = sum((getattr(s, device_profit_field) or 0) for s in stores)

    # Sort by profit for rankings
    by_profit = sorted(
        stores,
        key=lambda s: getattr(s, profit_field) or 0,
        reverse=True
    )

    # Sort by devices for rankings
    by_devices = sorted(
        stores,
        key=lambda s: getattr(s, devices_field) or 0,
        reverse=True
    )

    result = {
        'totals': {
            'profit': _format_currency(total_profit),
            'profit_raw': float(total_profit),
            'devices': total_devices,
            'invoiced': _format_currency(total_invoiced),
            'invoiced_raw': float(total_invoiced),
            'invoice_count': total_invoices,
            'device_profit': _format_currency(total_device_profit),
            'device_profit_raw': float(total_device_profit),
        },
        'top5_profit': [
            {
                'rank': i + 1,
                'store_name': s.store_name,
                'value': _format_currency(getattr(s, profit_field) or 0),
                'value_raw': float(getattr(s, profit_field) or 0),
            }
            for i, s in enumerate(by_profit[:5])
        ],
        'top5_devices': [
            {
                'rank': i + 1,
                'store_name': s.store_name,
                'value': getattr(s, devices_field) or 0,
            }
            for i, s in enumerate(by_devices[:5])
        ],
        'top15_profit': [
            {
                'rank': i + 1,
                'store_name': s.store_name,
                'value': _format_currency(getattr(s, profit_field) or 0),
                'value_raw': float(getattr(s, profit_field) or 0),
            }
            for i, s in enumerate(by_profit[:15])
        ],
        'top15_devices': [
            {
                'rank': i + 1,
                'store_name': s.store_name,
                'value': getattr(s, devices_field) or 0,
            }
            for i, s in enumerate(by_devices[:15])
        ],
        'all_profit': [
            {
                'rank': i + 1,
                'store_name': s.store_name,
                'value': _format_currency(getattr(s, profit_field) or 0),
                'value_raw': float(getattr(s, profit_field) or 0),
            }
            for i, s in enumerate(by_profit)
        ],
        'all_devices': [
            {
                'rank': i + 1,
                'store_name': s.store_name,
                'value': getattr(s, devices_field) or 0,
            }
            for i, s in enumerate(by_devices)
        ],
    }

    # Add MTD-specific target data (only if target columns exist)
    if period == 'mtd':
        if has_target_columns:
            try:
                result['targets'] = _build_mtd_targets(stores)
            except Exception as e:
                logger.warning(f"Error building MTD targets: {e}")
                result['targets'] = _get_empty_targets()
        else:
            result['targets'] = _get_empty_targets()

        # Add company-wide totals for percentage of target and trending
        result['totals']['pct_of_target'] = _calculate_company_pct_of_target(stores, has_target_columns)
        result['totals']['pct_of_target_raw'] = _calculate_company_pct_of_target_raw(stores, has_target_columns)
        result['totals']['trending'] = _calculate_company_trending(stores, has_target_columns)

    return result


def _calculate_company_pct_of_target(stores, has_target_columns):
    """Calculate company-wide percentage of device target."""
    if not has_target_columns:
        return "0%"

    try:
        total_actual = sum((getattr(s, 'mtd_devices_sold') or 0) for s in stores)
        total_target = sum((getattr(s, 'mtd_device_target') or 0) for s in stores)

        if total_target > 0:
            pct = (total_actual / total_target) * 100
            return f"{pct:.1f}%"
        return "0%"
    except Exception:
        return "0%"


def _calculate_company_pct_of_target_raw(stores, has_target_columns):
    """Calculate company-wide percentage of device target as raw number."""
    if not has_target_columns:
        return 0.0

    try:
        total_actual = sum((getattr(s, 'mtd_devices_sold') or 0) for s in stores)
        total_target = sum((getattr(s, 'mtd_device_target') or 0) for s in stores)

        if total_target > 0:
            return (total_actual / total_target) * 100
        return 0.0
    except Exception:
        return 0.0


def _calculate_company_trending(stores, has_target_columns):
    """Calculate company-wide trending (sum of all store trending values)."""
    if not has_target_columns:
        return 0

    try:
        total_trending = sum((getattr(s, 'mtd_device_trending') or 0) for s in stores)
        return int(total_trending)
    except Exception:
        return 0


def _get_empty_targets():
    """Return empty target structure when target data is not available."""
    return {
        'devices': {'total_target': 0, 'top5': [], 'top15': [], 'all': [], 'top5_trending': [], 'top10_first': [], 'top10_second': []},
        'activations': {'total_target': 0, 'top5': [], 'top15': [], 'all': []},
        'smart_return': {'total_target': 0, 'top5': [], 'top15': [], 'all': []},
        'accessories': {'total_target': 0, 'top5': [], 'top15': [], 'all': []},
    }


def _format_percentage(value):
    """Format a number as percentage string."""
    if value is None:
        return "0%"
    if isinstance(value, Decimal):
        value = float(value)
    return f"{value:.1f}%"


def _build_mtd_targets(stores):
    """Build MTD target data for devices, activations, smart returns, and accessories."""
    # Calculate totals for each target type
    total_device_target = sum((getattr(s, 'mtd_device_target') or 0) for s in stores)
    total_activations_target = sum((getattr(s, 'mtd_activations_target') or 0) for s in stores)
    total_smart_return_target = sum((getattr(s, 'mtd_smart_return_target') or 0) for s in stores)
    total_accessories_target = sum((getattr(s, 'mtd_accessories_target') or 0) for s in stores)

    # Sort by device % of target (highest first)
    by_device_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_device_target', None)],
        key=lambda s: getattr(s, 'mtd_device_pct_of_target') or 0,
        reverse=True
    )

    # Sort by activations % of target
    by_activations_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_activations_target', None)],
        key=lambda s: getattr(s, 'mtd_activations_pct_of_target') or 0,
        reverse=True
    )

    # Sort by smart return % of target
    by_smart_return_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_smart_return_target', None)],
        key=lambda s: getattr(s, 'mtd_smart_return_pct_of_target') or 0,
        reverse=True
    )

    # Sort by accessories % of target
    by_accessories_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_accessories_target', None)],
        key=lambda s: getattr(s, 'mtd_accessories_pct_of_target') or 0,
        reverse=True
    )

    # Sort by device trending (highest first)
    by_device_trending = sorted(
        [s for s in stores if getattr(s, 'mtd_device_trending', None) is not None],
        key=lambda s: getattr(s, 'mtd_device_trending') or 0,
        reverse=True
    )

    return {
        'devices': {
            'total_target': total_device_target,
            'top5': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'actual': getattr(s, 'mtd_devices_sold') or 0,
                    'target': getattr(s, 'mtd_device_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_device_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_device_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_device_trending') or 0),
                }
                for i, s in enumerate(by_device_pct[:5])
            ],
            'top15': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'actual': getattr(s, 'mtd_devices_sold') or 0,
                    'target': getattr(s, 'mtd_device_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_device_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_device_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_device_trending') or 0),
                }
                for i, s in enumerate(by_device_pct[:15])
            ],
            'all': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'actual': getattr(s, 'mtd_devices_sold') or 0,
                    'target': getattr(s, 'mtd_device_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_device_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_device_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_device_trending') or 0),
                }
                for i, s in enumerate(by_device_pct)
            ],
            'top5_trending': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'actual': getattr(s, 'mtd_devices_sold') or 0,
                    'target': getattr(s, 'mtd_device_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_device_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_device_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_device_trending') or 0),
                }
                for i, s in enumerate(by_device_trending[:5])
            ],
            'top10_first': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'actual': getattr(s, 'mtd_devices_sold') or 0,
                    'target': getattr(s, 'mtd_device_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_device_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_device_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_device_trending') or 0),
                }
                for i, s in enumerate(by_device_pct[:10])
            ],
            'top10_second': [
                {
                    'rank': i + 11,
                    'store_name': s.store_name,
                    'actual': getattr(s, 'mtd_devices_sold') or 0,
                    'target': getattr(s, 'mtd_device_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_device_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_device_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_device_trending') or 0),
                }
                for i, s in enumerate(by_device_pct[10:20])
            ],
        },
        'activations': {
            'total_target': total_activations_target,
            'top5': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_activations_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_activations_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_activations_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_activations_trending') or 0),
                }
                for i, s in enumerate(by_activations_pct[:5])
            ],
            'top15': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_activations_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_activations_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_activations_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_activations_trending') or 0),
                }
                for i, s in enumerate(by_activations_pct[:15])
            ],
            'all': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_activations_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_activations_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_activations_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_activations_trending') or 0),
                }
                for i, s in enumerate(by_activations_pct)
            ],
        },
        'smart_return': {
            'total_target': total_smart_return_target,
            'top5': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_smart_return_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_smart_return_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_smart_return_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_smart_return_trending') or 0),
                }
                for i, s in enumerate(by_smart_return_pct[:5])
            ],
            'top15': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_smart_return_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_smart_return_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_smart_return_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_smart_return_trending') or 0),
                }
                for i, s in enumerate(by_smart_return_pct[:15])
            ],
            'all': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_smart_return_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_smart_return_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_smart_return_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_smart_return_trending') or 0),
                }
                for i, s in enumerate(by_smart_return_pct)
            ],
        },
        'accessories': {
            'total_target': total_accessories_target,
            'top5': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_accessories_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_accessories_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_accessories_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_accessories_trending') or 0),
                }
                for i, s in enumerate(by_accessories_pct[:5])
            ],
            'top15': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_accessories_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_accessories_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_accessories_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_accessories_trending') or 0),
                }
                for i, s in enumerate(by_accessories_pct[:15])
            ],
            'all': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'target': getattr(s, 'mtd_accessories_target') or 0,
                    'pct_of_target': _format_percentage(getattr(s, 'mtd_accessories_pct_of_target')),
                    'pct_of_target_raw': float(getattr(s, 'mtd_accessories_pct_of_target') or 0),
                    'trending': int(getattr(s, 'mtd_accessories_trending') or 0),
                }
                for i, s in enumerate(by_accessories_pct)
            ],
        },
    }


def _format_currency(value):
    """Format a number as currency string."""
    if value is None:
        return "$0"
    if isinstance(value, Decimal):
        value = float(value)
    if value >= 1000:
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def _get_empty_sales_data():
    """Return empty data structure when no data is available."""
    empty_period = {
        'totals': {
            'profit': '$0',
            'profit_raw': 0,
            'devices': 0,
            'invoiced': '$0',
            'invoiced_raw': 0,
            'invoice_count': 0,
            'device_profit': '$0',
            'device_profit_raw': 0,
        },
        'top5_profit': [],
        'top5_devices': [],
        'top15_profit': [],
        'top15_devices': [],
        'all_profit': [],
        'all_devices': [],
    }

    empty_targets = {
        'devices': {'total_target': 0, 'top5': [], 'top15': [], 'all': [], 'top5_trending': [], 'top10_first': [], 'top10_second': []},
        'activations': {'total_target': 0, 'top5': [], 'top15': [], 'all': []},
        'smart_return': {'total_target': 0, 'top5': [], 'top15': [], 'all': []},
        'accessories': {'total_target': 0, 'top5': [], 'top15': [], 'all': []},
    }

    mtd_period = empty_period.copy()
    mtd_period['totals'] = mtd_period['totals'].copy()
    mtd_period['totals']['pct_of_target'] = '0%'
    mtd_period['totals']['pct_of_target_raw'] = 0.0
    mtd_period['totals']['trending'] = 0
    mtd_period['targets'] = empty_targets

    return {
        'meta': {
            'current_day_date': None,
            'store_count': 0,
            'last_updated': None,
        },
        'today': empty_period.copy(),
        'wtd': empty_period.copy(),
        'mtd': mtd_period,
    }


def clear_sales_cache():
    """Clear all cached sales data."""
    cache.delete(f'{CACHE_PREFIX}:sales_all')
    logger.info("Sales data cache cleared")


def get_available_data_variables():
    """
    Get a list of all available data variables for use in screen templates.

    Returns:
        dict: Categorized list of available variables with descriptions
    """
    return {
        'sales': {
            'description': 'Sales data from sales_board_summary (refreshed every 15 minutes)',
            'variables': {
                # Meta
                'sales.meta.current_day_date': 'Date of current day data (may lag by 1 day)',
                'sales.meta.store_count': 'Total number of stores',
                'sales.meta.last_updated': 'When data was last refreshed',

                # Today totals
                'sales.today.totals.profit': 'Today total profit (formatted)',
                'sales.today.totals.devices': 'Today total devices sold',
                'sales.today.totals.invoiced': 'Today total invoiced (formatted)',

                # Today rankings
                'sales.today.top5_profit': 'Top 5 stores by profit today (array)',
                'sales.today.top5_devices': 'Top 5 stores by devices sold today (array)',
                'sales.today.all_profit': 'All stores ranked by profit today (array)',
                'sales.today.all_devices': 'All stores ranked by devices today (array)',

                # WTD totals
                'sales.wtd.totals.profit': 'Week-to-date total profit (formatted)',
                'sales.wtd.totals.devices': 'Week-to-date total devices sold',

                # WTD rankings
                'sales.wtd.top5_profit': 'Top 5 stores by profit WTD (array)',
                'sales.wtd.top5_devices': 'Top 5 stores by devices sold WTD (array)',

                # MTD totals
                'sales.mtd.totals.profit': 'Month-to-date total profit (formatted)',
                'sales.mtd.totals.devices': 'Month-to-date total devices sold',

                # MTD rankings
                'sales.mtd.top5_profit': 'Top 5 stores by profit MTD (array)',
                'sales.mtd.top5_devices': 'Top 5 stores by devices sold MTD (array)',

                # MTD Device Targets
                'sales.mtd.targets.devices.top5': 'Top 5 stores by device % of target (array)',
                'sales.mtd.targets.devices.all': 'All stores ranked by device % of target (array)',
            }
        }
    }
