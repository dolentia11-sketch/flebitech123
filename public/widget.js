(function() {
    'use strict';
    // Flebitech Widget v1.2 — Embebible en Genially / Moodle / LMS / Web (laCardio & Unisabana)
    var scriptTag = document.currentScript;
    var origin = scriptTag ? new URL(scriptTag.src).origin : window.location.origin;

    // Container
    var container = document.createElement('div');
    container.id = 'flebitech-widget-root';
    container.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:999999;font-family:system-ui,-apple-system,sans-serif;display:flex;flex-direction:column;align-items:flex-end;';

    // Iframe
    var iframe = document.createElement('iframe');
    iframe.src = origin + '/';
    iframe.title = 'Flebitech - Asistente de Flebitis Química';
    iframe.style.cssText = 'width:430px;max-width:92vw;height:670px;max-height:86vh;border-radius:20px;border:1px solid #CBD5E1;box-shadow:0 20px 60px rgba(0,43,102,0.25),0 4px 16px rgba(0,0,0,0.08);display:none;margin-bottom:12px;background:#fff;transition:opacity 0.25s ease,transform 0.25s ease;opacity:0;transform:translateY(10px) scale(0.98);';

    // Button with laCardio heart pulse & branding
    var button = document.createElement('button');
    button.setAttribute('aria-label', 'Abrir Flebitech');
    button.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E4003B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 9v4"/><path d="M10 11h4"/></svg><span style="font-size:14px;font-weight:700;letter-spacing:-0.01em;">Flebitech</span>';
    button.style.cssText = 'height:50px;padding:0 20px;border-radius:25px;background:linear-gradient(135deg,#002B66 0%,#0A3882 100%);color:#fff;border:1px solid rgba(255,255,255,0.15);box-shadow:0 4px 20px rgba(0,43,102,0.35);cursor:pointer;display:flex;align-items:center;font-size:15px;transition:all 0.25s ease;';
    button.onmouseover = function() { button.style.transform = 'translateY(-2px) scale(1.03)'; button.style.boxShadow = '0 6px 25px rgba(0,43,102,0.45)'; };
    button.onmouseout = function() { button.style.transform = 'none'; button.style.boxShadow = '0 4px 20px rgba(0,43,102,0.35)'; };

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
            button.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E4003B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 9v4"/><path d="M10 11h4"/></svg><span style="font-size:14px;font-weight:700;letter-spacing:-0.01em;">Flebitech</span>';
        }
    };

    container.appendChild(iframe);
    container.appendChild(button);
    document.body.appendChild(container);
})();
