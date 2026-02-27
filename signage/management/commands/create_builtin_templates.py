"""
Management command to create built-in screen templates.

Usage:
    python manage.py create_builtin_templates
    python manage.py create_builtin_templates --force   # Overwrite existing
"""

from django.core.management.base import BaseCommand
from signage.models import ScreenTemplate


# =============================================================================
# STAFF KPI CARD TEMPLATE
# =============================================================================

STAFF_KPI_HTML = r"""
<div class="staff-kpi-screen">
    <div class="header">
        <img src="/static/signage/img/jump-logo-white.png" class="logo" alt="Jump.ca"
             onerror="this.style.display='none'">
        <div class="header-right">
            <div class="store-name" id="storeName"></div>
            <div class="date-display" id="dateDisplay"></div>
        </div>
    </div>

    <div class="main-content" id="mainContent">
        <div class="employee-header">
            <div class="rank-badge" id="rankBadge">
                <span class="rank-number" id="rankNumber">1</span>
            </div>
            <div class="employee-info">
                <div class="employee-name" id="employeeName">Loading...</div>
                <div class="employee-subtitle" id="employeeSubtitle"></div>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon">&#xe8e5;</div>
                <div class="kpi-label">TODAY'S PROFIT</div>
                <div class="kpi-value" id="todayProfit">$0</div>
                <div class="kpi-details">
                    <span id="todayDevices">0</span> devices &bull;
                    <span id="todayInvoices">0</span> invoices
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-icon">&#xe85c;</div>
                <div class="kpi-label">MTD PROFIT</div>
                <div class="kpi-value" id="mtdProfit">$0</div>
                <div class="kpi-details">
                    <span id="mtdDevices">0</span> devices &bull;
                    <span id="mtdInvoices">0</span> invoices
                </div>
            </div>

            <div class="kpi-card target-card">
                <div class="kpi-icon">&#xe153;</div>
                <div class="kpi-label">PROFIT TARGET</div>
                <div class="kpi-value" id="profitTarget">$0</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="profitProgress"></div>
                </div>
                <div class="kpi-details">
                    <span class="pct-badge" id="profitPctTarget">0%</span> of target
                </div>
            </div>

            <div class="kpi-card target-card">
                <div class="kpi-icon">&#xeb7f;</div>
                <div class="kpi-label">DEVICE TARGET</div>
                <div class="kpi-value" id="deviceActual">0 <span class="target-of">/ <span id="deviceTarget">0</span></span></div>
                <div class="progress-bar">
                    <div class="progress-fill" id="deviceProgress"></div>
                </div>
                <div class="kpi-details">
                    <span class="pct-badge" id="devicePctTarget">0%</span> of target
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-icon">&#xe889;</div>
                <div class="kpi-label">VS LAST YEAR</div>
                <div class="kpi-value" id="lyProfit">$0</div>
                <div class="kpi-details">
                    <span class="ly-change" id="lyChange"></span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-icon">&#xe80b;</div>
                <div class="kpi-label">STORE MTD</div>
                <div class="kpi-value" id="storeProfit">$0</div>
                <div class="kpi-details">
                    Rank <span id="storeRank">#0</span> of <span id="storeCount">0</span>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="employee-counter" id="employeeCounter"></div>
        <div class="last-updated" id="lastUpdated"></div>
    </div>
</div>
"""

STAFF_KPI_CSS = r"""
/* Jump.ca Staff KPI Card Template */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

:root {
    --brand-primary: #00aa90;
    --brand-dark: #003d36;
    --brand-accent: #c850c0;
    --brand-gold: #FFD700;
    --brand-silver: #C0C0C0;
    --brand-bronze: #CD7F32;
    --card-bg: rgba(255, 255, 255, 0.12);
    --card-border: rgba(255, 255, 255, 0.15);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --text-muted: rgba(255, 255, 255, 0.45);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

.staff-kpi-screen {
    width: 1920px;
    height: 1080px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: url('/static/signage/img/brand-bg.png') center/cover no-repeat, #1a1a2e;
    color: var(--text-primary);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

/* Header */
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 30px 50px 20px;
    position: relative;
    z-index: 1;
}

.logo {
    height: 48px;
    opacity: 0.9;
}

.header-right {
    text-align: right;
}

.store-name {
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.date-display {
    font-size: 18px;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Main content */
.main-content {
    flex: 1;
    padding: 10px 50px 0;
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 1;
    opacity: 1;
    transition: opacity 0.5s ease;
}

.main-content.fade-out {
    opacity: 0;
}

/* Employee header section */
.employee-header {
    display: flex;
    align-items: center;
    gap: 30px;
    margin-bottom: 40px;
}

.rank-badge {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--card-bg);
    border: 3px solid var(--card-border);
    flex-shrink: 0;
}

.rank-badge.gold {
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    border-color: #FFD700;
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
}
.rank-badge.gold .rank-number { color: #5a3e00; }

.rank-badge.silver {
    background: linear-gradient(135deg, #E8E8E8 0%, #B0B0B0 100%);
    border-color: #C0C0C0;
    box-shadow: 0 0 30px rgba(192, 192, 192, 0.3);
}
.rank-badge.silver .rank-number { color: #3a3a3a; }

.rank-badge.bronze {
    background: linear-gradient(135deg, #E8A860 0%, #CD7F32 100%);
    border-color: #CD7F32;
    box-shadow: 0 0 30px rgba(205, 127, 50, 0.3);
}
.rank-badge.bronze .rank-number { color: #4a2800; }

.rank-number {
    font-size: 38px;
    font-weight: 800;
    line-height: 1;
}

.employee-name {
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.1;
}

.employee-subtitle {
    font-size: 20px;
    color: var(--text-secondary);
    margin-top: 6px;
    font-weight: 500;
}

/* KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: 20px;
    flex: 1;
}

.kpi-card {
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 28px 32px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--brand-primary), var(--brand-accent));
    opacity: 0.6;
}

.kpi-icon {
    font-family: 'Material Icons';
    font-size: 32px;
    color: #fff;
    margin-bottom: 12px;
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.22);
    border-radius: 16px;
}

.kpi-label {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 12px;
}

.kpi-value {
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.1;
}

.target-of {
    font-size: 30px;
    font-weight: 500;
    color: var(--text-secondary);
}

.kpi-details {
    font-size: 20px;
    color: var(--text-secondary);
    margin-top: 12px;
    font-weight: 500;
}

/* Progress bars */
.progress-bar {
    width: 100%;
    height: 10px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 5px;
    margin-top: 16px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--brand-primary), var(--brand-accent));
    transition: width 1s ease;
    min-width: 0;
}

/* Percentage badge */
.pct-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 14px;
    font-size: 20px;
    font-weight: 700;
}

.pct-badge.on-track {
    background: rgba(0, 170, 144, 0.2);
    color: #00ddb3;
}

.pct-badge.behind {
    background: rgba(255, 107, 107, 0.2);
    color: #ff8a8a;
}

.pct-badge.ahead {
    background: rgba(0, 170, 144, 0.3);
    color: #00ffcc;
}

/* LY comparison */
.ly-change {
    font-weight: 700;
}

.ly-change.positive {
    color: #00ddb3;
}

.ly-change.negative {
    color: #ff8a8a;
}

/* Footer */
.footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 50px 24px;
    position: relative;
    z-index: 1;
}

.employee-counter {
    font-size: 18px;
    color: var(--text-muted);
    font-weight: 500;
}

.last-updated {
    font-size: 16px;
    color: var(--text-muted);
}

/* Dot indicators */
.dot-indicators {
    display: flex;
    gap: 8px;
    margin-left: 16px;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
}

.dot.active {
    background: var(--brand-primary);
    box-shadow: 0 0 8px rgba(0, 170, 144, 0.5);
    width: 24px;
    border-radius: 4px;
}

/* Responsive scaling for non-1920 screens */
@media (max-width: 1920px) {
    .staff-kpi-screen {
        transform-origin: top left;
    }
}
"""

