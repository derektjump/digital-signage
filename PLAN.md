# Digital Signage - Feature Roadmap

## Phase 1: Data Foundation

### 1A. Employee-Level Sales Data — ETL COMPLETE
The `employee_sales_summary` table is built and running on a 15-minute Airflow refresh.
Includes: today/MTD metrics, individual targets, target achievement %, prior year same month.
Employee ID mapping: invoice SoldByUserName → EmployeeUsername → EmployeeID.
Device sales assigned to employee's primary store.

### 1B. Prior Year Data — ETL COMPLETE
Both `sales_board_summary` and `employee_sales_summary` now include `ly_month_*` columns
(full prior year same month totals).

### 1C. Store-Level Updates — ETL COMPLETE
`sales_board_summary` now includes `mtd_profit_target` and `mtd_profit_pct_of_target`.

### 1D. Django Integration — IN PROGRESS
- [x] ETL tables exist and are refreshing
- [ ] Update `SalesBoardSummary` model with new LY + profit target columns
- [ ] Create `EmployeeSalesSummary` model (read-only, `managed=False`)
- [ ] Update `DataConnectRouter` for new model
- [ ] Build `get_employee_data(store_id=None)` in `data_services.py`
- [ ] Update `get_sales_data()` to include LY + profit target fields
- [ ] Create `/api/data/employees/` endpoint
- [ ] Register employee fields in `data_registry.py`
- [ ] Wire up store/date filters on ScreenDesign

### Notes
- All date calculations use Mountain Time (America/Regina — no DST)
- Both tables are DROP + RECREATED every 15 min (no schema migrations needed)
- Profit targets currently 0 until configured in iQmetrix
- Employee `employee_id` can be NULL for unmapped employees
- `employee_username` field also available for mapping

---

## Phase 2: User-Friendly Screen Creation (Template-First)

### 2A. Pre-Built Templates (5-10 starter templates)
1. **Staff KPI Card** — Individual employee: LY month profit, MTD profit, target, % to target
2. **Store Dashboard** — Store: LY profit, MTD profit, store target, plus top employees
3. **Staff vs Store Comparison** — Side-by-side: employee metrics vs store metrics
4. **Leaderboard** — Top employees by profit/devices within a store
5. **Announcement Board** — Text/image announcements (no data binding)
6. **Birthday/Recognition** — Employee spotlight with photo and message
7. **Store Target Tracker** — Visual gauges for devices, activations, smart return, accessories
8. **Multi-Metric Dashboard** — Configurable grid of stat cards

### 2B. Template Configuration UI
Instead of code editing, templates have simple forms:
- Dropdown: Pick your store
- Dropdown: Pick employee (filtered by store)
- Color picker: Brand colors
- Text fields: Custom titles, messages
- Image upload: Logo, background, employee photos

### 2C. Improve Template Gallery
- Better preview cards with live data
- Category filtering (KPI, Leaderboard, Announcement, etc.)
- "Use This Template" one-click flow

---

## Phase 3: LLM-Powered Builder (Future)

### 3A. Chat Interface
- Natural language: "Show me John's MTD profit vs his target"
- LLM generates HTML/CSS using brand styles and data variables
- Preview and iterate

### 3B. Pre-programmed Brand Knowledge
- Company colors, fonts, logo
- Standard layouts and component patterns
- Available data variables and their formats
