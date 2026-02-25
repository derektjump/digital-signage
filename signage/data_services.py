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


# =============================================================================
# STORE SALES DATA (sales_board_summary)
# =============================================================================

def get_sales_data(store_id=None):
    """
    Fetch all sales data from the sales_board_summary table.
    Returns a comprehensive data structure for use in templates.

    When store_id is provided, all stores are still included in rankings
    but a 'store' key is added with just that store's data for easy access.

    Data is cached for 5 minutes (configurable).

    Args:
        store_id: Optional store ID to highlight a specific store

    Returns:
        dict: Structured sales data with totals, rankings, and top performers
    """
    cache_key = f'{CACHE_PREFIX}:sales_all'
    cached_data = cache.get(cache_key)

    if cached_data is None:
        try:
            cached_data = _fetch_sales_data_from_db()
            cache.set(cache_key, cached_data, DEFAULT_CACHE_TIMEOUT)
            logger.info("Sales data fetched and cached")
        except Exception as e:
            logger.error(f"Error fetching sales data: {e}")
            cached_data = _get_empty_sales_data()

    # If store_id filter is set, add a 'store' key with that store's data
    if store_id and cached_data:
        cached_data = _add_store_filter(cached_data, store_id)

    return cached_data


def _fetch_sales_data_from_db():
    """
    Fetch sales data directly from the database.
    This is the internal implementation that queries the data_connect database.
    """
    if 'data_connect' not in settings.DATABASES:
        logger.warning("data_connect database not configured, returning empty data")
        return _get_empty_sales_data()

    try:
        from .models import SalesBoardSummary

        # Get all store data - use defer() to exclude target columns that may not exist
        target_fields = [
            'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending',
            'mtd_activations_target', 'mtd_activations_pct_of_target', 'mtd_activations_trending',
            'mtd_smart_return_target', 'mtd_smart_return_pct_of_target', 'mtd_smart_return_trending',
            'mtd_accessories_target', 'mtd_accessories_pct_of_target', 'mtd_accessories_trending',
            'mtd_profit_target', 'mtd_profit_pct_of_target',
            'ly_month_profit', 'ly_month_invoiced', 'ly_month_devices_sold', 'ly_month_device_profit',
        ]

        try:
            stores = list(SalesBoardSummary.objects.using('data_connect').all())
            has_target_columns = True
        except Exception as e:
            logger.warning(f"Failed to fetch with all columns, trying without new columns: {e}")
            stores = list(SalesBoardSummary.objects.using('data_connect').defer(*target_fields).all())
            has_target_columns = False

        if not stores:
            logger.warning("No sales data found in database")
            return _get_empty_sales_data()

        current_day_date = stores[0].current_day_date if stores else None

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
            'prior_year': _build_prior_year_data(stores, has_target_columns),
        }

        return data

    except Exception as e:
        logger.error(f"Database error fetching sales data: {e}")
        return _get_empty_sales_data()