STAFF_KPI_JS = r"""
(function() {
    var employees = [];
    var currentIndex = 0;
    var rotationTimer = null;
    var dataLoaded = false;
    var firstRender = true;
    // Use page_duration from design config if set, otherwise default to 5 seconds
    var ROTATION_INTERVAL = (window.designConfig && window.designConfig.page_duration)
        ? window.designConfig.page_duration * 1000
        : 5000;

    // Load required fonts dynamically
    ['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
     'https://fonts.googleapis.com/icon?family=Material+Icons'].forEach(function(url) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        document.head.appendChild(link);
    });

    // Wait for data to load
    window.addEventListener('signageDataLoaded', function() {
        updateStoreInfo();
    });

    window.addEventListener('employeeDataLoaded', function(e) {
        dataLoaded = true;
        var data = window.employeeData;
        if (data && data.employees && data.employees.length > 0) {
            employees = data.employees;
            // Sort by MTD profit (highest first)
            employees.sort(function(a, b) {
                return (b.mtd.profit_raw || 0) - (a.mtd.profit_raw || 0);
            });
            showEmployee(0);
            startRotation();
        } else {
            showNoData();
        }
    });

    // Fallback: if no data after 10 seconds, show message
    setTimeout(function() {
        if (!dataLoaded) showNoData();
    }, 10000);

    function showNoData() {
        var nameEl = document.getElementById('employeeName');
        var subEl = document.getElementById('employeeSubtitle');
        var badge = document.getElementById('rankBadge');
        if (nameEl) nameEl.textContent = 'No Employee Data';
        if (subEl) subEl.textContent = 'Employee data is not yet available. The ETL pipeline may still be setting up.';
        if (badge) badge.style.display = 'none';
    }

    function updateStoreInfo() {
        var sales = window.signageData;
        if (!sales) return;

        // Store name from store filter
        var storeName = '';
        if (sales.store && sales.store.store_name) {
            storeName = sales.store.store_name;
        }
        var el = document.getElementById('storeName');
        if (el) el.textContent = storeName;

        // Date
        var dateEl = document.getElementById('dateDisplay');
        if (dateEl && sales.meta && sales.meta.current_day_date) {
            var d = new Date(sales.meta.current_day_date + 'T00:00:00');
            dateEl.textContent = d.toLocaleDateString('en-US', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            });
        }

        // Store count
        var storeCountEl = document.getElementById('storeCount');
        if (storeCountEl && sales.meta) {
            storeCountEl.textContent = sales.meta.store_count || 0;
        }

        // Store MTD profit and rank
        if (sales.store) {
            var sp = document.getElementById('storeProfit');
            if (sp) sp.textContent = (sales.store.mtd && sales.store.mtd.profit) || '$0';

            var sr = document.getElementById('storeRank');
            if (sr) sr.textContent = '#' + ((sales.store.mtd && sales.store.mtd.rank) || 0);
        }

        // Last updated
        var luEl = document.getElementById('lastUpdated');
        if (luEl && sales.meta && sales.meta.last_updated) {
            var ts = new Date(sales.meta.last_updated);
            luEl.textContent = 'Updated ' + ts.toLocaleTimeString('en-US', {
                hour: 'numeric', minute: '2-digit'
            });
        }
    }

    function showEmployee(index) {
        if (employees.length === 0) return;
        var wrappedIndex = index % employees.length;
        // Signal cycle complete when we wrap back to the first employee
        if (index > 0 && wrappedIndex === 0) {
            window.signageCycleComplete = true;
        }
        currentIndex = wrappedIndex;
        var emp = employees[currentIndex];

        var content = document.getElementById('mainContent');

        // First render: populate immediately without fade animation
        if (firstRender) {
            firstRender = false;
            populateEmployee(emp);
            return;
        }

        // Subsequent renders: fade out, update, fade in
        content.classList.add('fade-out');

        setTimeout(function() {
            populateEmployee(emp);
            content.classList.remove('fade-out');
        }, 500);
    }

    function populateEmployee(emp) {
        setText('employeeName', emp.employee_name || 'Unknown');
        setText('employeeSubtitle', emp.store_name || '');

        // Rank badge (MTD profit rank)
        var rank = currentIndex + 1;
        var badge = document.getElementById('rankBadge');
        var rankNum = document.getElementById('rankNumber');
        if (badge && rankNum) {
            rankNum.textContent = rank;
            badge.className = 'rank-badge';
            if (rank === 1) badge.classList.add('gold');
            else if (rank === 2) badge.classList.add('silver');
            else if (rank === 3) badge.classList.add('bronze');
        }

        // Today
        setText('todayProfit', emp.today.profit || '$0');
        setText('todayDevices', emp.today.devices_sold || 0);
        setText('todayInvoices', emp.today.invoice_count || 0);

        // MTD
        setText('mtdProfit', emp.mtd.profit || '$0');
        setText('mtdDevices', emp.mtd.devices_sold || 0);
        setText('mtdInvoices', emp.mtd.invoice_count || 0);

        // Profit target
        setText('profitTarget', emp.targets.profit_target || '$0');
        var profitPct = emp.targets.profit_pct_of_target_raw || 0;
        setProgress('profitProgress', profitPct);
        setPctBadge('profitPctTarget', profitPct);

        // Device target
        var da = document.getElementById('deviceActual');
        if (da) {
            var devSold = emp.mtd.devices_sold || 0;
            var devTarget = Math.round(emp.targets.device_target || 0);
            da.innerHTML = devSold + ' <span class="target-of">/ <span id="deviceTarget">' + devTarget + '</span></span>';
        }
        var devicePct = emp.targets.device_pct_of_target_raw || 0;
        setProgress('deviceProgress', devicePct);
        setPctBadge('devicePctTarget', devicePct);

        // Prior year comparison
        setText('lyProfit', emp.prior_year.profit || '$0');
        var lyChange = document.getElementById('lyChange');
        if (lyChange) {
            var mtdRaw = emp.mtd.profit_raw || 0;
            var lyRaw = emp.prior_year.profit_raw || 0;
            if (lyRaw > 0) {
                var changePct = ((mtdRaw - lyRaw) / lyRaw) * 100;
                var sign = changePct >= 0 ? '+' : '';
                lyChange.textContent = sign + changePct.toFixed(1) + '% vs LY';
                lyChange.className = 'ly-change ' + (changePct >= 0 ? 'positive' : 'negative');
            } else {
                lyChange.textContent = 'No LY data';
                lyChange.className = 'ly-change';
            }
        }

        updateStoreInfo();

        var counter = document.getElementById('employeeCounter');
        if (counter) {
            counter.textContent = (currentIndex + 1) + ' of ' + employees.length;
        }
    }

    function startRotation() {
        if (rotationTimer) clearInterval(rotationTimer);
        if (employees.length <= 1) return;

        rotationTimer = setInterval(function() {
            showEmployee(currentIndex + 1);
        }, ROTATION_INTERVAL);
    }

    function setText(id, value) {
        var el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    function setProgress(id, pct) {
        var el = document.getElementById(id);
        if (el) {
            var clamped = Math.min(Math.max(pct, 0), 100);
            el.style.width = clamped + '%';
        }
    }

    function setPctBadge(id, pct) {
        var el = document.getElementById(id);
        if (el) {
            el.textContent = pct.toFixed(1) + '%';
            el.className = 'pct-badge';
            if (pct >= 100) el.classList.add('ahead');
            else if (pct >= 70) el.classList.add('on-track');
            else el.classList.add('behind');
        }
    }
})();
"""

