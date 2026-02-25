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
    background: linear-gradient(135deg, var(--brand-dark) 0%, #0a2a26 30%, #1a1a2e 60%, #2d1b3d 100%);
    color: var(--text-primary);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

/* Subtle animated gradient overlay */
.staff-kpi-screen::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 20% 50%, rgba(0, 170, 144, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(200, 80, 192, 0.06) 0%, transparent 50%);
    animation: ambientShift 20s ease-in-out infinite;
    pointer-events: none;
}

@keyframes ambientShift {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-5%, 3%); }
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
    font-size: 22px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.date-display {
    font-size: 15px;
    color: var(--text-secondary);
    margin-top: 2px;
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
    font-size: 28px;
    color: var(--brand-primary);
    margin-bottom: 8px;
    opacity: 0.8;
}

.kpi-label {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.1;
}

.target-of {
    font-size: 24px;
    font-weight: 500;
    color: var(--text-secondary);
}

.kpi-details {
    font-size: 16px;
    color: var(--text-secondary);
    margin-top: 10px;
    font-weight: 500;
}

/* Progress bars */
.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    margin-top: 14px;
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
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 15px;
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
    font-size: 15px;
    color: var(--text-muted);
    font-weight: 500;
}

.last-updated {
    font-size: 13px;
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
    var ROTATION_INTERVAL = 8000; // 8 seconds per employee

    // Wait for data to load
    window.addEventListener('signageDataLoaded', function() {
        updateStoreInfo();
    });

    window.addEventListener('employeeDataLoaded', function(e) {
        var data = window.employeeData;
        if (data && data.employees && data.employees.length > 0) {
            employees = data.employees;
            // Sort by MTD profit (highest first)
            employees.sort(function(a, b) {
                return (b.mtd.profit_raw || 0) - (a.mtd.profit_raw || 0);
            });
            showEmployee(0);
            startRotation();
        }
    });

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
        currentIndex = index % employees.length;
        var emp = employees[currentIndex];

        var content = document.getElementById('mainContent');

        // Fade out
        content.classList.add('fade-out');

        setTimeout(function() {
            // Update employee info
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

            // Store info (refresh in case data updated)
            updateStoreInfo();

            // Employee counter
            var counter = document.getElementById('employeeCounter');
            if (counter) {
                counter.textContent = (currentIndex + 1) + ' of ' + employees.length;
            }

            // Fade in
            content.classList.remove('fade-out');
        }, 500);
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
    background: linear-gradient(135deg, var(--brand-dark) 0%, #0a2a26 30%, #1a1a2e 60%, #2d1b3d 100%);
    color: #fff;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 50px 20px;
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
}

.board-container.fade-out { opacity: 0; }

/* Leaderboard row */
.lb-row {
    display: grid;
    grid-template-columns: 70px 1fr 180px 180px 140px;
    align-items: center;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 24px;
    gap: 16px;
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

.lb-header {
    display: grid;
    grid-template-columns: 70px 1fr 180px 180px 140px;
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
}

.page-indicator, .last-updated {
    font-size: 13px;
    color: rgba(255,255,255,0.35);
}
"""

STORE_LEADERBOARD_JS = r"""
(function() {
    var ROWS_PER_PAGE = 10;
    var PAGE_INTERVAL = 10000;
    var stores = [];
    var currentPage = 0;
    var totalPages = 1;
    var pageTimer = null;

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
        currentPage = page % totalPages;
        var container = document.getElementById('boardContainer');
        container.classList.add('fade-out');

        setTimeout(function() {
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

                row.innerHTML =
                    '<div class="lb-rank ' + rankClass + '">' + rank + '</div>' +
                    '<div class="lb-name">' + (store.store_name || '') + '</div>' +
                    '<div class="lb-value">' + (store.value || '$0') + '</div>' +
                    '<div class="lb-secondary">' + (store.ly_month_profit || '$0') + '</div>' +
                    '<div class="lb-pct ' + pctClass + '">' + pctText + '</div>';

                container.appendChild(row);
            });

            // Page indicator
            var pi = document.getElementById('pageIndicator');
            if (pi && totalPages > 1) {
                pi.textContent = 'Page ' + (currentPage + 1) + ' of ' + totalPages;
            }

            container.classList.remove('fade-out');
        }, 400);
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
