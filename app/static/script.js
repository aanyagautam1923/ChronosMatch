"use strict";

/*
 * ChronosMatch Dashboard
 *
 * Week 1:
 *   Basic dashboard and API connectivity.
 *
 * Week 2:
 *   Async processing and optimized engine statistics.
 *
 * Week 3:
 *   Order book and latency monitoring integration.
 *
 * Week 4:
 *   Full integration, testing and error handling.
 *
 * Backend endpoint paths can be configured below.
 */

const CONFIG = {
    healthEndpoints: ["/health", "/api/health"],
    statsEndpoints: ["/api/stats", "/stats"],
    orderEndpoints: ["/api/orders", "/orders"],
    refreshInterval: 5000,
    requestTimeout: 4000,
    maxChartPoints: 24,
    maxOrders: 50
};

const state = {
    online: false,
    refreshing: false,
    chartValues: [],
    lastStats: null,
    lastOrders: [],
    timer: null
};

const $ = (id) => document.getElementById(id);

function setText(id, value) {
    const element = $(id);

    if (element) {
        element.textContent = value;
    }
}

function showNotification(message) {
    const notification = $("notification");

    if (!notification) return;

    notification.textContent = message;
    notification.classList.add("show");

    clearTimeout(showNotification.timeout);

    showNotification.timeout = setTimeout(() => {
        notification.classList.remove("show");
    }, 3000);
}

function setConnectionStatus(online, message) {
    state.online = online;

    const dotIds = ["sidebar-status", "live-dot"];

    dotIds.forEach((id) => {
        const dot = $(id);

        if (!dot) return;

        dot.classList.toggle("online", online);
        dot.classList.toggle("offline", !online);
    });

    setText(
        "sidebar-status-text",
        online ? "Backend connected" : "Backend offline"
    );

    setText(
        "connection-label",
        message || (online ? "Connected to backend" : "Backend unavailable")
    );

    setText("engine-status", online ? "Online" : "Offline");

    setText(
        "engine-description",
        online ? "API responding" : "Check backend server"
    );

    const refreshButton = $("refresh-btn");

    if (refreshButton) {
        refreshButton.disabled = state.refreshing;
    }
}

async function fetchJson(url) {
    const controller = new AbortController();

    const timeout = setTimeout(() => {
        controller.abort();
    }, CONFIG.requestTimeout);

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            cache: "no-store",
            signal: controller.signal
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } finally {
        clearTimeout(timeout);
    }
}

async function tryEndpoints(endpoints) {
    let lastError = null;

    for (const endpoint of endpoints) {
        try {
            const data = await fetchJson(endpoint);

            return {
                ok: true,
                endpoint,
                data
            };
        } catch (error) {
            lastError = error;
        }
    }

    return {
        ok: false,
        endpoint: null,
        data: null,
        error: lastError
    };
}

function getNumber(object, keys) {
    if (!object || typeof object !== "object") {
        return null;
    }

    for (const key of keys) {
        const value = key.split(".").reduce((current, part) => {
            return current == null ? undefined : current[part];
        }, object);

        if (
            value !== undefined &&
            value !== null &&
            value !== "" &&
            Number.isFinite(Number(value))
        ) {
            return Number(value);
        }
    }

    return null;
}

function formatNumber(value) {
    if (value === null || value === undefined) {
        return "--";
    }

    return new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 2
    }).format(value);
}

function formatLatency(value, unit) {
    if (value === null) {
        return "--";
    }

    const normalizedUnit = String(unit || "").toLowerCase();

    if (normalizedUnit.includes("ns")) {
        return `${formatNumber(value)} ns`;
    }

    if (normalizedUnit.includes("us") ||
        normalizedUnit.includes("µs")) {
        return `${formatNumber(value)} µs`;
    }

    if (normalizedUnit.includes("ms")) {
        return `${formatNumber(value)} ms`;
    }

    // Without explicit units, retain the backend's raw numeric value.
    return `${formatNumber(value)} (raw)`;
}