# =============================================================================
# STORE LEADERBOARD TEMPLATE
# =============================================================================

STORE_LEADERBOARD_HTML = r"""
<div class="leaderboard-screen">
    <div class="header">
        <img src="/static/signage/img/jump-logo-white.png" class="logo" alt="Jump.ca"
             onerror="this.style.display='none'">
        <div class="header-center">
            <div class="title" id="boardTitle">MTD STORE LEADERBOARD</div>
            <div class="subtitle" id="boardSubtitle"></div>
        </div>
        <div class="header-right">
            <div class="company-total" id="companyTotal">$0</div>
            <div class="company-label">COMPANY TOTAL</div>
        </div>
    </div>

    <div class="board-container" id="boardContainer">
        <!-- Rows are generated by JS -->
    </div>

    <div class="footer">
        <div class="page-indicator" id="pageIndicator"></div>
        <div class="last-updated" id="lastUpdated"></div>
    </div>
</div>
"""

STORE_LEADERBOARD_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --brand-primary: #00aa90;
    --brand-dark: #003d36;
    --brand-accent: #c850c0;
    --brand-gold: #FFD700;
    --brand-silver: #C0C0C0;
    --brand-bronze: #CD7F32;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

.leaderboard-screen {
    width: 1920px;
    height: 1080px;
    font-family: 'Inter', sans-serif;
    background: url('/static/signage/img/brand-bg.png') center/cover no-repeat, #1a1a2e;
    color: #fff;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 50px 20px;
    position: relative;
    z-index: 1;
}

.logo { height: 44px; opacity: 0.9; }

.header-center { text-align: center; }

.title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 3px;
}

.subtitle {
    font-size: 15px;
    color: rgba(255,255,255,0.6);
    margin-top: 4px;
}

.header-right { text-align: right; }

.company-total {
    font-size: 32px;
    font-weight: 800;
    color: var(--brand-primary);
}

.company-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.5);
    margin-top: 2px;
}

.board-container {
    flex: 1;
    padding: 10px 50px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    opacity: 1;
    transition: opacity 0.4s ease;
    position: relative;
    z-index: 1;
}

.board-container.fade-out { opacity: 0; }

/* Leaderboard row */
.lb-row {
    display: grid;
    grid-template-columns: 70px 1fr 320px 200px 160px;
    align-items: center;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 24px;
    gap: 16px;
    flex: 1;
}

.lb-row.top-3 {
    background: rgba(255,255,255,0.1);
    border-color: rgba(255,255,255,0.15);
}

.lb-rank {
    font-size: 26px;
    font-weight: 800;
    text-align: center;
}

.lb-rank.gold { color: var(--brand-gold); }
.lb-rank.silver { color: var(--brand-silver); }
.lb-rank.bronze { color: var(--brand-bronze); }

.lb-name {
    font-size: 22px;
    font-weight: 700;
}

.lb-value {
    font-size: 24px;
    font-weight: 800;
    text-align: right;
}

.lb-secondary {
    font-size: 18px;
    font-weight: 600;
    text-align: right;
    color: rgba(255,255,255,0.6);
}

.lb-pct {
    text-align: right;
    font-size: 18px;
    font-weight: 700;
}

