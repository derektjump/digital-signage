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
            self._register_employee_fields()
            self._initialized = True

    def _register_sales_fields(self):
        """Register all sales-related data fields."""

        # Define ranking item fields (used in profit/devices arrays)
        ranking_fields = [
            DataField('rank', 'Rank', 'Position in ranking (1, 2, 3...)', 'number', '1'),
            DataField('store_name', 'Store Name', 'Name of the store', 'string', 'Store 12'),
            DataField('store_id', 'Store ID', 'Store identifier', 'number', '42'),
            DataField('value', 'Value', 'Formatted value (currency or number)', 'string', '$12,345'),
            DataField('value_raw', 'Raw Value', 'Numeric value for calculations', 'number', '12345.00'),
        ]

        # MTD profit ranking fields include LY and target data
        mtd_profit_ranking_fields = ranking_fields + [
            DataField('ly_month_profit', 'LY Month Profit', 'Prior year same month profit (formatted)', 'currency', '$10,200'),
            DataField('ly_month_profit_raw', 'LY Month Profit (Raw)', 'Prior year profit numeric value', 'number', '10200.00'),
            DataField('profit_target', 'Profit Target', 'Monthly profit target (formatted)', 'currency', '$15,000'),
            DataField('profit_target_raw', 'Profit Target (Raw)', 'Monthly profit target numeric', 'number', '15000.00'),
            DataField('profit_pct_of_target', 'Profit % of Target', 'Percentage of profit target achieved', 'percentage', '82.3%'),
            DataField('profit_pct_of_target_raw', 'Profit % of Target (Raw)', 'Numeric percentage', 'number', '82.3'),
        ]

        # Target ranking fields include additional target-related data
        target_ranking_fields = [
            DataField('rank', 'Rank', 'Position in ranking', 'number', '1'),
            DataField('store_name', 'Store Name', 'Name of the store', 'string', 'Store 12'),
            DataField('store_id', 'Store ID', 'Store identifier', 'number', '42'),
            DataField('actual', 'Actual', 'Actual count achieved', 'number', '45'),
            DataField('target', 'Target', 'Target count', 'number', '50'),
            DataField('pct_of_target', 'Percent of Target', 'Formatted percentage', 'percentage', '90.0%'),
            DataField('pct_of_target_raw', 'Raw Percent', 'Numeric percentage for calculations', 'number', '90.0'),
            DataField('trending', 'Trending', 'Projected end-of-month value', 'number', '52'),
        ]

        sales_subcategories = []

        # ========== TODAY ==========
        today_fields = [
            DataField('sales.today.totals.profit', 'Total Profit', 'Total profit across all stores today (formatted with $ and commas)', 'currency', '$58,110'),
            DataField('sales.today.totals.profit_raw', 'Total Profit (Raw)', 'Numeric profit value for calculations', 'number', '58110.00'),
            DataField('sales.today.totals.devices', 'Devices Sold', 'Total devices sold across all stores today', 'number', '234'),
            DataField('sales.today.totals.invoiced', 'Total Invoiced', 'Total invoiced amount today (formatted)', 'currency', '$125,430'),
            DataField('sales.today.totals.invoiced_raw', 'Total Invoiced (Raw)', 'Numeric invoiced value', 'number', '125430.00'),
            DataField('sales.today.totals.invoice_count', 'Invoice Count', 'Number of invoices processed today', 'number', '89'),
            DataField('sales.today.totals.device_profit', 'Device Profit', 'Total profit from device sales today (formatted)', 'currency', '$15,230'),
            DataField('sales.today.totals.device_profit_raw', 'Device Profit (Raw)', 'Numeric device profit', 'number', '15230.00'),
            DataField('sales.today.top5_profit', 'Top 5 by Profit', 'Top 5 stores ranked by profit today', 'array', '[5 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.today.top15_profit', 'Top 15 by Profit', 'Top 15 stores ranked by profit today', 'array', '[15 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.today.all_profit', 'All Stores by Profit', 'All stores ranked by profit today', 'array', '[All stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.today.top5_devices', 'Top 5 by Devices', 'Top 5 stores ranked by devices sold today', 'array', '[5 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.today.top15_devices', 'Top 15 by Devices', 'Top 15 stores ranked by devices sold today', 'array', '[15 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.today.all_devices', 'All Stores by Devices', 'All stores ranked by devices sold today', 'array', '[All stores]', is_array=True, array_item_fields=ranking_fields),
        ]

        for f in today_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='today', name='Today',
            description="Today's sales data",
            icon='calendar_today', fields=today_fields
        ))

        # ========== WEEK-TO-DATE ==========
        wtd_fields = [
            DataField('sales.wtd.totals.profit', 'WTD Total Profit', 'Week-to-date total profit (formatted)', 'currency', '$245,890'),
            DataField('sales.wtd.totals.profit_raw', 'WTD Profit (Raw)', 'Numeric WTD profit', 'number', '245890.00'),
            DataField('sales.wtd.totals.devices', 'WTD Devices Sold', 'Week-to-date total devices sold', 'number', '1234'),
            DataField('sales.wtd.totals.invoiced', 'WTD Total Invoiced', 'Week-to-date invoiced amount (formatted)', 'currency', '$567,890'),
            DataField('sales.wtd.totals.invoiced_raw', 'WTD Invoiced (Raw)', 'Numeric WTD invoiced', 'number', '567890.00'),
            DataField('sales.wtd.totals.invoice_count', 'WTD Invoice Count', 'Week-to-date number of invoices', 'number', '456'),
            DataField('sales.wtd.totals.device_profit', 'WTD Device Profit', 'Week-to-date device profit (formatted)', 'currency', '$78,450'),
            DataField('sales.wtd.totals.device_profit_raw', 'WTD Device Profit (Raw)', 'Numeric WTD device profit', 'number', '78450.00'),
            DataField('sales.wtd.top5_profit', 'WTD Top 5 by Profit', 'Top 5 stores by profit week-to-date', 'array', '[5 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.wtd.top15_profit', 'WTD Top 15 by Profit', 'Top 15 stores by profit week-to-date', 'array', '[15 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.wtd.all_profit', 'WTD All Stores by Profit', 'All stores ranked by profit week-to-date', 'array', '[All stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.wtd.top5_devices', 'WTD Top 5 by Devices', 'Top 5 stores by devices sold week-to-date', 'array', '[5 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.wtd.top15_devices', 'WTD Top 15 by Devices', 'Top 15 stores by devices sold week-to-date', 'array', '[15 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.wtd.all_devices', 'WTD All Stores by Devices', 'All stores ranked by devices week-to-date', 'array', '[All stores]', is_array=True, array_item_fields=ranking_fields),
        ]

        for f in wtd_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='wtd', name='Week-to-Date',
            description='Week-to-date sales data',
            icon='date_range', fields=wtd_fields
        ))

        # ========== MONTH-TO-DATE ==========
        mtd_fields = [
            DataField('sales.mtd.totals.profit', 'MTD Total Profit', 'Month-to-date total profit (formatted)', 'currency', '$1,245,890'),
            DataField('sales.mtd.totals.profit_raw', 'MTD Profit (Raw)', 'Numeric MTD profit', 'number', '1245890.00'),
            DataField('sales.mtd.totals.devices', 'MTD Devices Sold', 'Month-to-date total devices sold', 'number', '5234'),
            DataField('sales.mtd.totals.invoiced', 'MTD Total Invoiced', 'Month-to-date invoiced amount (formatted)', 'currency', '$2,567,890'),
            DataField('sales.mtd.totals.invoiced_raw', 'MTD Invoiced (Raw)', 'Numeric MTD invoiced', 'number', '2567890.00'),
            DataField('sales.mtd.totals.invoice_count', 'MTD Invoice Count', 'Month-to-date number of invoices', 'number', '2456'),
            DataField('sales.mtd.totals.device_profit', 'MTD Device Profit', 'Month-to-date device profit (formatted)', 'currency', '$378,450'),
            DataField('sales.mtd.totals.device_profit_raw', 'MTD Device Profit (Raw)', 'Numeric MTD device profit', 'number', '378450.00'),
            DataField('sales.mtd.totals.pct_of_target', 'MTD % of Device Target', 'Company-wide percentage of device target achieved', 'percentage', '87.5%'),
            DataField('sales.mtd.totals.pct_of_target_raw', 'MTD % of Device Target (Raw)', 'Numeric percentage', 'number', '87.5'),
            DataField('sales.mtd.totals.trending', 'MTD Trending', 'Projected devices at end of month', 'number', '6245'),
            DataField('sales.mtd.totals.profit_target', 'MTD Profit Target', 'Company-wide monthly profit target (formatted)', 'currency', '$1,500,000'),
            DataField('sales.mtd.totals.profit_target_raw', 'MTD Profit Target (Raw)', 'Numeric profit target', 'number', '1500000.00'),
            DataField('sales.mtd.totals.profit_pct_of_target', 'MTD Profit % of Target', 'Company-wide profit % of target', 'percentage', '83.1%'),
            DataField('sales.mtd.totals.profit_pct_of_target_raw', 'MTD Profit % of Target (Raw)', 'Numeric percentage', 'number', '83.1'),
            # Rankings - MTD profit includes LY and target per store
            DataField('sales.mtd.top5_profit', 'MTD Top 5 by Profit', 'Top 5 stores by profit MTD (includes LY and targets)', 'array', '[5 stores]', is_array=True, array_item_fields=mtd_profit_ranking_fields),
            DataField('sales.mtd.top15_profit', 'MTD Top 15 by Profit', 'Top 15 stores by profit MTD', 'array', '[15 stores]', is_array=True, array_item_fields=mtd_profit_ranking_fields),
            DataField('sales.mtd.all_profit', 'MTD All Stores by Profit', 'All stores ranked by profit MTD', 'array', '[All stores]', is_array=True, array_item_fields=mtd_profit_ranking_fields),
            DataField('sales.mtd.top5_devices', 'MTD Top 5 by Devices', 'Top 5 stores by devices sold MTD', 'array', '[5 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.mtd.top15_devices', 'MTD Top 15 by Devices', 'Top 15 stores by devices sold MTD', 'array', '[15 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.mtd.all_devices', 'MTD All Stores by Devices', 'All stores ranked by devices MTD', 'array', '[All stores]', is_array=True, array_item_fields=ranking_fields),
            # Target Rankings
            DataField('sales.mtd.targets.devices.top5', 'Top 5 by Device % of Target', 'Top 5 stores by percentage of device target', 'array', '[5 stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.devices.top15', 'Top 15 by Device % of Target', 'Top 15 stores by device target %', 'array', '[15 stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.devices.all', 'All by Device % of Target', 'All stores by device target %', 'array', '[All stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.activations.top5', 'Top 5 by Activation % of Target', 'Top 5 stores by activation target %', 'array', '[5 stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.activations.all', 'All by Activation % of Target', 'All stores by activation target %', 'array', '[All stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.smart_return.top5', 'Top 5 by Smart Return % of Target', 'Top 5 stores by smart return target %', 'array', '[5 stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.smart_return.all', 'All by Smart Return % of Target', 'All stores by smart return target %', 'array', '[All stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.accessories.top5', 'Top 5 by Accessories % of Target', 'Top 5 stores by accessories target %', 'array', '[5 stores]', is_array=True, array_item_fields=target_ranking_fields),
            DataField('sales.mtd.targets.accessories.all', 'All by Accessories % of Target', 'All stores by accessories target %', 'array', '[All stores]', is_array=True, array_item_fields=target_ranking_fields),
        ]

        for f in mtd_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='mtd', name='Month-to-Date',
            description='Month-to-date sales data with targets',
            icon='calendar_month', fields=mtd_fields
        ))

        # ========== PRIOR YEAR ==========
        prior_year_fields = [
            DataField('sales.prior_year.totals.profit', 'LY Month Profit', 'Prior year same month total profit (all stores)', 'currency', '$1,100,000'),
            DataField('sales.prior_year.totals.profit_raw', 'LY Month Profit (Raw)', 'Numeric LY profit', 'number', '1100000.00'),
            DataField('sales.prior_year.totals.invoiced', 'LY Month Invoiced', 'Prior year same month invoiced (all stores)', 'currency', '$2,200,000'),
            DataField('sales.prior_year.totals.invoiced_raw', 'LY Month Invoiced (Raw)', 'Numeric LY invoiced', 'number', '2200000.00'),
            DataField('sales.prior_year.totals.devices', 'LY Month Devices', 'Prior year same month devices sold', 'number', '4800'),
            DataField('sales.prior_year.totals.device_profit', 'LY Month Device Profit', 'Prior year device profit (formatted)', 'currency', '$340,000'),
            DataField('sales.prior_year.totals.device_profit_raw', 'LY Month Device Profit (Raw)', 'Numeric LY device profit', 'number', '340000.00'),
            DataField('sales.prior_year.top5_profit', 'LY Top 5 by Profit', 'Top 5 stores by profit last year same month', 'array', '[5 stores]', is_array=True, array_item_fields=ranking_fields),
            DataField('sales.prior_year.all_profit', 'LY All Stores by Profit', 'All stores ranked by profit last year same month', 'array', '[All stores]', is_array=True, array_item_fields=ranking_fields),
        ]

        for f in prior_year_fields:
            self._fields[f.path] = f

        sales_subcategories.append(DataCategory(
            key='prior_year', name='Prior Year (Same Month)',
            description='Last year same month totals for comparison',
            icon='history', fields=prior_year_fields
        ))

        # ========== META FIELDS ==========
        meta_fields = [
            DataField('sales.meta.current_day_date', 'Current Day Date', 'The date used for "today" data', 'date', '2026-02-25'),
            DataField('sales.meta.store_count', 'Store Count', 'Total number of stores in the data', 'number', '25'),
            DataField('sales.meta.last_updated', 'Last Updated', 'Timestamp when sales data was last refreshed', 'date', '2026-02-25T10:30:00'),
            DataField('sales.meta.has_target_data', 'Has Target Data', 'Whether target data is available', 'string', 'true'),
        ]

        for f in meta_fields:
            self._fields[f.path] = f

        self._categories['sales'] = DataCategory(
            key='sales',
            name='Store Sales Data',
            description='Store-level sales data from sales_board_summary (refreshed every 15 minutes)',
            icon='point_of_sale',
            fields=meta_fields,
            subcategories=sales_subcategories
        )

    def _register_employee_fields(self):
        """Register all employee-related data fields."""

        # Employee record fields (each item in the employees array)
        employee_item_fields = [
            DataField('employee_id', 'Employee ID', 'Unique employee identifier', 'number', '1234'),
            DataField('employee_name', 'Employee Name', 'Employee display name', 'string', 'John Smith'),
            DataField('store_name', 'Store Name', 'Store the employee belongs to', 'string', 'Store 12'),
            DataField('store_id', 'Store ID', 'Store identifier', 'number', '42'),
            DataField('today.profit', 'Today Profit', "Employee's profit today (formatted)", 'currency', '$1,250'),
            DataField('today.profit_raw', 'Today Profit (Raw)', 'Numeric profit', 'number', '1250.00'),
            DataField('today.devices_sold', 'Today Devices', 'Devices sold today', 'number', '3'),
            DataField('mtd.profit', 'MTD Profit', "Employee's MTD profit (formatted)", 'currency', '$8,500'),
            DataField('mtd.profit_raw', 'MTD Profit (Raw)', 'Numeric MTD profit', 'number', '8500.00'),
            DataField('mtd.devices_sold', 'MTD Devices', 'Devices sold MTD', 'number', '22'),
            DataField('targets.profit_target', 'Profit Target', 'Monthly profit target (formatted)', 'currency', '$10,000'),
            DataField('targets.profit_pct_of_target', '% of Profit Target', 'Percentage of profit target achieved', 'percentage', '85.0%'),
            DataField('targets.device_target', 'Device Target', 'Monthly device target', 'number', '25'),
            DataField('targets.device_pct_of_target', '% of Device Target', 'Percentage of device target achieved', 'percentage', '88.0%'),
            DataField('prior_year.profit', 'LY Month Profit', 'Prior year same month profit (formatted)', 'currency', '$7,200'),
            DataField('prior_year.profit_raw', 'LY Month Profit (Raw)', 'Numeric LY profit', 'number', '7200.00'),
            DataField('prior_year.devices_sold', 'LY Month Devices', 'Prior year same month devices', 'number', '18'),
        ]

        # Employee ranking fields
        employee_ranking_fields = [
            DataField('rank', 'Rank', 'Position in ranking', 'number', '1'),
            DataField('employee_name', 'Employee Name', 'Employee display name', 'string', 'John Smith'),
            DataField('employee_id', 'Employee ID', 'Unique employee identifier', 'number', '1234'),
            DataField('store_name', 'Store Name', 'Store name', 'string', 'Store 12'),
            DataField('value', 'Value', 'Formatted value', 'string', '$8,500'),
            DataField('value_raw', 'Raw Value', 'Numeric value', 'number', '8500.00'),
        ]

        employee_subcategories = []

        # ========== ALL EMPLOYEES ==========
        all_employee_fields = [
            DataField(
                'employees.employees',
                'All Employees',
                'Complete list of all employees with full metrics (filter by store_id in API call)',
                'array', '[All employees]',
                is_array=True, array_item_fields=employee_item_fields
            ),
        ]

        for f in all_employee_fields:
            self._fields[f.path] = f

        employee_subcategories.append(DataCategory(
            key='all', name='All Employees',
            description='Full employee records with today, MTD, targets, and prior year data',
            icon='people', fields=all_employee_fields
        ))

        # ========== EMPLOYEE RANKINGS ==========
        ranking_fields_list = [
            DataField('employees.rankings.by_mtd_profit', 'All by MTD Profit', 'All employees ranked by MTD profit', 'array', '[All employees]', is_array=True, array_item_fields=employee_ranking_fields),
            DataField('employees.rankings.top5_mtd_profit', 'Top 5 by MTD Profit', 'Top 5 employees by MTD profit', 'array', '[5 employees]', is_array=True, array_item_fields=employee_ranking_fields),
            DataField('employees.rankings.by_today_profit', 'All by Today Profit', 'All employees ranked by today profit', 'array', '[All employees]', is_array=True, array_item_fields=employee_ranking_fields),
            DataField('employees.rankings.top5_today_profit', 'Top 5 by Today Profit', 'Top 5 employees by today profit', 'array', '[5 employees]', is_array=True, array_item_fields=employee_ranking_fields),
        ]

        for f in ranking_fields_list:
            self._fields[f.path] = f

        employee_subcategories.append(DataCategory(
            key='rankings', name='Employee Rankings',
            description='Employee leaderboards by profit',
            icon='leaderboard', fields=ranking_fields_list
        ))

        # ========== EMPLOYEE META ==========
        employee_meta_fields = [
            DataField('employees.meta.employee_count', 'Employee Count', 'Total number of employees in the data', 'number', '150'),
            DataField('employees.meta.store_count', 'Store Count', 'Number of stores with employee data', 'number', '25'),
            DataField('employees.meta.last_updated', 'Last Updated', 'When employee data was last refreshed', 'date', '2026-02-25T10:30:00'),
            DataField('employees.meta.filtered_store_id', 'Filtered Store', 'Store ID filter applied (null if all stores)', 'number', '42'),
        ]

        for f in employee_meta_fields:
            self._fields[f.path] = f

        self._categories['employees'] = DataCategory(
            key='employees',
            name='Employee Sales Data',
            description='Employee-level sales data from employee_sales_summary (refreshed every 15 minutes). Use ?store_id=X to filter by store.',
            icon='badge',
            fields=employee_meta_fields,
            subcategories=employee_subcategories
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