def _build_period_data(stores, period, has_target_columns=False):
    """
    Build data structure for a specific time period (today, wtd, mtd).
    """
    profit_field = f'{period}_profit'
    devices_field = f'{period}_devices_sold'
    invoiced_field = f'{period}_invoiced'
    invoice_count_field = f'{period}_invoice_count'
    device_profit_field = f'{period}_device_profit'

    total_profit = sum((getattr(s, profit_field) or 0) for s in stores)
    total_devices = sum((getattr(s, devices_field) or 0) for s in stores)
    total_invoiced = sum((getattr(s, invoiced_field) or 0) for s in stores)
    total_invoices = sum((getattr(s, invoice_count_field) or 0) for s in stores)
    total_device_profit = sum((getattr(s, device_profit_field) or 0) for s in stores)

    by_profit = sorted(stores, key=lambda s: getattr(s, profit_field) or 0, reverse=True)
    by_devices = sorted(stores, key=lambda s: getattr(s, devices_field) or 0, reverse=True)

    def _store_profit_entry(i, s):
        entry = {
            'rank': i + 1,
            'store_name': s.store_name,
            'store_id': s.store_id,
            'value': _format_currency(getattr(s, profit_field) or 0),
            'value_raw': float(getattr(s, profit_field) or 0),
        }
        # For MTD, include LY and target data per store
        if period == 'mtd' and has_target_columns:
            entry['ly_month_profit'] = _format_currency(getattr(s, 'ly_month_profit', None) or 0)
            entry['ly_month_profit_raw'] = float(getattr(s, 'ly_month_profit', None) or 0)
            entry['profit_target'] = _format_currency(getattr(s, 'mtd_profit_target', None) or 0)
            entry['profit_target_raw'] = float(getattr(s, 'mtd_profit_target', None) or 0)
            entry['profit_pct_of_target'] = _format_percentage(getattr(s, 'mtd_profit_pct_of_target', None))
            entry['profit_pct_of_target_raw'] = float(getattr(s, 'mtd_profit_pct_of_target', None) or 0)
        return entry

    def _store_device_entry(i, s):
        return {
            'rank': i + 1,
            'store_name': s.store_name,
            'store_id': s.store_id,
            'value': getattr(s, devices_field) or 0,
        }

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
        'top5_profit': [_store_profit_entry(i, s) for i, s in enumerate(by_profit[:5])],
        'top5_devices': [_store_device_entry(i, s) for i, s in enumerate(by_devices[:5])],
        'top15_profit': [_store_profit_entry(i, s) for i, s in enumerate(by_profit[:15])],
        'top15_devices': [_store_device_entry(i, s) for i, s in enumerate(by_devices[:15])],
        'all_profit': [_store_profit_entry(i, s) for i, s in enumerate(by_profit)],
        'all_devices': [_store_device_entry(i, s) for i, s in enumerate(by_devices)],
    }

    if period == 'mtd':
        if has_target_columns:
            try:
                result['targets'] = _build_mtd_targets(stores)
            except Exception as e:
                logger.warning(f"Error building MTD targets: {e}")
                result['targets'] = _get_empty_targets()
        else:
            result['targets'] = _get_empty_targets()

        result['totals']['pct_of_target'] = _calculate_company_pct_of_target(stores, has_target_columns)
        result['totals']['pct_of_target_raw'] = _calculate_company_pct_of_target_raw(stores, has_target_columns)
        result['totals']['trending'] = _calculate_company_trending(stores, has_target_columns)

        # Add profit target totals
        if has_target_columns:
            total_profit_target = sum((getattr(s, 'mtd_profit_target', None) or 0) for s in stores)
            result['totals']['profit_target'] = _format_currency(total_profit_target)
            result['totals']['profit_target_raw'] = float(total_profit_target)
            if total_profit_target > 0:
                pct = (float(total_profit) / float(total_profit_target)) * 100
                result['totals']['profit_pct_of_target'] = f"{pct:.1f}%"
                result['totals']['profit_pct_of_target_raw'] = pct
            else:
                result['totals']['profit_pct_of_target'] = "0%"
                result['totals']['profit_pct_of_target_raw'] = 0.0

    return result


def _build_prior_year_data(stores, has_target_columns):
    """Build prior year same month data for all stores."""
    if not has_target_columns:
        return _get_empty_prior_year()

    try:
        total_ly_profit = sum((getattr(s, 'ly_month_profit', None) or 0) for s in stores)
        total_ly_invoiced = sum((getattr(s, 'ly_month_invoiced', None) or 0) for s in stores)
        total_ly_devices = sum((getattr(s, 'ly_month_devices_sold', None) or 0) for s in stores)
        total_ly_device_profit = sum((getattr(s, 'ly_month_device_profit', None) or 0) for s in stores)

        by_ly_profit = sorted(
            stores,
            key=lambda s: getattr(s, 'ly_month_profit', None) or 0,
            reverse=True
        )

        return {
            'totals': {
                'profit': _format_currency(total_ly_profit),
                'profit_raw': float(total_ly_profit),
                'invoiced': _format_currency(total_ly_invoiced),
                'invoiced_raw': float(total_ly_invoiced),
                'devices': total_ly_devices,
                'device_profit': _format_currency(total_ly_device_profit),
                'device_profit_raw': float(total_ly_device_profit),
            },
            'all_profit': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'store_id': s.store_id,
                    'value': _format_currency(getattr(s, 'ly_month_profit', None) or 0),
                    'value_raw': float(getattr(s, 'ly_month_profit', None) or 0),
                }
                for i, s in enumerate(by_ly_profit)
            ],
            'top5_profit': [
                {
                    'rank': i + 1,
                    'store_name': s.store_name,
                    'store_id': s.store_id,
                    'value': _format_currency(getattr(s, 'ly_month_profit', None) or 0),
                    'value_raw': float(getattr(s, 'ly_month_profit', None) or 0),
                }
                for i, s in enumerate(by_ly_profit[:5])
            ],
        }
    except Exception as e:
        logger.warning(f"Error building prior year data: {e}")
        return _get_empty_prior_year()


