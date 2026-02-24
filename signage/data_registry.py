"""
Data Field Registry for Screen Builder

Provides a hierarchical structure of all available data fields
with human-readable descriptions for the visual data picker.

Usage:
    from signage.data_registry import DataFieldRegistry

    registry = DataFieldRegistry()
    categories = registry.get_all_categories()
    field = registry.get_field('sales.today.totals.profit')
    json_data = registry.to_json()
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class DataField:
    """Represents a single data field available for templates."""
    path: str  # Full dot-notation path (e.g., 'sales.today.totals.profit')
    name: str  # Human-readable name
    description: str  # Tooltip description
    data_type: str  # 'string', 'number', 'currency', 'percentage', 'array', 'date'
    example: str  # Example value
    is_array: bool = False
    array_item_fields: List['DataField'] = field(default_factory=list)


@dataclass
class DataCategory:
    """Groups related data fields together."""
    key: str  # Category key (e.g., 'sales')
    name: str  # Display name
    description: str
    icon: str  # Material icon name
    fields: List[DataField] = field(default_factory=list)
    subcategories: List['DataCategory'] = field(default_factory=list)


class DataFieldRegistry:
    """
    Central registry of all available data fields for screen templates.

    This is a singleton class that maintains the complete catalog of
    data fields available for use in screen designs.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._categories: Dict[str, DataCategory] = {}
            self._fields: Dict[str, DataField] = {}
            self._register_sales_fields()
            self._initialized = True

    def _register_sales_fields(self):
        """Register all sales-related data fields."""

        # Define ranking item fields (used in profit/devices arrays)
        ranking_fields = [
            DataField('rank', 'Rank', 'Position in ranking (1, 2, 3...)', 'number', '1'),
            DataField('store_name', 'Store Name', 'Name of the store', 'string', 'Store 12'),
            DataField('value', 'Value', 'Formatted value (currency or number)', 'string', '$12,345'),
            DataField('value_raw', 'Raw Value', 'Numeric value for calculations', 'number', '12345.00'),
        ]

        # Target ranking fields include additional target-related data
        target_ranking_fields = [
            DataField('rank', 'Rank', 'Position in ranking', 'number', '1'),
            DataField('store_name', 'Store Name', 'Name of the store', 'string', 'Store 12'),
            DataField('actual', 'Actual', 'Actual count achieved', 'number', '45'),
            DataField('target', 'Target', 'Target count', 'number', '50'),
            DataField('pct_of_target', 'Percent of Target', 'Formatted percentage', 'percentage', '90.0%'),
            DataField('pct_of_target_raw', 'Raw Percent', 'Numeric percentage for calculations', 'number', '90.0'),
            DataField('trending', 'Trending', 'Projected end-of-month value', 'number', '52'),
        ]

        # Build subcategories for each time period
        sales_subcategories = []

        # ========== TODAY ==========
        today_fields = [
            # Totals
            DataField(
                'sales.today.totals.profit',
                'Total Profit',
                'Total profit across all stores today (formatted with $ and commas)',
                'currency', '$58,110'
            ),
            DataField(
                'sales.today.totals.profit_raw',
                'Total Profit (Raw)',
                'Numeric profit value for calculations',
                'number', '58110.00'
            ),
            DataField(
                'sales.today.totals.devices',
                'Devices Sold',
                'Total devices sold across all stores today',
                'number', '234'
            ),
            DataField(
                'sales.today.totals.invoiced',
                'Total Invoiced',
                'Total invoiced amount today (formatted)',
                'currency', '$125,430'
            ),
            DataField(
                'sales.today.totals.invoiced_raw',
                'Total Invoiced (Raw)',
                'Numeric invoiced value for calculations',
                'number', '125430.00'
            ),
            DataField(
                'sales.today.totals.invoice_count',
                'Invoice Count',
                'Number of invoices processed today',
                'number', '89'
            ),
            DataField(
                'sales.today.totals.device_profit',
                'Device Profit',
                'Total profit from device sales today (formatted)',
                'currency', '$15,230'
            ),
            DataField(
                'sales.today.totals.device_profit_raw',
                'Device Profit (Raw)',
                'Numeric device profit for calculations',
                'number', '15230.00'
            ),
            # Rankings - Profit
            DataField(
                'sales.today.top5_profit',
                'Top 5 by Profit',
                'Top 5 stores ranked by profit today',
                'array', '[5 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.today.top15_profit',
                'Top 15 by Profit',
                'Top 15 stores ranked by profit today',
                'array', '[15 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.today.all_profit',
                'All Stores by Profit',
                'All stores ranked by profit today',
                'array', '[All stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            # Rankings - Devices
            DataField(
                'sales.today.top5_devices',
                'Top 5 by Devices',
                'Top 5 stores ranked by devices sold today',
                'array', '[5 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.today.top15_devices',
                'Top 15 by Devices',
                'Top 15 stores ranked by devices sold today',
                'array', '[15 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.today.all_devices',
                'All Stores by Devices',
                'All stores ranked by devices sold today',
                'array', '[All stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
        ]

        for f in today_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='today',
            name='Today',
            description="Today's sales data (may lag by 1 day)",
            icon='calendar_today',
            fields=today_fields
        ))

        # ========== WEEK-TO-DATE ==========
        wtd_fields = [
            # Totals
            DataField(
                'sales.wtd.totals.profit',
                'WTD Total Profit',
                'Week-to-date total profit (formatted)',
                'currency', '$245,890'
            ),
            DataField(
                'sales.wtd.totals.profit_raw',
                'WTD Profit (Raw)',
                'Numeric WTD profit for calculations',
                'number', '245890.00'
            ),
            DataField(
                'sales.wtd.totals.devices',
                'WTD Devices Sold',
                'Week-to-date total devices sold',
                'number', '1,234'
            ),
            DataField(
                'sales.wtd.totals.invoiced',
                'WTD Total Invoiced',
                'Week-to-date invoiced amount (formatted)',
                'currency', '$567,890'
            ),
            DataField(
                'sales.wtd.totals.invoiced_raw',
                'WTD Invoiced (Raw)',
                'Numeric WTD invoiced for calculations',
                'number', '567890.00'
            ),
            DataField(
                'sales.wtd.totals.invoice_count',
                'WTD Invoice Count',
                'Week-to-date number of invoices',
                'number', '456'
            ),
            DataField(
                'sales.wtd.totals.device_profit',
                'WTD Device Profit',
                'Week-to-date device profit (formatted)',
                'currency', '$78,450'
            ),
            DataField(
                'sales.wtd.totals.device_profit_raw',
                'WTD Device Profit (Raw)',
                'Numeric WTD device profit',
                'number', '78450.00'
            ),
            # Rankings
            DataField(
                'sales.wtd.top5_profit',
                'WTD Top 5 by Profit',
                'Top 5 stores by profit week-to-date',
                'array', '[5 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.wtd.top15_profit',
                'WTD Top 15 by Profit',
                'Top 15 stores by profit week-to-date',
                'array', '[15 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.wtd.all_profit',
                'WTD All Stores by Profit',
                'All stores ranked by profit week-to-date',
                'array', '[All stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.wtd.top5_devices',
                'WTD Top 5 by Devices',
                'Top 5 stores by devices sold week-to-date',
                'array', '[5 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.wtd.top15_devices',
                'WTD Top 15 by Devices',
                'Top 15 stores by devices sold week-to-date',
                'array', '[15 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.wtd.all_devices',
                'WTD All Stores by Devices',
                'All stores ranked by devices week-to-date',
                'array', '[All stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
        ]

        for f in wtd_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='wtd',
            name='Week-to-Date',
            description='Week-to-date sales data',
            icon='date_range',
            fields=wtd_fields
        ))

        # ========== MONTH-TO-DATE ==========
        mtd_fields = [
            # Totals
            DataField(
                'sales.mtd.totals.profit',
                'MTD Total Profit',
                'Month-to-date total profit (formatted)',
                'currency', '$1,245,890'
            ),
            DataField(
                'sales.mtd.totals.profit_raw',
                'MTD Profit (Raw)',
                'Numeric MTD profit for calculations',
                'number', '1245890.00'
            ),
            DataField(
                'sales.mtd.totals.devices',
                'MTD Devices Sold',
                'Month-to-date total devices sold',
                'number', '5,234'
            ),
            DataField(
                'sales.mtd.totals.invoiced',
                'MTD Total Invoiced',
                'Month-to-date invoiced amount (formatted)',
                'currency', '$2,567,890'
            ),
            DataField(
                'sales.mtd.totals.invoiced_raw',
                'MTD Invoiced (Raw)',
                'Numeric MTD invoiced for calculations',
                'number', '2567890.00'
            ),
            DataField(
                'sales.mtd.totals.invoice_count',
                'MTD Invoice Count',
                'Month-to-date number of invoices',
                'number', '2,456'
            ),
            DataField(
                'sales.mtd.totals.device_profit',
                'MTD Device Profit',
                'Month-to-date device profit (formatted)',
                'currency', '$378,450'
            ),
            DataField(
                'sales.mtd.totals.device_profit_raw',
                'MTD Device Profit (Raw)',
                'Numeric MTD device profit',
                'number', '378450.00'
            ),
            DataField(
                'sales.mtd.totals.pct_of_target',
                'MTD % of Target',
                'Company-wide percentage of device target achieved',
                'percentage', '87.5%'
            ),
            DataField(
                'sales.mtd.totals.pct_of_target_raw',
                'MTD % of Target (Raw)',
                'Numeric percentage for calculations',
                'number', '87.5'
            ),
            DataField(
                'sales.mtd.totals.trending',
                'MTD Trending',
                'Projected devices at end of month',
                'number', '6,245'
            ),
            # Rankings - Profit
            DataField(
                'sales.mtd.top5_profit',
                'MTD Top 5 by Profit',
                'Top 5 stores by profit month-to-date',
                'array', '[5 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.mtd.top15_profit',
                'MTD Top 15 by Profit',
                'Top 15 stores by profit month-to-date',
                'array', '[15 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.mtd.all_profit',
                'MTD All Stores by Profit',
                'All stores ranked by profit month-to-date',
                'array', '[All stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            # Rankings - Devices
            DataField(
                'sales.mtd.top5_devices',
                'MTD Top 5 by Devices',
                'Top 5 stores by devices sold month-to-date',
                'array', '[5 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.mtd.top15_devices',
                'MTD Top 15 by Devices',
                'Top 15 stores by devices sold month-to-date',
                'array', '[15 stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            DataField(
                'sales.mtd.all_devices',
                'MTD All Stores by Devices',
                'All stores ranked by devices month-to-date',
                'array', '[All stores]',
                is_array=True, array_item_fields=ranking_fields
            ),
            # Target Rankings - Devices
            DataField(
                'sales.mtd.targets.devices.top5',
                'Top 5 by Device % of Target',
                'Top 5 stores by percentage of device target achieved',
                'array', '[5 stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            DataField(
                'sales.mtd.targets.devices.top15',
                'Top 15 by Device % of Target',
                'Top 15 stores by percentage of device target achieved',
                'array', '[15 stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            DataField(
                'sales.mtd.targets.devices.all',
                'All Stores by Device % of Target',
                'All stores ranked by percentage of device target',
                'array', '[All stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            # Target Rankings - Activations
            DataField(
                'sales.mtd.targets.activations.top5',
                'Top 5 by Activation % of Target',
                'Top 5 stores by percentage of activation target achieved',
                'array', '[5 stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            DataField(
                'sales.mtd.targets.activations.all',
                'All Stores by Activation % of Target',
                'All stores ranked by percentage of activation target',
                'array', '[All stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            # Target Rankings - Smart Return
            DataField(
                'sales.mtd.targets.smart_return.top5',
                'Top 5 by Smart Return % of Target',
                'Top 5 stores by percentage of smart return target achieved',
                'array', '[5 stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            DataField(
                'sales.mtd.targets.smart_return.all',
                'All Stores by Smart Return % of Target',
                'All stores ranked by percentage of smart return target',
                'array', '[All stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            # Target Rankings - Accessories
            DataField(
                'sales.mtd.targets.accessories.top5',
                'Top 5 by Accessories % of Target',
                'Top 5 stores by percentage of accessories target achieved',
                'array', '[5 stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
            DataField(
                'sales.mtd.targets.accessories.all',
                'All Stores by Accessories % of Target',
                'All stores ranked by percentage of accessories target',
                'array', '[All stores]',
                is_array=True, array_item_fields=target_ranking_fields
            ),
        ]

        for f in mtd_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='mtd',
            name='Month-to-Date',
            description='Month-to-date sales data with targets',
            icon='calendar_month',
            fields=mtd_fields
        ))

        # ========== META FIELDS ==========
        meta_fields = [
            DataField(
                'sales.meta.current_day_date',
                'Current Day Date',
                'The date used for "today" data (may lag by 1 day)',
                'date', '2026-01-23'
            ),
            DataField(
                'sales.meta.store_count',
                'Store Count',
                'Total number of stores in the data',
                'number', '25'
            ),
            DataField(
                'sales.meta.last_updated',
                'Last Updated',
                'Timestamp when the sales data was last refreshed',
                'date', '2026-01-23T10:30:00'
            ),
            DataField(
                'sales.meta.has_target_data',
                'Has Target Data',
                'Whether target data is available',
                'string', 'true'
            ),
        ]

        for f in meta_fields:
            self._fields[f.path] = f

        # Create main sales category with meta fields and subcategories
        self._categories['sales'] = DataCategory(
            key='sales',
            name='Sales Data',
            description='Sales data from sales_board_summary (refreshed every 15 minutes)',
            icon='point_of_sale',
            fields=meta_fields,
            subcategories=sales_subcategories
        )

    def get_all_categories(self) -> List[DataCategory]:
        """Get all registered data categories."""
        return list(self._categories.values())

    def get_category(self, key: str) -> Optional[DataCategory]:
        """Get a specific category by key."""
        return self._categories.get(key)

    def get_field(self, path: str) -> Optional[DataField]:
        """Get a specific field by its dot-notation path."""
        return self._fields.get(path)

    def get_all_fields(self) -> Dict[str, DataField]:
        """Get all registered fields as a dictionary."""
        return self._fields.copy()

    def get_all_paths(self) -> List[str]:
        """Get a list of all field paths for autocomplete."""
        return list(self._fields.keys())

    def search_fields(self, query: str) -> List[DataField]:
        """Search fields by name, path, or description."""
        query = query.lower()
        results = []
        for field in self._fields.values():
            if (query in field.path.lower() or
                query in field.name.lower() or
                query in field.description.lower()):
                results.append(field)
        return results

    def to_json(self) -> Dict[str, Any]:
        """
        Export registry as JSON for frontend use.

        Returns a structure suitable for building the data picker UI.
        """
        def field_to_dict(f: DataField) -> dict:
            result = {
                'path': f.path,
                'name': f.name,
                'description': f.description,
                'data_type': f.data_type,
                'example': f.example,
                'is_array': f.is_array,
            }
            if f.array_item_fields:
                result['array_item_fields'] = [field_to_dict(af) for af in f.array_item_fields]
            return result

        def category_to_dict(c: DataCategory) -> dict:
            return {
                'key': c.key,
                'name': c.name,
                'description': c.description,
                'icon': c.icon,
                'fields': [field_to_dict(f) for f in c.fields],
                'subcategories': [category_to_dict(sc) for sc in c.subcategories]
            }

        return {
            'categories': [category_to_dict(c) for c in self._categories.values()],
            'all_paths': self.get_all_paths()
        }


# Convenience function for quick access
def get_data_registry() -> DataFieldRegistry:
    """Get the singleton DataFieldRegistry instance."""
    return DataFieldRegistry()
