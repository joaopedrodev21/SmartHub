/* ============================================================
   SmartHub CRM — Tema claro/escuro + Sidebar drawer
   ============================================================ */
(function () {
  'use strict';

  var THEME_KEY = 'smarthub-theme';
  var root = document.documentElement;

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (e) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* ignore */
    }
  }

  function getSystemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches
      ? 'light'
      : 'dark';
  }

  function applyTheme(theme, persist) {
    root.setAttribute('data-theme', theme);
    if (persist) {
      storeTheme(theme);
    }
    var toggle = document.querySelector('.theme-toggle');
    if (toggle) {
      var icon = toggle.querySelector('[data-theme-icon]');
      if (icon) {
        icon.setAttribute('data-lucide', theme === 'dark' ? 'moon' : 'sun');
      }
    }
    if (window.lucide) {
      lucide.createIcons();
    }
    document.dispatchEvent(new CustomEvent('smarthub:theme-change', { detail: { theme: theme } }));
  }

  function initTheme() {
    var stored = getStoredTheme();
    var theme = stored || getSystemTheme();
    applyTheme(theme, false);
  }

  function toggleTheme() {
    var current = root.getAttribute('data-theme') || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark', true);
  }

  /* Sidebar drawer (mobile) */
  function initSidebar() {
    var toggleBtn = document.querySelector('[data-sidebar-toggle]');
    var backdrop = document.querySelector('.sidebar-backdrop');
    var sidebar = document.querySelector('.sidebar');

    function close() {
      if (sidebar) sidebar.classList.remove('open');
      if (backdrop) backdrop.classList.remove('show');
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        if (sidebar) sidebar.classList.toggle('open');
        if (backdrop) backdrop.classList.toggle('show');
      });
    }
    if (backdrop) {
      backdrop.addEventListener('click', close);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTheme();

    var toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleTheme);
    }

    initSidebar();
  });
})();