def _get_empty_prior_year():
    """Return empty prior year structure."""
    return {
        'totals': {
            'profit': '$0', 'profit_raw': 0,
            'invoiced': '$0', 'invoiced_raw': 0,
            'devices': 0,
            'device_profit': '$0', 'device_profit_raw': 0,
        },
        'all_profit': [],
        'top5_profit': [],
    }


def _add_store_filter(data, store_id):
    """
    Add a 'store' key to the data with just the filtered store's metrics.
    Rankings still contain all stores so you can see position.
    The 'store' key gives quick access to the specific store's numbers.
    """
    import copy
    result = copy.deepcopy(data)

    # Find this store in the all_profit rankings for each period
    store_data = {
        'store_id': store_id,
        'store_name': None,
    }

    for period in ['today', 'wtd', 'mtd']:
        period_data = result.get(period, {})
        store_entry = None
        for entry in period_data.get('all_profit', []):
            if entry.get('store_id') == store_id:
                store_entry = entry
                if not store_data['store_name']:
                    store_data['store_name'] = entry.get('store_name')
                break

        if store_entry:
            store_data[period] = {
                'profit': store_entry.get('value', '$0'),
                'profit_raw': store_entry.get('value_raw', 0),
                'rank': store_entry.get('rank', 0),
            }
            # For MTD, include LY and target fields
            if period == 'mtd':
                store_data[period]['ly_month_profit'] = store_entry.get('ly_month_profit', '$0')
                store_data[period]['ly_month_profit_raw'] = store_entry.get('ly_month_profit_raw', 0)
                store_data[period]['profit_target'] = store_entry.get('profit_target', '$0')
                store_data[period]['profit_target_raw'] = store_entry.get('profit_target_raw', 0)
                store_data[period]['profit_pct_of_target'] = store_entry.get('profit_pct_of_target', '0%')
                store_data[period]['profit_pct_of_target_raw'] = store_entry.get('profit_pct_of_target_raw', 0)
        else:
            store_data[period] = {
                'profit': '$0', 'profit_raw': 0, 'rank': 0,
            }

    # Prior year for this store
    prior_year = result.get('prior_year', {})
    ly_entry = None
    for entry in prior_year.get('all_profit', []):
        if entry.get('store_id') == store_id:
            ly_entry = entry
            break
    if ly_entry:
        store_data['prior_year'] = {
            'profit': ly_entry.get('value', '$0'),
            'profit_raw': ly_entry.get('value_raw', 0),
        }
    else:
        store_data['prior_year'] = {'profit': '$0', 'profit_raw': 0}

    result['store'] = store_data
    result['meta']['filtered_store_id'] = store_id
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
    total_device_target = sum((getattr(s, 'mtd_device_target') or 0) for s in stores)
    total_activations_target = sum((getattr(s, 'mtd_activations_target') or 0) for s in stores)
    total_smart_return_target = sum((getattr(s, 'mtd_smart_return_target') or 0) for s in stores)
    total_accessories_target = sum((getattr(s, 'mtd_accessories_target') or 0) for s in stores)

    by_device_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_device_target', None)],
        key=lambda s: getattr(s, 'mtd_device_pct_of_target') or 0,
        reverse=True
    )

    by_activations_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_activations_target', None)],
        key=lambda s: getattr(s, 'mtd_activations_pct_of_target') or 0,
        reverse=True
    )

    by_smart_return_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_smart_return_target', None)],
        key=lambda s: getattr(s, 'mtd_smart_return_pct_of_target') or 0,
        reverse=True
    )

    by_accessories_pct = sorted(
        [s for s in stores if getattr(s, 'mtd_accessories_target', None)],
        key=lambda s: getattr(s, 'mtd_accessories_pct_of_target') or 0,
        reverse=True
    )

    by_device_trending = sorted(
        [s for s in stores if getattr(s, 'mtd_device_trending', None) is not None],
        key=lambda s: getattr(s, 'mtd_device_trending') or 0,
        reverse=True
    )

    def _target_entry(i, s, target_field, pct_field, trending_field=None, actual_field='mtd_devices_sold'):
        entry = {
            'rank': i + 1,
            'store_name': s.store_name,
            'store_id': s.store_id,
            'actual': getattr(s, actual_field) or 0,
            'target': getattr(s, target_field) or 0,
            'pct_of_target': _format_percentage(getattr(s, pct_field)),
            'pct_of_target_raw': float(getattr(s, pct_field) or 0),
        }
        if trending_field:
            entry['trending'] = int(getattr(s, trending_field) or 0)
        return entry

    return {
        'devices': {
            'total_target': total_device_target,
            'top5': [_target_entry(i, s, 'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending') for i, s in enumerate(by_device_pct[:5])],
            'top15': [_target_entry(i, s, 'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending') for i, s in enumerate(by_device_pct[:15])],
            'all': [_target_entry(i, s, 'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending') for i, s in enumerate(by_device_pct)],
            'top5_trending': [_target_entry(i, s, 'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending') for i, s in enumerate(by_device_trending[:5])],
            'top10_first': [_target_entry(i, s, 'mtd_device_target', 'mtd_device_pct_of_target', 'mtd_device_trending') for i, s in enumerate(by_device_pct[:10])],
            'top10_second': [
                {
                    'rank': i + 11,
                    'store_name': s.store_name,
                    'store_id': s.store_id,
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
            'top5': [_target_entry(i, s, 'mtd_activations_target', 'mtd_activations_pct_of_target', 'mtd_activations_trending', 'mtd_devices_sold') for i, s in enumerate(by_activations_pct[:5])],
            'top15': [_target_entry(i, s, 'mtd_activations_target', 'mtd_activations_pct_of_target', 'mtd_activations_trending', 'mtd_devices_sold') for i, s in enumerate(by_activations_pct[:15])],
            'all': [_target_entry(i, s, 'mtd_activations_target', 'mtd_activations_pct_of_target', 'mtd_activations_trending', 'mtd_devices_sold') for i, s in enumerate(by_activations_pct)],
        },
        'smart_return': {
            'total_target': total_smart_return_target,
            'top5': [_target_entry(i, s, 'mtd_smart_return_target', 'mtd_smart_return_pct_of_target', 'mtd_smart_return_trending', 'mtd_devices_sold') for i, s in enumerate(by_smart_return_pct[:5])],
            'top15': [_target_entry(i, s, 'mtd_smart_return_target', 'mtd_smart_return_pct_of_target', 'mtd_smart_return_trending', 'mtd_devices_sold') for i, s in enumerate(by_smart_return_pct[:15])],
            'all': [_target_entry(i, s, 'mtd_smart_return_target', 'mtd_smart_return_pct_of_target', 'mtd_smart_return_trending', 'mtd_devices_sold') for i, s in enumerate(by_smart_return_pct)],
        },
        'accessories': {
            'total_target': total_accessories_target,
            'top5': [_target_entry(i, s, 'mtd_accessories_target', 'mtd_accessories_pct_of_target', 'mtd_accessories_trending', 'mtd_devices_sold') for i, s in enumerate(by_accessories_pct[:5])],
            'top15': [_target_entry(i, s, 'mtd_accessories_target', 'mtd_accessories_pct_of_target', 'mtd_accessories_trending', 'mtd_devices_sold') for i, s in enumerate(by_accessories_pct[:15])],
            'all': [_target_entry(i, s, 'mtd_accessories_target', 'mtd_accessories_pct_of_target', 'mtd_accessories_trending', 'mtd_devices_sold') for i, s in enumerate(by_accessories_pct)],
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
    mtd_period['totals']['profit_target'] = '$0'
    mtd_period['totals']['profit_target_raw'] = 0
    mtd_period['totals']['profit_pct_of_target'] = '0%'
    mtd_period['totals']['profit_pct_of_target_raw'] = 0.0
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
        'prior_year': _get_empty_prior_year(),
    }


def clear_sales_cache():
    """Clear all cached sales data."""
    cache.delete(f'{CACHE_PREFIX}:sales_all')
    logger.info("Sales data cache cleared")


# =============================================================================
# EMPLOYEE SALES DATA (employee_sales_summary)
# =============================================================================

def get_employee_data(store_id=None):
    """
    Fetch employee-level sales data from the employee_sales_summary table.
    Optionally filter by store_id.

    Data is cached for 5 minutes.

    Args:
        store_id: Optional store ID to filter employees by store

    Returns:
        dict: Employee data with per-employee metrics, rankings, and targets
    """
    cache_key = f'{CACHE_PREFIX}:employees:{store_id or "all"}'
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        logger.debug("Returning cached employee data")
        return cached_data

    try:
        data = _fetch_employee_data_from_db(store_id)
        cache.set(cache_key, data, DEFAULT_CACHE_TIMEOUT)
        logger.info(f"Employee data fetched and cached (store_id={store_id})")
        return data
    except Exception as e:
        logger.error(f"Error fetching employee data: {e}")
        return _get_empty_employee_data()


def _fetch_employee_data_from_db(store_id=None):
    """Fetch employee data directly from the database."""
    if 'data_connect' not in settings.DATABASES:
        logger.warning("data_connect database not configured, returning empty employee data")
        return _get_empty_employee_data()

    try:
        from .models import EmployeeSalesSummary, SalesBoardSummary

        qs = EmployeeSalesSummary.objects.using('data_connect')
        filtered_store_name = None

        if store_id:
            # store_id in this table = employee's HOME store, not transaction store.
            # store_name = where the sale actually happened.
            # Look up the store name from SalesBoardSummary to filter by transaction location.
            try:
                store_obj = SalesBoardSummary.objects.using('data_connect').filter(store_id=store_id).first()
                if store_obj:
                    filtered_store_name = store_obj.store_name
                    qs = qs.filter(store_name=filtered_store_name)
                else:
                    qs = qs.filter(store_id=store_id)
            except Exception:
                qs = qs.filter(store_id=store_id)

        all_rows = list(qs.all())

        if not all_rows:
            logger.warning(f"No employee data found (store_id={store_id})")
            return _get_empty_employee_data()

        # Get unique transaction stores from the data
        stores = {}
        for row in all_rows:
            # Use store_name (transaction store) for the store list
            sname = row.store_name
            if sname and sname not in stores.values():
                stores[row.store_id] = sname

        # Group rows by employee.
        # When filtered to a specific store: each employee has one row for that store.
        # When "All": employees may have rows across multiple stores — aggregate them.
        emp_groups = {}
        for row in all_rows:
            key = row.employee_id or row.employee_name
            if key not in emp_groups:
                emp_groups[key] = []
            emp_groups[key].append(row)

        employee_list = []
        for key, rows in emp_groups.items():
            employee_list.append(_build_aggregated_employee_entry(rows))

        # Sort by MTD profit for rankings
        by_mtd_profit = sorted(employee_list, key=lambda e: e['mtd']['profit_raw'], reverse=True)
        by_today_profit = sorted(employee_list, key=lambda e: e['today']['profit_raw'], reverse=True)

        # Add ranks
        for i, emp in enumerate(by_mtd_profit):
            emp['mtd_profit_rank'] = i + 1
        for i, emp in enumerate(by_today_profit):
            emp['today_profit_rank'] = i + 1

        return {
            'meta': {
                'employee_count': len(employee_list),
                'store_count': len(stores),
                'stores': [{'store_id': sid, 'store_name': sname} for sid, sname in sorted(stores.items(), key=lambda x: x[1])],
                'last_updated': str(all_rows[0].last_updated) if all_rows and all_rows[0].last_updated else None,
                'filtered_store_id': store_id,
                'filtered_store_name': filtered_store_name,
            },
            'employees': employee_list,
            'rankings': {
                'by_mtd_profit': [
                    {
                        'rank': i + 1,
                        'employee_name': e['employee_name'],
                        'employee_id': e['employee_id'],
                        'store_name': e['store_name'],
                        'value': e['mtd']['profit'],
                        'value_raw': e['mtd']['profit_raw'],
                    }
                    for i, e in enumerate(by_mtd_profit)
                ],
                'by_today_profit': [
                    {
                        'rank': i + 1,
                        'employee_name': e['employee_name'],
                        'employee_id': e['employee_id'],
                        'store_name': e['store_name'],
                        'value': e['today']['profit'],
                        'value_raw': e['today']['profit_raw'],
                    }
                    for i, e in enumerate(by_today_profit)
                ],
                'top5_mtd_profit': [
                    {
                        'rank': i + 1,
                        'employee_name': e['employee_name'],
                        'employee_id': e['employee_id'],
                        'store_name': e['store_name'],
                        'value': e['mtd']['profit'],
                        'value_raw': e['mtd']['profit_raw'],
                    }
                    for i, e in enumerate(by_mtd_profit[:5])
                ],
                'top5_today_profit': [
                    {
                        'rank': i + 1,
                        'employee_name': e['employee_name'],
                        'employee_id': e['employee_id'],
                        'store_name': e['store_name'],
                        'value': e['today']['profit'],
                        'value_raw': e['today']['profit_raw'],
                    }
                    for i, e in enumerate(by_today_profit[:5])
                ],
            },
        }

    except Exception as e:
        logger.error(f"Database error fetching employee data: {e}")
        return _get_empty_employee_data()


def _build_aggregated_employee_entry(rows):
    """
    Build a single employee data entry by aggregating across store rows.

    Single row (store-filtered): store_name is the transaction store.
    Multiple rows (all stores): aggregate metrics, show home store name.
    """
    primary = rows[0]

    def _sum(field):
        return sum(float(getattr(r, field) or 0) for r in rows)

    def _sum_int(field):
        return sum(int(getattr(r, field) or 0) for r in rows)

    # For display: use the transaction store_name from the row
    # (when filtered, this is the specific store; when aggregated, first row)
    display_store_name = primary.store_name

    total_mtd_profit = _sum('mtd_profit')
    total_today_profit = _sum('today_profit')

    # Targets come from the employee (same across rows), use primary row
    profit_target = float(primary.mtd_profit_target or 0)
    device_target = float(primary.mtd_device_target or 0)

    # Recalculate pct of target from aggregated values
    profit_pct = (total_mtd_profit / profit_target * 100) if profit_target > 0 else 0.0
    total_mtd_devices = _sum_int('mtd_devices_sold')
    device_pct = (total_mtd_devices / device_target * 100) if device_target > 0 else 0.0

    return {
        'employee_id': primary.employee_id,
        'employee_name': primary.employee_name,
        'employee_username': primary.employee_username,
        'store_id': primary.store_id,
        'store_name': display_store_name,
        'today': {
            'profit': _format_currency(total_today_profit),
            'profit_raw': total_today_profit,
            'invoiced': _format_currency(_sum('today_invoiced')),
            'invoiced_raw': _sum('today_invoiced'),
            'invoice_count': _sum_int('today_invoice_count'),
            'devices_sold': _sum_int('today_devices_sold'),
            'device_profit': _format_currency(_sum('today_device_profit')),
            'device_profit_raw': _sum('today_device_profit'),
        },
        'mtd': {
            'profit': _format_currency(total_mtd_profit),
            'profit_raw': total_mtd_profit,
            'invoiced': _format_currency(_sum('mtd_invoiced')),
            'invoiced_raw': _sum('mtd_invoiced'),
            'invoice_count': _sum_int('mtd_invoice_count'),
            'devices_sold': total_mtd_devices,
            'device_profit': _format_currency(_sum('mtd_device_profit')),
            'device_profit_raw': _sum('mtd_device_profit'),
        },
        'targets': {
            'profit_target': _format_currency(profit_target),
            'profit_target_raw': profit_target,
            'profit_pct_of_target': _format_percentage(profit_pct),
            'profit_pct_of_target_raw': profit_pct,
            'device_target': device_target,
            'device_pct_of_target': _format_percentage(device_pct),
            'device_pct_of_target_raw': device_pct,
            'activations_target': float(primary.mtd_activations_target or 0),
            'accessories_target': float(primary.mtd_accessories_target or 0),
            'smart_return_target': float(primary.mtd_smart_return_target or 0),
        },
        'prior_year': {
            'profit': _format_currency(_sum('ly_month_profit')),
            'profit_raw': _sum('ly_month_profit'),
            'invoiced': _format_currency(_sum('ly_month_invoiced')),
            'invoiced_raw': _sum('ly_month_invoiced'),
            'devices_sold': _sum_int('ly_month_devices_sold'),
            'device_profit': _format_currency(_sum('ly_month_device_profit')),
            'device_profit_raw': _sum('ly_month_device_profit'),
        },
    }


def _get_empty_employee_data():
    """Return empty employee data structure."""
    return {
        'meta': {
            'employee_count': 0,
            'store_count': 0,
            'stores': [],
            'last_updated': None,
            'filtered_store_id': None,
            'filtered_store_name': None,
        },
        'employees': [],
        'rankings': {
            'by_mtd_profit': [],
            'by_today_profit': [],
            'top5_mtd_profit': [],
            'top5_today_profit': [],
        },
    }


def clear_employee_cache(store_id=None):
    """Clear cached employee data."""
    if store_id:
        cache.delete(f'{CACHE_PREFIX}:employees:{store_id}')
    else:
        cache.delete(f'{CACHE_PREFIX}:employees:all')
    logger.info(f"Employee data cache cleared (store_id={store_id})")


# =============================================================================
# COMBINED DATA (for screens that need both store + employee)
# =============================================================================

def get_all_data(store_id=None):
    """
    Get both store sales data and employee data in one call.
    Used by the player API for screens that reference both data sets.

    Args:
        store_id: Optional store ID to filter data

    Returns:
        dict: Combined data with 'sales' and 'employees' keys
    """
    return {
        'sales': get_sales_data(store_id=store_id),
        'employees': get_employee_data(store_id=store_id),
    }


# =============================================================================
# UTILITY
# =============================================================================

def get_available_data_variables():
    """
    Get a list of all available data variables for use in screen templates.

    Returns:
        dict: Categorized list of available variables with descriptions
    """
    return {
        'sales': {
            'description': 'Store-level sales data (refreshed every 15 minutes)',
            'variables': {
                'sales.meta.current_day_date': 'Date of current day data',
                'sales.meta.store_count': 'Total number of stores',
                'sales.meta.last_updated': 'When data was last refreshed',
                'sales.today.totals.profit': 'Today total profit (formatted)',
                'sales.today.totals.devices': 'Today total devices sold',
                'sales.today.totals.invoiced': 'Today total invoiced (formatted)',
                'sales.today.top5_profit': 'Top 5 stores by profit today (array)',
                'sales.today.all_profit': 'All stores ranked by profit today (array)',
                'sales.wtd.totals.profit': 'Week-to-date total profit (formatted)',
                'sales.wtd.totals.devices': 'Week-to-date total devices sold',
                'sales.mtd.totals.profit': 'Month-to-date total profit (formatted)',
                'sales.mtd.totals.devices': 'Month-to-date total devices sold',
                'sales.mtd.totals.profit_target': 'Company MTD profit target',
                'sales.mtd.totals.profit_pct_of_target': 'Company MTD profit % of target',
                'sales.mtd.targets.devices.top5': 'Top 5 stores by device % of target (array)',
                'sales.prior_year.totals.profit': 'Prior year same month total profit',
                'sales.prior_year.totals.devices': 'Prior year same month devices sold',
            }
        },
        'employees': {
            'description': 'Employee-level sales data (refreshed every 15 minutes)',
            'variables': {
                'employees.meta.employee_count': 'Total employees in data',
                'employees.meta.stores': 'List of stores with employees (array)',
                'employees.employees': 'All employee records (array)',
                'employees.rankings.by_mtd_profit': 'All employees ranked by MTD profit (array)',
                'employees.rankings.top5_mtd_profit': 'Top 5 employees by MTD profit (array)',
                'employees.rankings.by_today_profit': 'All employees ranked by today profit (array)',
                'employees.rankings.top5_today_profit': 'Top 5 employees by today profit (array)',
            }
        },
    }