function normalizeStats(payload) {
    const data = payload?.data || payload?.stats || payload || {};

    const latencyObject = data.latency || data.latency_stats || {};

    return {
        totalOrders: getNumber(data, [
            "total_orders",
            "orders_processed",
            "processed_orders",
            "total_processed",
            "order_count",
            "metrics.total_orders"
        ]),

        throughput: getNumber(data, [
            "throughput",
            "orders_per_second",
            "orders_per_sec",
            "ops_per_second",
            "metrics.throughput"
        ]),

        latency: getNumber(data, [
            "average_latency",
            "avg_latency",
            "latency_avg",
            "average_latency_ns",
            "latency.average",
            "latency.avg",
            "latency_avg_ns"
        ]) ?? getNumber(latencyObject, [
            "average",
            "avg",
            "mean",
            "avg_ns"
        ]),

        latencyUnit:
            data.latency_unit ||
            data.latency_units ||
            latencyObject.unit ||
            "",

        raw: data
    };
}

function updateStats(payload) {
    const stats = normalizeStats(payload);

    state.lastStats = stats;

    setText("total-orders", formatNumber(stats.totalOrders));
    setText("throughput", formatNumber(stats.throughput));

    setText(
        "latency",
        formatLatency(stats.latency, stats.latencyUnit)
    );

    setText(
        "performance-throughput",
        formatNumber(stats.throughput)
    );

    if (stats.throughput !== null) {
        addChartPoint(stats.throughput);
    }

    updateComponentStatuses(stats.raw);
}

function updateComponentStatuses(data) {
    const components = {
        "protocol-status": [
            "protocol",
            "order_protocol"
        ],

        "buffer-status": [
            "ring_buffer",
            "buffer"
        ],

        "matching-status": [
            "matching_engine",
            "engine"
        ],

        "firehose-status": [
            "firehose",
            "receiver"
        ]
    };

    for (const [elementId, keys] of Object.entries(components)) {
        const element = $(elementId);

        if (!element) continue;

        let value;

        for (const key of keys) {
            if (data && data[key] !== undefined) {
                value = data[key];
                break;
            }
        }

        if (value === undefined) {
            element.textContent = "Not reported";
            element.className = "component-status";
            continue;
        }

        const isOnline =
            value === true ||
            value === "online" ||
            value === "healthy" ||
            value === "running";

        const isOffline =
            value === false ||
            value === "offline" ||
            value === "stopped" ||
            value === "error";

        element.textContent = isOnline
            ? "Online"
            : isOffline
                ? "Offline"
                : String(value);

        element.className = "component-status";

        if (isOnline) {
            element.classList.add("online");
        } else if (isOffline) {
            element.classList.add("offline");
        }
    }
}

function addChartPoint(value) {
    if (!Number.isFinite(value) || value < 0) {
        return;
    }

    state.chartValues.push(value);

    if (state.chartValues.length > CONFIG.maxChartPoints) {
        state.chartValues.shift();
    }

    renderChart();
}

function renderChart() {
    const chart = $("performance-chart");

    if (!chart) return;

    if (state.chartValues.length === 0) {
        chart.replaceChildren();

        const placeholder = document.createElement("div");

        placeholder.className = "chart-placeholder";
        placeholder.textContent = "Waiting for performance data";

        chart.appendChild(placeholder);

        return;
    }

    chart.replaceChildren();

    const maxValue = Math.max(...state.chartValues, 1);

    state.chartValues.forEach((value, index) => {
        const bar = document.createElement("div");

        bar.className = "chart-bar";

        const height = Math.max(
            4,
            (value / maxValue) * 100
        );

        bar.style.height = `${height}%`;

        bar.title =
            `Sample ${index + 1}: ${formatNumber(value)} orders/sec`;

        chart.appendChild(bar);
    });

    setText(
        "chart-update-time",
        `Updated ${new Date().toLocaleTimeString()}`
    );
}

function normalizeOrders(payload) {
    let orders = payload;

    if (payload && !Array.isArray(payload)) {
        orders =
            payload.orders ??
            payload.data?.orders ??
            payload.results ??
            payload.data ??
            [];
    }

    return Array.isArray(orders) ? orders : [];
}

function safeValue(value, fallback = "--") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }

    return String(value);
}

function createCell(value, className = "") {
    const cell = document.createElement("td");

    cell.textContent = safeValue(value);

    if (className) {
        cell.className = className;
    }

    return cell;
}

