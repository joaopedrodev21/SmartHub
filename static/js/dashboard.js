/*
   SmartHub CRM — Graficos do Dashboard (Chart.js)
   Espera os dados serializados em <script id="chart-data" type="application/json">
*/
(function () {
  'use strict';

  function cssVar(name, fallback) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
  }

  function palette() {
    var isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
    return {
      text: cssVar('--text', isDark ? '#e6f0ea' : '#1a2620'),
      muted: cssVar('--muted', isDark ? '#8aa39a' : '#5b6b63'),
      grid: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(16,60,32,0.1)',
      green: cssVar('--green', '#22c55e'),
      greenStrong: cssVar('--green-strong', '#16a34a'),
      surface: cssVar('--card-bg', isDark ? '#10150f' : '#ffffff'),
      categories: ['#22c55e', '#7c3aed', '#0ea5e9', '#f59e0b', '#ef4444', '#64748b'],
    };
  }

  function formatCurrency(value) {
    var n = Number(value) || 0;
    return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function buildCharts() {
    var dataEl = document.getElementById('chart-data');
    if (!dataEl || typeof Chart === 'undefined') return;

    var data;
    try {
      data = JSON.parse(dataEl.textContent);
    } catch (e) {
      return;
    }

    var p = palette();
    var common = {
      color: p.text,
      grid: { color: p.grid },
      border: { color: p.grid },
      ticks: { color: p.muted },
    };

    Chart.defaults.color = p.text;
    Chart.defaults.borderColor = p.grid;

    /* Faturamento por mes */
    let revenueLabels = [];
    let revenueValues = [];
    (data.revenue_by_month || []).forEach(function (item) {
      revenueLabels.push(item.label);
      revenueValues.push(Number(item.value));
    });

    var revenueCtx = document.getElementById('chart-revenue');
    if (revenueCtx) {
      new Chart(revenueCtx, {
        type: 'line',
        data: {
          labels: revenueLabels,
          datasets: [{
            label: 'Faturamento',
            data: revenueValues,
            borderColor: p.green,
            backgroundColor: p.surface,
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointBackgroundColor: p.green,
            pointRadius: 4,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: { label: function (ctx) { return ' ' + formatCurrency(ctx.parsed.y); } },
            },
          },
          scales: {
            x: common,
            y: {
              ...common,
              ticks: { ...common.ticks, callback: function (v) { return formatCurrency(v); } },
            },
          },
        },
      });
    }

    /* Vendas por dia */
    let salesLabels = [];
    let salesValues = [];
    (data.sales_by_day || []).forEach(function (item) {
      salesLabels.push(item.label);
      salesValues.push(Number(item.value));
    });

    var salesCtx = document.getElementById('chart-sales');
    if (salesCtx) {
      new Chart(salesCtx, {
        type: 'bar',
        data: {
          labels: salesLabels,
          datasets: [{
            label: 'Vendas',
            data: salesValues,
            backgroundColor: p.green,
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: common, y: { ...common, ticks: { ...common.ticks, precision: 0 } } },
        },
      });
    }

    /* Categorias */
    let catLabels = [];
    let catValues = [];
    (data.category_count || []).forEach(function (item) {
      catLabels.push(item.label);
      catValues.push(Number(item.value));
    });

    let  catCtx = document.getElementById('chart-category');
    if (catCtx) {
      new Chart(catCtx, {
        type: 'doughnut',
        data: {
          labels: catLabels,
          datasets: [{
            data: catValues,
            backgroundColor: p.categories,
            borderColor: p.surface,
            borderWidth: 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { color: p.text, boxWidth: 12 } } },
        },
      });
    }
  }

  function onThemeChange() {
    /* Destroy any existing chart instances and rebuild with the new palette */
    if (Chart && Chart.getChart) {
      let ctxs = document.querySelectorAll('.chart-box canvas');
      ctxs.forEach(function (canvas) {
        var existing = Chart.getChart(canvas);
        if (existing) existing.destroy();
      });
    }
    buildCharts();
  }

  document.addEventListener('DOMContentLoaded', function () {
    buildCharts();
    /* Rebuild charts when the theme toggles (dispatched by theme.js) */
    document.addEventListener('smarthub:theme-change', onThemeChange);
  });
})();