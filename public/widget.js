(function() {
    'use strict';
    // Flebitech Widget v1.1 — Embebible en Genially / Moodle / LMS / Web
    var scriptTag = document.currentScript;
    var origin = scriptTag ? new URL(scriptTag.src).origin : window.location.origin;

    // Container
    var container = document.createElement('div');
    container.id = 'flebitech-widget-root';
    container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:999999;font-family:system-ui,-apple-system,sans-serif;display:flex;flex-direction:column;align-items:flex-end;';

    // Iframe
    var iframe = document.createElement('iframe');
    iframe.src = origin + '/';
    iframe.title = 'Flebitech - Asistente de Flebitis';
    iframe.style.cssText = 'width:420px;max-width:92vw;height:650px;max-height:85vh;border-radius:20px;border:1px solid #CBD5E1;box-shadow:0 20px 60px rgba(0,0,0,0.2),0 4px 12px rgba(0,0,0,0.08);display:none;margin-bottom:12px;background:#fff;transition:opacity 0.25s ease,transform 0.25s ease;opacity:0;transform:translateY(10px) scale(0.98);';

    // Button
    var button = document.createElement('button');
    button.setAttribute('aria-label', 'Abrir Flebitech');
    button.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg><span style="font-size:14px;font-weight:700;">Flebitech</span>';
    button.style.cssText = 'height:52px;padding:0 22px;border-radius:26px;background:linear-gradient(135deg,#1D5FC6 0%,#0A3882 100%);color:#fff;border:none;box-shadow:0 4px 20px rgba(10,56,130,0.35);cursor:pointer;display:flex;align-items:center;font-size:16px;transition:all 0.25s ease;';
    button.onmouseover = function() { button.style.transform = 'scale(1.05)'; button.style.boxShadow = '0 6px 25px rgba(10,56,130,0.45)'; };
    button.onmouseout = function() { button.style.transform = 'scale(1)'; button.style.boxShadow = '0 4px 20px rgba(10,56,130,0.35)'; };

    var isOpen = false;
    button.onclick = function() {
        isOpen = !isOpen;
        if (isOpen) {
            iframe.style.display = 'block';
            requestAnimationFrame(function() {
                iframe.style.opacity = '1';
                iframe.style.transform = 'translateY(0) scale(1)';
            });
            button.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg><span style="font-size:14px;font-weight:700;margin-left:6px;">Cerrar</span>';
        } else {
            iframe.style.opacity = '0';
            iframe.style.transform = 'translateY(10px) scale(0.98)';
            setTimeout(function() { iframe.style.display = 'none'; }, 250);
            button.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg><span style="font-size:14px;font-weight:700;">Flebitech</span>';
        }
    };

    container.appendChild(iframe);
    container.appendChild(button);
    document.body.appendChild(container);
})();
