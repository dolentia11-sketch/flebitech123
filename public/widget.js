(function() {
    // Flebitech Floating Widget para Genially / LMS / Web
    const scriptTag = document.currentScript;
    const origin = scriptTag ? new URL(scriptTag.src).origin : window.location.origin;

    const container = document.createElement('div');
    container.id = 'flebitech-widget-root';
    container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:999999;font-family:sans-serif;display:flex;flex-direction:column;align-items:flex-end;';

    const iframe = document.createElement('iframe');
    iframe.src = origin + '/';
    iframe.style.cssText = 'width:400px;max-width:90vw;height:620px;max-height:85vh;border-radius:20px;border:1px solid #CBD5E1;box-shadow:0 15px 35px rgba(0,0,0,0.25);display:none;margin-bottom:14px;background:#fff;';

    const button = document.createElement('button');
    button.innerHTML = '🏥 <span style=\"font-size:13px;font-weight:700;margin-left:4px;\">Flebitech</span>';
    button.style.cssText = 'height:50px;padding:0 20px;border-radius:25px;background:#004080;color:#fff;border:none;box-shadow:0 4px 15px rgba(0,64,128,0.4);cursor:pointer;display:flex;align-items:center;font-size:18px;transition:transform 0.2s;';
    
    button.onmouseover = () => button.style.transform = 'scale(1.05)';
    button.onmouseout = () => button.style.transform = 'scale(1)';

    button.onclick = () => {
        const isHidden = iframe.style.display === 'none';
        iframe.style.display = isHidden ? 'block' : 'none';
    };

    container.appendChild(iframe);
    container.appendChild(button);
    document.body.appendChild(container);
})();