.lb-pct.on-track { color: #00ddb3; }
.lb-pct.behind { color: #ff8a8a; }
.lb-pct.ahead { color: #00ffcc; }

.lb-value-group {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 12px;
}

.lb-change {
    font-size: 16px;
    font-weight: 700;
}

.lb-change.positive { color: #00ddb3; }
.lb-change.negative { color: #ff8a8a; }

.lb-header {
    display: grid;
    grid-template-columns: 70px 1fr 320px 200px 160px;
    padding: 0 24px 6px;
    gap: 16px;
}

.lb-header span {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
}

.lb-header span:nth-child(n+3) { text-align: right; }

.footer {
    display: flex;
    justify-content: space-between;
    padding: 12px 50px 24px;
    position: relative;
    z-index: 1;
}

.page-indicator, .last-updated {
    font-size: 13px;
    color: rgba(255,255,255,0.35);
}
"""

STORE_LEADERBOARD_JS = r"""
(function() {
    var ROWS_PER_PAGE = 10;
    // Use page_duration from design config if set, otherwise default to 10 seconds
    var PAGE_INTERVAL = (window.designConfig && window.designConfig.page_duration)
        ? window.designConfig.page_duration * 1000
        : 10000;
    var stores = [];
    var currentPage = 0;
    var totalPages = 1;
    var pageTimer = null;
    var firstRender = true;

    // Load required fonts dynamically
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap';
    document.head.appendChild(link);

    window.addEventListener('signageDataLoaded', function() {
        var sales = window.signageData;
        if (!sales) return;

        stores = sales.mtd.all_profit || [];
        totalPages = Math.ceil(stores.length / ROWS_PER_PAGE);

        // Set header
        var dateEl = document.getElementById('boardSubtitle');
        if (dateEl && sales.meta && sales.meta.current_day_date) {
            var d = new Date(sales.meta.current_day_date + 'T00:00:00');
            dateEl.textContent = d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        }

        setText('companyTotal', sales.mtd.totals.profit || '$0');

        var luEl = document.getElementById('lastUpdated');
        if (luEl && sales.meta && sales.meta.last_updated) {
            var ts = new Date(sales.meta.last_updated);
            luEl.textContent = 'Updated ' + ts.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        }

        showPage(0);
        if (totalPages > 1) startPaging();
    });

    function showPage(page) {
        // Signal cycle complete when we wrap back to the first page
        if (page > 0 && page % totalPages === 0) {
            window.signageCycleComplete = true;
        }
        currentPage = page % totalPages;
        var container = document.getElementById('boardContainer');

        if (firstRender) {
            firstRender = false;
            populatePage(container);
            return;
        }

        container.classList.add('fade-out');
        setTimeout(function() {
            populatePage(container);
            container.classList.remove('fade-out');
        }, 400);
    }

    function populatePage(container) {
        container.innerHTML = '';

        // Column header
        var header = document.createElement('div');
        header.className = 'lb-header';
        header.innerHTML = '<span>RANK</span><span>STORE</span><span>MTD PROFIT</span><span>LY PROFIT</span><span>% TARGET</span>';
        container.appendChild(header);

        var start = currentPage * ROWS_PER_PAGE;
        var pageStores = stores.slice(start, start + ROWS_PER_PAGE);

        pageStores.forEach(function(store, i) {
            var rank = start + i + 1;
            var row = document.createElement('div');
            row.className = 'lb-row' + (rank <= 3 ? ' top-3' : '');

            var rankClass = rank === 1 ? 'gold' : rank === 2 ? 'silver' : rank === 3 ? 'bronze' : '';
            var pctRaw = store.profit_pct_of_target_raw || 0;
            var pctClass = pctRaw >= 100 ? 'ahead' : pctRaw >= 70 ? 'on-track' : 'behind';
            var pctText = store.profit_pct_of_target || '0%';

            // Calculate MTD vs LY % change
            var mtdRaw = store.value_raw || 0;
            var lyRaw = store.ly_month_profit_raw || 0;
            var vsLyText = '--';
            var vsLyClass = '';
            if (lyRaw > 0) {
                var changePct = ((mtdRaw - lyRaw) / lyRaw) * 100;
                vsLyText = (changePct >= 0 ? '+' : '') + changePct.toFixed(0) + '%';
                vsLyClass = changePct >= 0 ? 'positive' : 'negative';
            } else if (mtdRaw > 0) {
                vsLyText = '+100%';
                vsLyClass = 'positive';
            }

            row.innerHTML =
                '<div class="lb-rank ' + rankClass + '">' + rank + '</div>' +
                '<div class="lb-name">' + (store.store_name || '') + '</div>' +
                '<div class="lb-value-group"><span class="lb-value">' + (store.value || '$0') + '</span><span class="lb-change ' + vsLyClass + '">' + vsLyText + '</span></div>' +
                '<div class="lb-secondary">' + (store.ly_month_profit || '$0') + '</div>' +
                '<div class="lb-pct ' + pctClass + '">' + pctText + '</div>';

            container.appendChild(row);
        });

        var pi = document.getElementById('pageIndicator');
        if (pi && totalPages > 1) {
            pi.textContent = 'Page ' + (currentPage + 1) + ' of ' + totalPages;
        }
    }

    function startPaging() {
        if (pageTimer) clearInterval(pageTimer);
        pageTimer = setInterval(function() {
            showPage(currentPage + 1);
        }, PAGE_INTERVAL);
    }

    function setText(id, value) {
        var el = document.getElementById(id);
        if (el) el.textContent = value;
    }
})();
"""


# =============================================================================
# STORE TOP PERFORMERS TEMPLATE
# =============================================================================

STORE_TOP_PERFORMERS_HTML = r"""
<div class="top-performers-screen">
    <div class="header">
        <img src="/static/signage/img/jump-logo-white.png" class="logo" alt="Jump.ca"
             onerror="this.style.display='none'">
        <div class="header-center">
            <div class="title" id="storeName">STORE TOP PERFORMERS</div>
            <div class="subtitle" id="dateDisplay"></div>
        </div>
        <div class="header-right">
            <div class="last-updated" id="lastUpdated"></div>
        </div>
    </div>

    <div class="grid-container" id="gridContainer">
        <!-- Column Headers -->
        <div class="grid-header">
            <div class="col-category">CATEGORY</div>
            <div class="col-employee">TOP PERFORMER</div>
            <div class="col-staff">STAFF</div>
            <div class="col-store">STORE</div>
        </div>

        <!-- Row 1: Last Year Month -->
        <div class="grid-row" id="rowLY">
            <div class="col-category">
                <div class="category-icon ly"><span class="material-icons">history</span></div>
                <div class="category-label">LAST YEAR<br>MONTH TOTAL</div>
            </div>
            <div class="col-employee">
                <div class="emp-name" id="lyName">--</div>
            </div>
            <div class="col-staff">
                <div class="metric-value" id="lyStaffValue">$0</div>
            </div>
            <div class="col-store">
                <div class="metric-value store-value" id="lyStoreValue">$0</div>
            </div>
        </div>

        <!-- Row 2: MTD -->
        <div class="grid-row" id="rowMTD">
            <div class="col-category">
                <div class="category-icon mtd"><span class="material-icons">trending_up</span></div>
                <div class="category-label">MONTH<br>TO DATE</div>
            </div>
            <div class="col-employee">
                <div class="emp-name" id="mtdName">--</div>
            </div>
            <div class="col-staff">
                <div class="metric-value" id="mtdStaffValue">$0</div>
            </div>
            <div class="col-store">
                <div class="metric-value store-value" id="mtdStoreValue">$0</div>
            </div>
        </div>

        <!-- Row 3: Target -->
        <div class="grid-row" id="rowTarget">
            <div class="col-category">
                <div class="category-icon target"><span class="material-icons">flag</span></div>
                <div class="category-label">PROFIT<br>TARGET</div>
            </div>
            <div class="col-employee">
                <div class="emp-name" id="targetName">--</div>
            </div>
            <div class="col-staff">
                <div class="metric-value" id="targetStaffValue">$0</div>
                <div class="metric-sub" id="targetStaffPct"></div>
            </div>
            <div class="col-store">
                <div class="metric-value store-value" id="targetStoreValue">$0</div>
                <div class="metric-sub" id="targetStorePct"></div>
            </div>
        </div>
    </div>

    <!-- Bottom sections -->
    <div class="bottom-sections">
        <!-- 2nd Place Runner-Up -->
        <div class="bottom-card" id="runnerUpSection">
            <div class="bottom-label">RUNNER UP &mdash; MONTH TO DATE</div>
            <div class="bottom-content">
                <div class="bottom-name" id="runnerUpName">--</div>
                <div class="bottom-value" id="runnerUpValue">$0</div>
                <div class="bottom-detail" id="runnerUpGap"></div>
            </div>
        </div>

        <!-- Store Company Rank -->
        <div class="bottom-card" id="companyRankSection">
            <div class="bottom-label">STORE RANKING</div>
            <div class="bottom-content">
                <div class="bottom-name" id="companyRankText">--</div>
                <div class="bottom-value" id="companyRankProfit">$0</div>
                <div class="bottom-detail" id="companyRankDetail">MTD Profit</div>
            </div>
        </div>

        <!-- Top Employee Company-Wide -->
        <div class="bottom-card" id="topCompanyEmpSection">
            <div class="bottom-label">TOP IN COMPANY &mdash; MTD PROFIT</div>
            <div class="bottom-content">
                <div class="bottom-name" id="topCompanyEmpName">--</div>
                <div class="bottom-value" id="topCompanyEmpValue">$0</div>
                <div class="bottom-detail" id="topCompanyEmpStore"></div>
            </div>
        </div>

        <!-- Top Store Company-Wide -->
        <div class="bottom-card" id="topCompanyStoreSection">
            <div class="bottom-label">TOP STORE &mdash; MTD PROFIT</div>
            <div class="bottom-content">
                <div class="bottom-name" id="topCompanyStoreName">--</div>
                <div class="bottom-value" id="topCompanyStoreValue">$0</div>
                <div class="bottom-detail" id="topCompanyStoreDetail"></div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="employee-count" id="employeeCount"></div>
        <div class="last-updated" id="lastUpdated2"></div>
    </div>
</div>
"""

STORE_TOP_PERFORMERS_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

:root {
    --brand-primary: #00aa90;
    --brand-dark: #003d36;
    --brand-accent: #c850c0;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

.top-performers-screen {
    width: 1920px;
    height: 1080px;
    font-family: 'Inter', sans-serif;
    background: url('/static/signage/img/brand-bg.png') center/cover no-repeat, #1a1a2e;
    color: #fff;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 30px 50px 20px;
    position: relative;
    z-index: 1;
}

.logo { height: 44px; opacity: 0.9; }

.header-center { text-align: center; }

.title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 3px;
}

.subtitle {
    font-size: 15px;
    color: rgba(255,255,255,0.6);
    margin-top: 4px;
}

.header-right { text-align: right; }

.last-updated {
    font-size: 13px;
    color: rgba(255,255,255,0.4);
}

/* Grid Container */
.grid-container {
    flex: 3;
    padding: 20px 60px 10px;
    display: flex;
    flex-direction: column;
    gap: 0;
    position: relative;
    z-index: 1;
}

.grid-header {
    display: grid;
    grid-template-columns: 280px 1fr 1fr 1fr;
    gap: 20px;
    padding: 0 20px 16px;
}

.grid-header > div {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.4);
}

.grid-header .col-staff,
.grid-header .col-store {
    text-align: center;
}

.grid-row {
    flex: 1;
    display: grid;
    grid-template-columns: 280px 1fr 1fr 1fr;
    gap: 20px;
    align-items: center;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 28px 30px;
    margin-bottom: 12px;
    transition: transform 0.3s ease;
}

/* Category column */
.col-category {
    display: flex;
    align-items: center;
    gap: 18px;
}

.category-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.category-icon .material-icons {
    font-size: 32px;
}

.category-icon.ly {
    background: rgba(255, 200, 60, 0.15);
}

.category-icon.ly .material-icons {
    color: #f0c040;
}

.category-icon.mtd {
    background: rgba(100, 180, 255, 0.2);
}

.category-icon.mtd .material-icons {
    color: #64b4ff;
}

.category-icon.target {
    background: rgba(200, 80, 192, 0.2);
}

.category-icon.target .material-icons {
    color: var(--brand-accent);
}

.category-label {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    line-height: 1.3;
    color: rgba(255,255,255,0.8);
}

/* Employee column */
.col-employee {
    display: flex;
    align-items: center;
    padding-left: 10px;
}

.emp-name {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
}

/* Value columns */
.col-staff,
.col-store {
    text-align: center;
}

.metric-value {
    font-size: 48px;
    font-weight: 800;
    color: var(--brand-primary);
}

.metric-value.store-value {
    color: rgba(255,255,255,0.7);
}

.metric-sub {
    font-size: 18px;
    font-weight: 600;
    margin-top: 4px;
    color: rgba(255,255,255,0.4);
}

.metric-sub.ahead { color: var(--brand-primary); }
.metric-sub.behind { color: #ff6b6b; }

/* Bottom sections (2x2 grid) */
.bottom-sections {
    flex: 2;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 12px 20px;
    padding: 10px 60px 6px;
    position: relative;
    z-index: 1;
}

.bottom-card {
    display: flex;
    flex-direction: column;
}

.bottom-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: rgba(255,255,255,0.3);
    margin-bottom: 8px;
}

.bottom-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 20px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 24px;
}

.bottom-name {
    font-size: 20px;
    font-weight: 700;
    flex: 1;
}

.bottom-value {
    font-size: 28px;
    font-weight: 800;
    color: rgba(255,255,255,0.7);
}

.bottom-detail {
    font-size: 14px;
    font-weight: 600;
    color: rgba(255,255,255,0.4);
}

/* Footer */
.footer {
    display: flex;
    justify-content: space-between;
    padding: 12px 60px 28px;
    position: relative;
    z-index: 1;
}

.employee-count {
    font-size: 14px;
    color: rgba(255,255,255,0.3);
}
"""

STORE_TOP_PERFORMERS_JS = r"""
(function() {
    var dataLoaded = false;

    ['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
     'https://fonts.googleapis.com/icon?family=Material+Icons'].forEach(function(url) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        document.head.appendChild(link);
    });

    window.addEventListener('signageDataLoaded', function() {
        updateHeader();
        populateCompanyRank();
    });

    window.addEventListener('employeeDataLoaded', function() {
        dataLoaded = true;
        populateGrid();
    });

    setTimeout(function() {
        if (!dataLoaded) showNoData();
    }, 10000);

    function showNoData() {
        var el = document.getElementById('mtdName');
        if (el) el.textContent = 'No data available';
    }

    function populateCompanyRank() {
        var sales = window.signageData;
        if (!sales || !sales.mtd || !sales.mtd.all_profit) return;

        var allStores = sales.mtd.all_profit;
        var storeId = sales.store && sales.store.store_id;
        var storeName = sales.store && sales.store.store_name;

        // Current store rank
        if (storeId || storeName) {
            for (var i = 0; i < allStores.length; i++) {
                if (allStores[i].store_id === storeId || allStores[i].store_name === storeName) {
                    setText('companyRankText', '#' + (i + 1) + ' of ' + allStores.length + ' stores');
                    setText('companyRankProfit', allStores[i].value || '$0');
                    setText('companyRankDetail', 'MTD Profit');
                    break;
                }
            }
        }

        // Top store in company (first in sorted list)
        if (allStores.length > 0) {
            var top = allStores[0];
            setText('topCompanyStoreName', top.store_name || 'Unknown');
            setText('topCompanyStoreValue', top.value || '$0');
            setText('topCompanyStoreDetail', 'MTD Profit');
        }

        // Fetch company-wide employees for top employee
        fetchCompanyTopEmployee();
    }

    function fetchCompanyTopEmployee() {
        fetch('/api/data/employees/')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.success || !data.employees || !data.employees.employees) return;
                var allEmps = data.employees.employees;
                if (allEmps.length === 0) return;

                var topEmp = allEmps.slice().sort(function(a, b) {
                    return (b.mtd.profit_raw || 0) - (a.mtd.profit_raw || 0);
                })[0];

                setText('topCompanyEmpName', topEmp.employee_name || 'Unknown');
                setText('topCompanyEmpValue', formatCurrency(topEmp.mtd.profit_raw || 0));
                setText('topCompanyEmpStore', topEmp.store_name || '');
            })
            .catch(function() {});
    }

    function updateHeader() {
        var sales = window.signageData;
        if (!sales) return;

        var storeName = '';
        if (sales.store && sales.store.store_name) {
            storeName = sales.store.store_name.toUpperCase() + ' TOP PERFORMERS';
        } else {
            storeName = 'STORE TOP PERFORMERS';
        }
        setText('storeName', storeName);

        if (sales.meta && sales.meta.current_day_date) {
            var d = new Date(sales.meta.current_day_date + 'T00:00:00');
            setText('dateDisplay', d.toLocaleDateString('en-US', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            }));
        }

        if (sales.meta && sales.meta.last_updated) {
            var ts = new Date(sales.meta.last_updated);
            var timeStr = 'Updated ' + ts.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
            setText('lastUpdated', timeStr);
            setText('lastUpdated2', timeStr);
        }
    }

    function populateGrid() {
        var data = window.employeeData;
        if (!data || !data.employees || data.employees.length === 0) {
            showNoData();
            return;
        }

        var employees = data.employees;

        // Find top employee by LY month profit
        var topLY = employees.slice().sort(function(a, b) {
            return (b.prior_year.profit_raw || 0) - (a.prior_year.profit_raw || 0);
        })[0];

        // Find top employee by MTD profit
        var topMTD = employees.slice().sort(function(a, b) {
            return (b.mtd.profit_raw || 0) - (a.mtd.profit_raw || 0);
        })[0];

        // Target row uses the top MTD employee
        var topTarget = topMTD;

        // Calculate store totals
        var storeLY = 0, storeMTD = 0, storeTarget = 0;
        employees.forEach(function(emp) {
            storeLY += (emp.prior_year.profit_raw || 0);
            storeMTD += (emp.mtd.profit_raw || 0);
            storeTarget += (emp.targets.profit_target_raw || 0);
        });

        // Populate LY row
        setText('lyName', topLY.employee_name || 'Unknown');
        setText('lyStaffValue', formatCurrency(topLY.prior_year.profit_raw || 0));
        setText('lyStoreValue', formatCurrency(storeLY));

        // Populate MTD row
        setText('mtdName', topMTD.employee_name || 'Unknown');
        setText('mtdStaffValue', formatCurrency(topMTD.mtd.profit_raw || 0));
        setText('mtdStoreValue', formatCurrency(storeMTD));

        // Populate Target row
        setText('targetName', topTarget.employee_name || 'Unknown');
        setText('targetStaffValue', formatCurrency(topTarget.targets.profit_target_raw || 0));
        setText('targetStoreValue', formatCurrency(storeTarget));

        // Show % of target achieved
        var staffPct = topTarget.targets.profit_pct_of_target_raw || 0;
        var staffPctEl = document.getElementById('targetStaffPct');
        if (staffPctEl) {
            staffPctEl.textContent = staffPct.toFixed(0) + '% achieved';
            staffPctEl.className = 'metric-sub ' + (staffPct >= 100 ? 'ahead' : 'behind');
        }

        if (storeTarget > 0) {
            var storePct = (storeMTD / storeTarget) * 100;
            var storePctEl = document.getElementById('targetStorePct');
            if (storePctEl) {
                storePctEl.textContent = storePct.toFixed(0) + '% achieved';
                storePctEl.className = 'metric-sub ' + (storePct >= 100 ? 'ahead' : 'behind');
            }
        }

        // 2nd place MTD employee
        var sortedMTD = employees.slice().sort(function(a, b) {
            return (b.mtd.profit_raw || 0) - (a.mtd.profit_raw || 0);
        });
        if (sortedMTD.length >= 2) {
            var second = sortedMTD[1];
            setText('runnerUpName', second.employee_name || 'Unknown');
            setText('runnerUpValue', formatCurrency(second.mtd.profit_raw || 0));
            var gap = (topMTD.mtd.profit_raw || 0) - (second.mtd.profit_raw || 0);
            setText('runnerUpGap', formatCurrency(gap) + ' behind #1');
        } else {
            var section = document.getElementById('runnerUpSection');
            if (section) section.style.display = 'none';
        }

        // Employee count
        setText('employeeCount', employees.length + ' employees');
    }

    function formatCurrency(value) {
        if (value >= 1000) {
            return '$' + (value / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
        }
        return '$' + Math.round(value).toLocaleString();
    }

    function setText(id, value) {
        var el = document.getElementById(id);
        if (el) el.textContent = value;
    }
})();
"""


# =============================================================================
# STORE PERFORMANCE SNAPSHOT TEMPLATE
# =============================================================================

STORE_SNAPSHOT_HTML = r"""
<div class="snapshot-screen">
    <div class="header">
        <img src="/static/signage/img/jump-logo-white.png" class="logo" alt="Jump.ca"
             onerror="this.style.display='none'">
        <div class="header-center">
            <div class="title" id="storeName">PERFORMANCE SNAPSHOT</div>
            <div class="subtitle" id="dateDisplay"></div>
        </div>
        <div class="header-right">
            <div class="last-updated" id="lastUpdated"></div>
        </div>
    </div>

    <div class="cards-stack" id="cardsStack">
        <!-- Card 1: Last Year -->
        <div class="wide-card">
            <div class="card-left">
                <div class="card-icon ly"><span class="material-icons">history</span></div>
                <div class="card-info">
                    <div class="card-label">VS LAST YEAR</div>
                    <div class="card-emp" id="lyName2">--</div>
                </div>
            </div>
            <div class="card-metrics">
                <div class="metric-block">
                    <div class="metric-label">STAFF</div>
                    <div class="metric-num primary" id="lyStaffBig">$0</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">STORE</div>
                    <div class="metric-num" id="lyStoreBig">$0</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">CONTRIBUTION</div>
                    <div class="metric-num small" id="lyContrib">0%</div>
                </div>
            </div>
            <div class="card-bar">
                <div class="bar-track"><div class="bar-fill" id="lyBarStaff"></div></div>
            </div>
        </div>

        <!-- Card 2: MTD -->
        <div class="wide-card featured">
            <div class="card-left">
                <div class="card-icon mtd"><span class="material-icons">trending_up</span></div>
                <div class="card-info">
                    <div class="card-label">MONTH TO DATE</div>
                    <div class="card-emp" id="mtdName2">--</div>
                </div>
            </div>
            <div class="card-metrics">
                <div class="metric-block">
                    <div class="metric-label">STAFF</div>
                    <div class="metric-num primary" id="mtdStaffBig">$0</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">STORE</div>
                    <div class="metric-num" id="mtdStoreBig">$0</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">CONTRIBUTION</div>
                    <div class="metric-num small" id="mtdContrib">0%</div>
                </div>
            </div>
            <div class="card-bar">
                <div class="bar-track"><div class="bar-fill" id="mtdBarStaff"></div></div>
            </div>
        </div>

        <!-- Card 3: Target -->
        <div class="wide-card">
            <div class="card-left">
                <div class="card-icon target"><span class="material-icons">flag</span></div>
                <div class="card-info">
                    <div class="card-label">PROFIT TARGET</div>
                    <div class="card-emp" id="targetName2">--</div>
                </div>
            </div>
            <div class="card-metrics">
                <div class="metric-block">
                    <div class="metric-label">STAFF TARGET</div>
                    <div class="metric-num primary" id="targetStaffBig">$0</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">STORE TARGET</div>
                    <div class="metric-num" id="storeTargetVal">$0</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">STAFF %</div>
                    <div class="metric-num small" id="staffTargetPct">0%</div>
                </div>
                <div class="metric-block">
                    <div class="metric-label">STORE %</div>
                    <div class="metric-num small" id="storeTargetPct">0%</div>
                </div>
            </div>
            <div class="card-bar">
                <div class="bar-track"><div class="bar-fill" id="targetBarStaff"></div></div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="employee-count" id="employeeCount2"></div>
        <div class="last-updated" id="lastUpdated2"></div>
    </div>
</div>
"""

STORE_SNAPSHOT_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

:root {
    --brand-primary: #00aa90;
    --brand-accent: #c850c0;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

.snapshot-screen {
    width: 1920px;
    height: 1080px;
    font-family: 'Inter', sans-serif;
    background: url('/static/signage/img/brand-bg.png') center/cover no-repeat, #1a1a2e;
    color: #fff;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 30px 50px 20px;
    position: relative;
    z-index: 1;
}

.logo { height: 44px; opacity: 0.9; }
.header-center { text-align: center; }

.title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 3px;
}

.subtitle {
    font-size: 15px;
    color: rgba(255,255,255,0.6);
    margin-top: 4px;
}

.header-right { text-align: right; }

.last-updated {
    font-size: 13px;
    color: rgba(255,255,255,0.4);
}

/* Cards Stack */
.cards-stack {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 10px 50px;
    position: relative;
    z-index: 1;
}

.wide-card {
    flex: 1;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 28px 40px;
    display: flex;
    align-items: center;
    gap: 40px;
    position: relative;
    overflow: hidden;
}

.wide-card.featured {
    background: rgba(255,255,255,0.12);
    border-color: rgba(0, 170, 144, 0.3);
    box-shadow: 0 0 40px rgba(0, 170, 144, 0.1);
}

/* Left section: icon + label + employee */
.card-left {
    display: flex;
    align-items: center;
    gap: 18px;
    min-width: 340px;
}

.card-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.card-icon .material-icons {
    font-size: 28px;
}

.card-icon.ly { background: rgba(255, 200, 60, 0.15); }
.card-icon.ly .material-icons { color: #f0c040; }
.card-icon.mtd { background: rgba(100, 180, 255, 0.2); }
.card-icon.mtd .material-icons { color: #64b4ff; }
.card-icon.target { background: rgba(200, 80, 192, 0.2); }
.card-icon.target .material-icons { color: var(--brand-accent); }

.card-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.card-label {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.45);
}

.card-emp {
    font-size: 26px;
    font-weight: 700;
    white-space: nowrap;
}

/* Metrics section */
.card-metrics {
    display: flex;
    gap: 48px;
    flex: 1;
    justify-content: center;
}

.metric-block {
    text-align: center;
}

.metric-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.4);
    margin-bottom: 6px;
}

.metric-num {
    font-size: 32px;
    font-weight: 800;
    color: rgba(255,255,255,0.8);
}

.metric-num.primary {
    color: var(--brand-primary);
}

.metric-num.small {
    font-size: 28px;
}

/* Bar section */
.card-bar {
    width: 200px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
}

.bar-track {
    width: 100%;
    height: 12px;
    background: rgba(255,255,255,0.1);
    border-radius: 6px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, var(--brand-primary), var(--brand-accent));
    transition: width 1s ease;
    width: 0%;
}

/* Footer */
.footer {
    display: flex;
    justify-content: space-between;
    padding: 8px 50px 24px;
    position: relative;
    z-index: 1;
}

.employee-count {
    font-size: 14px;
    color: rgba(255,255,255,0.3);
}
"""

STORE_SNAPSHOT_JS = r"""
(function() {
    var dataLoaded = false;

    ['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
     'https://fonts.googleapis.com/icon?family=Material+Icons'].forEach(function(url) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        document.head.appendChild(link);
    });

    window.addEventListener('signageDataLoaded', function() {
        updateHeader();
    });

    window.addEventListener('employeeDataLoaded', function() {
        dataLoaded = true;
        populateCards();
    });

    setTimeout(function() {
        if (!dataLoaded) {
            var el = document.getElementById('mtdName2');
            if (el) el.textContent = 'No data available';
        }
    }, 10000);

    function updateHeader() {
        var sales = window.signageData;
        if (!sales) return;

        var storeName = '';
        if (sales.store && sales.store.store_name) {
            storeName = sales.store.store_name.toUpperCase() + ' SNAPSHOT';
        } else {
            storeName = 'PERFORMANCE SNAPSHOT';
        }
        setText('storeName', storeName);

        if (sales.meta && sales.meta.current_day_date) {
            var d = new Date(sales.meta.current_day_date + 'T00:00:00');
            setText('dateDisplay', d.toLocaleDateString('en-US', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            }));
        }

        if (sales.meta && sales.meta.last_updated) {
            var ts = new Date(sales.meta.last_updated);
            var timeStr = 'Updated ' + ts.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
            setText('lastUpdated', timeStr);
            setText('lastUpdated2', timeStr);
        }
    }

    function populateCards() {
        var data = window.employeeData;
        if (!data || !data.employees || data.employees.length === 0) return;

        var employees = data.employees;

        // Find top employees
        var topLY = employees.slice().sort(function(a, b) {
            return (b.prior_year.profit_raw || 0) - (a.prior_year.profit_raw || 0);
        })[0];

        var topMTD = employees.slice().sort(function(a, b) {
            return (b.mtd.profit_raw || 0) - (a.mtd.profit_raw || 0);
        })[0];

        var topTarget = topMTD;

        // Store totals
        var storeLY = 0, storeMTD = 0, storeTarget = 0;
        employees.forEach(function(emp) {
            storeLY += (emp.prior_year.profit_raw || 0);
            storeMTD += (emp.mtd.profit_raw || 0);
            storeTarget += (emp.targets.profit_target_raw || 0);
        });

        // Card 1: LY
        setText('lyName2', topLY.employee_name || 'Unknown');
        setText('lyStaffBig', formatCurrency(topLY.prior_year.profit_raw || 0));
        setText('lyStoreBig', formatCurrency(storeLY));
        setBar('lyBarStaff', topLY.prior_year.profit_raw || 0, storeLY);
        var lyContrib = storeLY > 0 ? ((topLY.prior_year.profit_raw || 0) / storeLY * 100).toFixed(0) + '%' : '0%';
        setText('lyContrib', lyContrib);

        // Card 2: MTD
        setText('mtdName2', topMTD.employee_name || 'Unknown');
        setText('mtdStaffBig', formatCurrency(topMTD.mtd.profit_raw || 0));
        setText('mtdStoreBig', formatCurrency(storeMTD));
        setBar('mtdBarStaff', topMTD.mtd.profit_raw || 0, storeMTD);
        var mtdContrib = storeMTD > 0 ? ((topMTD.mtd.profit_raw || 0) / storeMTD * 100).toFixed(0) + '%' : '0%';
        setText('mtdContrib', mtdContrib);

        // Card 3: Target
        setText('targetName2', topTarget.employee_name || 'Unknown');
        setText('targetStaffBig', formatCurrency(topTarget.targets.profit_target_raw || 0));
        setText('storeTargetVal', formatCurrency(storeTarget));
        var staffPct = topTarget.targets.profit_pct_of_target_raw || 0;
        setText('staffTargetPct', staffPct.toFixed(0) + '%');
        var storePct = storeTarget > 0 ? (storeMTD / storeTarget * 100) : 0;
        setText('storeTargetPct', storePct.toFixed(0) + '%');
        setBar('targetBarStaff', staffPct, 100);

        setText('employeeCount2', employees.length + ' employees');
    }

    function formatCurrency(value) {
        if (value >= 1000) {
            return '$' + (value / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
        }
        return '$' + Math.round(value).toLocaleString();
    }

    function setBar(id, staffVal, storeVal) {
        var el = document.getElementById(id);
        if (el && storeVal > 0) {
            var pct = Math.min((staffVal / storeVal) * 100, 100);
            el.style.width = pct + '%';
        }
    }

    function setText(id, value) {
        var el = document.getElementById(id);
        if (el) el.textContent = value;
    }
})();
"""


# =============================================================================
# COMMAND
# =============================================================================

TEMPLATES = [
    {
        'name': 'Staff KPI Card',
        'slug': 'staff-kpi-card',
        'description': 'Full-screen employee KPI display that auto-rotates through each team member. Shows today\'s profit, MTD profit, targets, prior year comparison, and store rank. Set a store filter on the design to show only that store\'s employees.',
        'template_type': 'kpi_dashboard',
        'html_code': STAFF_KPI_HTML,
        'css_code': STAFF_KPI_CSS,
        'js_code': STAFF_KPI_JS,
        'is_featured': True,
        'branding_config': {
            'primary_color': '#00aa90',
            'secondary_color': '#003d36',
            'accent_color': '#c850c0',
            'text_color': '#ffffff',
        },
    },
    {
        'name': 'Store Leaderboard',
        'slug': 'store-leaderboard',
        'description': 'Company-wide store leaderboard showing MTD profit rankings with prior year comparison and target percentages. Auto-pages through all stores.',
        'template_type': 'leaderboard',
        'html_code': STORE_LEADERBOARD_HTML,
        'css_code': STORE_LEADERBOARD_CSS,
        'js_code': STORE_LEADERBOARD_JS,
        'is_featured': True,
        'branding_config': {
            'primary_color': '#00aa90',
            'secondary_color': '#003d36',
            'accent_color': '#c850c0',
            'text_color': '#ffffff',
        },
    },
    {
        'name': 'Store Top Performers',
        'slug': 'store-top-performers',
        'description': 'Shows the top employee in each key category (Last Year, MTD, Target) compared to store totals. A quick at-a-glance view of who is leading in each metric. Set a store filter to show a specific store.',
        'template_type': 'kpi_dashboard',
        'html_code': STORE_TOP_PERFORMERS_HTML,
        'css_code': STORE_TOP_PERFORMERS_CSS,
        'js_code': STORE_TOP_PERFORMERS_JS,
        'is_featured': True,
        'branding_config': {
            'primary_color': '#00aa90',
            'secondary_color': '#003d36',
            'accent_color': '#c850c0',
            'text_color': '#ffffff',
        },
    },
    {
        'name': 'Store Performance Snapshot',
        'slug': 'store-performance-snapshot',
        'description': 'Visual performance dashboard with three cards showing the top performer in Last Year profit, MTD profit, and Target achievement. Includes contribution bars and a target ring chart. Set a store filter for store-specific data.',
        'template_type': 'kpi_dashboard',
        'html_code': STORE_SNAPSHOT_HTML,
        'css_code': STORE_SNAPSHOT_CSS,
        'js_code': STORE_SNAPSHOT_JS,
        'is_featured': True,
        'branding_config': {
            'primary_color': '#00aa90',
            'secondary_color': '#003d36',
            'accent_color': '#c850c0',
            'text_color': '#ffffff',
        },
    },
]


class Command(BaseCommand):
    help = 'Create built-in screen templates (Staff KPI Card, Store Leaderboard, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing templates with the same slug',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = 0
        updated = 0
        skipped = 0

        for tmpl_data in TEMPLATES:
            slug = tmpl_data['slug']
            existing = ScreenTemplate.objects.filter(slug=slug).first()

            if existing and not force:
                self.stdout.write(self.style.WARNING(f'  Skipped "{tmpl_data["name"]}" (already exists, use --force to overwrite)'))
                skipped += 1
                continue

            if existing and force:
                for key, value in tmpl_data.items():
                    setattr(existing, key, value)
                existing.save()
                self.stdout.write(self.style.SUCCESS(f'  Updated "{tmpl_data["name"]}"'))
                updated += 1
            else:
                ScreenTemplate.objects.create(**tmpl_data)
                self.stdout.write(self.style.SUCCESS(f'  Created "{tmpl_data["name"]}"'))
                created += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done: {created} created, {updated} updated, {skipped} skipped'
        ))