function renderOrders(orders) {
    const tbody = $("orders-table-body");

    if (!tbody) return;

    tbody.replaceChildren();

    if (!orders.length) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.className = "empty-state";
        cell.textContent = state.online
            ? "No orders have been returned by the backend."
            : "Backend unavailable. Live orders cannot be loaded.";

        row.appendChild(cell);
        tbody.appendChild(row);

        return;
    }

    orders.slice(0, CONFIG.maxOrders).forEach((order) => {
        const row = document.createElement("tr");

        const id = order.order_id ?? order.id ?? order.orderId;

        const symbol =
            order.symbol ??
            order.instrument ??
            order.ticker;

        const side = String(
            order.side ?? order.order_type ?? "--"
        ).toUpperCase();

        const quantity =
            order.quantity ??
            order.qty ??
            order.size;

        const price = order.price ?? order.limit_price;

        const status = String(
            order.status ?? order.state ?? "Received"
        );

        row.appendChild(createCell(id));
        row.appendChild(createCell(symbol));

        row.appendChild(
            createCell(
                side,
                side === "BUY"
                    ? "side-buy"
                    : side === "SELL"
                        ? "side-sell"
                        : ""
            )
        );

        row.appendChild(createCell(quantity));
        row.appendChild(createCell(price));

        const statusCell = document.createElement("td");
        const badge = document.createElement("span");

        badge.className = "order-status";
        badge.textContent = status;

        if (/pending|queued/i.test(status)) {
            badge.classList.add("pending");
        } else if (/reject|error|fail/i.test(status)) {
            badge.classList.add("rejected");
        }

        statusCell.appendChild(badge);
        row.appendChild(statusCell);

        tbody.appendChild(row);
    });
}

async function refreshDashboard(showMessage = false) {
    if (state.refreshing) return;

    state.refreshing = true;

    const button = $("refresh-btn");

    if (button) {
        button.disabled = true;
        button.textContent = "Refreshing...";
    }

    try {
        const healthResult = await tryEndpoints(
            CONFIG.healthEndpoints
        );

        const statsResult = await tryEndpoints(
            CONFIG.statsEndpoints
        );

        const ordersResult = await tryEndpoints(
            CONFIG.orderEndpoints
        );

        const online =
            healthResult.ok ||
            statsResult.ok ||
            ordersResult.ok;

        setConnectionStatus(
            online,
            online
                ? "Backend responding"
                : "Backend unavailable"
        );

        if (statsResult.ok) {
            updateStats(statsResult.data);
        }

        if (ordersResult.ok) {
            state.lastOrders = normalizeOrders(ordersResult.data);

            renderOrders(state.lastOrders);
        } else if (!online) {
            renderOrders([]);
        }

        if (healthResult.ok) {
            const health = healthResult.data;

            if (health && typeof health === "object") {
                const reportedStatus =
                    health.status ??
                    health.state ??
                    health.data?.status;

                if (reportedStatus !== undefined) {
                    setText("engine-status", String(reportedStatus));
                }
            }
        }

        if (showMessage) {
            showNotification(
                online
                    ? "Dashboard refreshed."
                    : "Backend unavailable. Start your FastAPI server."
            );
        }
    } catch (error) {
        console.error("Dashboard refresh failed:", error);

        setConnectionStatus(false, "Connection error");

        if (showMessage) {
            showNotification("Unable to refresh dashboard.");
        }
    } finally {
        state.refreshing = false;

        if (button) {
            button.disabled = false;
            button.textContent = "↻ Refresh";
        }
    }
}

function initializeDashboard() {
    const refreshButton = $("refresh-btn");
    const ordersButton = $("orders-refresh-btn");

    if (refreshButton) {
        refreshButton.addEventListener("click", () => {
            refreshDashboard(true);
        });
    }

    if (ordersButton) {
        ordersButton.addEventListener("click", async () => {
            await refreshDashboard(true);
        });
    }

    document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => {
            document.querySelectorAll(".nav-link").forEach((item) => {
                item.classList.remove("active");
            });

            link.classList.add("active");
        });
    });

    setConnectionStatus(false, "Connecting to backend");

    renderOrders([]);
    renderChart();

    refreshDashboard();

    state.timer = setInterval(() => {
        refreshDashboard();
    }, CONFIG.refreshInterval);

    window.addEventListener("beforeunload", () => {
        if (state.timer) {
            clearInterval(state.timer);
        }
    });
}

document.addEventListener("DOMContentLoaded", initializeDashboard);
