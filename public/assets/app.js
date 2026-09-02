// ─── State ───
        let allMedications = [];
        let currentRiskFilter = 'all';
        let sessionQuestions = 0;
        let sessionResolved = 0;
        let chatHistory = [];
        let casesSolved = { 1: false, 2: false, 3: false };

        const sessionId = 'session_' + Math.random().toString(36).substring(2, 9);
        const sidEl = document.getElementById('session-id-display');
        if (sidEl) sidEl.textContent = sessionId;

        // ─── Tab Switching ───
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            const target = document.getElementById('tab-' + tabId);
            const btn = document.getElementById('tab-btn-' + tabId);
            if (target) target.classList.remove('hidden');
            if (btn) btn.classList.add('active');

            if (tabId === 'meds' && allMedications.length === 0) loadMedications();
            if (tabId === 'analytics') loadMetrics();
        }

        // ─── Preset Question ───
        function askPreset(text) {
            document.getElementById('user-input').value = text;
            handleChatSubmit(new Event('submit'));
        }

        // ─── Reset Chat ───
        function resetChat() {
            chatHistory = [];
            const container = document.getElementById('chat-messages');
            container.innerHTML = `
                <div class="flex items-start gap-3 animate-fade-in">
                    <div class="w-9 h-9 rounded-full bg-gradient-to-br from-brand-700 to-brand-900 text-white flex items-center justify-center text-sm shrink-0 shadow-md shadow-brand-900/20">
                        <i class="fa-solid fa-user-nurse"></i>
                    </div>
                    <div class="bubble-ai p-4 max-w-2xl shadow-sm text-sm leading-relaxed border-l-4 border-l-brand-700">
                        <div class="flex items-center justify-between mb-1.5">
                            <p class="font-bold text-brand-700">Conversación reiniciada 🏥</p>
                            <span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Tutor Clínico</span>
                        </div>
                        <p class="text-slate-600">Historial limpiado. ¿En qué fármaco, protocolo o acceso vascular puedo orientarte ahora?</p>
                    </div>
                </div>
            `;
            const input = document.getElementById('user-input');
            if (input) input.focus();
        }

        // ─── Chat Submit ───
        async function handleChatSubmit(e) {
            e.preventDefault();
            const input = document.getElementById('user-input');
            const query = input.value.trim();
            if (!query) return;

            input.value = '';
            input.focus();
            appendMessage('user', query);

            // Add user message to history
            chatHistory.push({ role: 'user', content: query });

            const loadingId = appendLoading();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        session_id: sessionId,
                        // El turno actual viaja en `query`; el historial contiene
                        // únicamente los turnos anteriores para conservar bien
                        // la entidad activa en preguntas de continuación.
                        history: chatHistory.slice(0, -1).slice(-6)
                    })
                });

                if (!res.ok) throw new Error('HTTP ' + res.status);

                const data = await res.json();
                removeLoading(loadingId);
                const answer = typeof data.response === 'string' && data.response.trim()
                    ? data.response
                    : 'La documentación de Flebitech no devolvió una respuesta utilizable. Intenta de nuevo.';
                appendMessage('ai', answer, data.sources || [], data.had_answer === true, data.latency_ms || 0);

                // Add assistant response to history
                chatHistory.push({ role: 'assistant', content: answer });

                // Update session counters
                sessionQuestions++;
                if (data.had_answer) sessionResolved++;
                updateSidebarCounters();
            } catch (err) {
                removeLoading(loadingId);
                appendMessage('ai', '⚠️ Error conectando con el servidor de Flebitech. Verifica que el backend esté en ejecución e intenta nuevamente.', [], false, 0);
            }
        }

        function updateSidebarCounters() {
            const countEl = document.getElementById('sidebar-count');
            const resolvedEl = document.getElementById('sidebar-resolved');
            if (countEl) countEl.textContent = sessionQuestions;
            if (resolvedEl) resolvedEl.textContent = sessionResolved;
        }

        // ─── Copy Message ───
        function copyBubbleText(btn) {
            const bubble = btn.closest('.bubble-ai');
            if (!bubble) return;
            const clone = bubble.cloneNode(true);
            const footer = clone.querySelector('.border-t');
            if (footer) footer.remove();
            const textToCopy = clone.innerText.trim();
            navigator.clipboard.writeText(textToCopy).then(() => {
                const icon = btn.querySelector('i');
                const origClass = icon.className;
                icon.className = 'fa-solid fa-check text-emerald-600';
                setTimeout(() => { icon.className = origClass; }, 1500);
            });
        }

        // ─── Render Messages ───
        function appendMessage(role, text, sources = [], hadAnswer = true, latency = 0) {
            const container = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = 'flex w-full min-w-0 items-start gap-3 animate-slide-up';

            const markdownHtml = typeof marked !== 'undefined'
    ? marked.parse(text, { breaks: true, gfm: true })
    : escapeHtml(text).replace(/\n/g, '<br>');

const htmlContent = typeof DOMPurify !== 'undefined'
    ? DOMPurify.sanitize(markdownHtml, {
        USE_PROFILES: { html: true },
        FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'style', 'form'],
        FORBID_ATTR: ['onerror', 'onload', 'onclick', 'srcdoc']
    })
    : escapeHtml(text).replace(/\n/g, '<br>');

            if (role === 'user') {
                div.innerHTML = `
                    <div class="ml-auto bubble-user p-3.5 max-w-xl min-w-0 break-words text-sm shadow-md leading-relaxed">
                        ${escapeHtml(text)}
                    </div>`;
            } else {
                let sourceBadge = '';
                if (sources && sources.length > 0 && hadAnswer) {
                    const srcNames = sources.map(s => '<span class="font-semibold text-slate-700">' + escapeHtml(s) + '</span>').join(' · ');
                    sourceBadge = `<div class="mt-3 pt-2.5 border-t border-slate-100 text-[11px] text-slate-400 flex flex-wrap items-center justify-between gap-2">
                        <div class="flex min-w-0 flex-wrap items-center gap-1.5 break-words">
                            <i class="fa-solid fa-book-bookmark text-brand-600"></i> Fuentes: ${srcNames} · ${Math.round(latency)} ms
                        </div>
                        <button data-copy-response title="Copiar respuesta" class="text-slate-400 hover:text-brand-700 transition-colors px-1.5 py-0.5 rounded cursor-pointer">
                            <i class="fa-regular fa-copy"></i>
                        </button>
                    </div>`;
                } else if (!hadAnswer) {
                    sourceBadge = `<div class="mt-3 pt-2.5 border-t border-slate-100 text-[11px] text-amber-600 flex items-center justify-between">
                        <div class="flex items-center gap-1.5">
                            <i class="fa-solid fa-circle-exclamation text-amber-500"></i> Fuera de la base indexada de Flebitech
                        </div>
                        <button data-copy-response title="Copiar respuesta" class="text-slate-400 hover:text-brand-700 transition-colors px-1.5 py-0.5 rounded cursor-pointer">
                            <i class="fa-regular fa-copy"></i>
                        </button>
                    </div>`;
                }
                div.innerHTML = `
                    <div class="w-9 h-9 rounded-full bg-gradient-to-br from-brand-700 to-brand-900 text-white flex items-center justify-center text-sm shrink-0 shadow-md shadow-brand-900/20">
                        <i class="fa-solid fa-user-nurse"></i>
                    </div>
                    <div class="bubble-ai min-w-0 flex-1 p-4 max-w-2xl shadow-sm text-sm leading-relaxed border-l-4 ${hadAnswer ? 'border-l-brand-600' : 'border-l-amber-400'}">
                        ${htmlContent}
                        ${sourceBadge}
                    </div>`;
            }
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        function appendLoading() {
            const container = document.getElementById('chat-messages');
            const id = 'loading-' + Date.now();
            const div = document.createElement('div');
            div.id = id;
            div.className = 'flex items-start gap-3 animate-fade-in';
            div.innerHTML = `
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-brand-700 to-brand-900 text-white flex items-center justify-center text-sm shrink-0 shadow-md shadow-brand-900/20">
                    <i class="fa-solid fa-user-nurse"></i>
                </div>
                <div class="bubble-ai p-4 shadow-sm flex items-center gap-2">
                    <div class="flex gap-1">
                        <div class="typing-dot w-2 h-2 rounded-full bg-brand-600"></div>
                        <div class="typing-dot w-2 h-2 rounded-full bg-cardio-500"></div>
                        <div class="typing-dot w-2 h-2 rounded-full bg-brand-600"></div>
                    </div>
                    <span class="text-xs text-slate-400 ml-1">Consultando base documental...</span>
                </div>`;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
            return id;
        }

        function removeLoading(id) {
            const el = document.getElementById(id);
            if (el) el.remove();
        }

        // ─── Medications ───
        async function loadMedications() {
            try {
                const res = await fetch('/api/medications');
                allMedications = await res.json();
                renderMedications(allMedications);
            } catch (e) {
                document.getElementById('meds-container').innerHTML =
                    '<p class="col-span-full text-center text-red-500 py-4">Error cargando medicamentos. Recarga la página.</p>';
            }
        }

        function getRiskClass(risk) {
            const r = (risk || '').toLowerCase();
            if (r.includes('extremo') || r.includes('vesicante')) return 'risk-extreme';
            if (r.includes('muy alto') || r.includes('alto')) return 'risk-high';
            if (r.includes('moderado')) return 'risk-moderate';
            return 'risk-low';
        }

        function filterRisk(risk) {
            currentRiskFilter = risk;
            document.querySelectorAll('.risk-filter-btn').forEach(btn => {
                if (btn.dataset.risk === risk) {
                    btn.className = 'risk-filter-btn px-3 py-1 rounded-full border border-slate-300 font-semibold bg-brand-700 text-white shrink-0';
                } else {
                    btn.className = 'risk-filter-btn px-3 py-1 rounded-full border border-slate-200 font-semibold bg-white text-slate-600 hover:border-brand-400 shrink-0';
                }
            });
            filterMeds();
        }

        function renderMedications(meds) {
            const container = document.getElementById('meds-container');
            if (!meds.length) {
                container.innerHTML = '<p class="col-span-full text-center text-slate-400 py-8">No se encontraron medicamentos con ese criterio.</p>';
                return;
            }
            container.innerHTML = meds.map(m => {
                const riskClass = getRiskClass(m.riesgo_flebitis);
                const centralType = (m.tipo_via_central || 'pendiente_revision').replace(/_/g, ' ');
                const centralSource = m.fuente_via_central || '';
                const centralPending = centralType.includes('pendiente') || centralSource.toLowerCase().includes('pendiente');
                const centralTone = centralPending
                    ? 'bg-amber-50 text-amber-800 border-amber-200'
                    : 'bg-brand-50 text-brand-800 border-brand-200';
                return `
                <div class="p-4 rounded-xl border border-slate-200 bg-white hover:shadow-md hover:border-brand-300 transition-all duration-200 space-y-3 group flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start gap-2">
                            <h4 class="font-bold text-slate-900 text-sm group-hover:text-brand-700 transition-colors">${escapeHtml(m.nombre)}</h4>
                            <span class="px-2 py-0.5 rounded-md text-[10px] font-bold border shrink-0 ${riskClass}">${escapeHtml(m.riesgo_flebitis || '')}</span>
                        </div>
                        <p class="text-xs text-slate-400 mt-0.5">${escapeHtml(m.grupo || '')}</p>
                        <div class="grid grid-cols-2 gap-2 pt-2.5 mt-2 border-t border-slate-100 text-xs">
                            <div><span class="text-slate-400">pH:</span> <code class="font-bold text-slate-700">${escapeHtml(m.ph || '')}</code></div>
                            <div><span class="text-slate-400">Osmolaridad:</span> <code class="font-bold text-slate-700">${escapeHtml(m.osmolaridad || '')}</code></div>
                        </div>
                        <div class="text-xs text-slate-600 space-y-1 mt-2">
                            <p><strong class="text-slate-500">Vía:</strong> ${escapeHtml(m.via_recomendada || '')}</p>
                            <p><strong class="text-slate-500">Vía central:</strong> <span class="inline-flex rounded-md border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${centralTone}">${escapeHtml(centralType)}</span></p>
                            ${centralSource ? `<p class="text-[11px] text-slate-500"><strong>Fuente vía central:</strong> ${escapeHtml(centralSource)}</p>` : ''}
                            <p><strong class="text-slate-500">Diluyente:</strong> ${escapeHtml(m.diluyente_recomendado || '')}</p>
                            <p><strong class="text-slate-500">Infusión:</strong> ${escapeHtml(m.tiempo_infusion_minimo || '')}</p>
                        </div>
                    </div>
                    <div class="pt-2 border-t border-slate-100">
                        <p class="text-[11px] text-amber-900 bg-amber-50/80 rounded-lg p-2 border border-amber-200/60 leading-relaxed">
                            <i class="fa-solid fa-user-nurse text-amber-600 mr-1"></i>
                            ${escapeHtml(m.observaciones_enfermeria || '')}
                        </p>
                    </div>
                </div>`;
            }).join('');
        }

        function filterMeds() {
            const q = document.getElementById('med-search').value.toLowerCase();
            const filtered = allMedications.filter(m => {
                const matchQuery = (m.nombre || '').toLowerCase().includes(q) ||
                                   (m.grupo || '').toLowerCase().includes(q) ||
                                   (m.riesgo_flebitis || '').toLowerCase().includes(q);

                if (!matchQuery) return false;

                if (currentRiskFilter === 'all') return true;
                const r = (m.riesgo_flebitis || '').toLowerCase();
                if (currentRiskFilter === 'extremo') return r.includes('extremo') || r.includes('vesicante');
                if (currentRiskFilter === 'alto') return r.includes('alto') || r.includes('muy alto');
                if (currentRiskFilter === 'moderado') return r.includes('moderado');
                if (currentRiskFilter === 'bajo') return r.includes('bajo') || r.includes('isotónico');
                return true;
            });
            renderMedications(filtered);
        }

        // ─── Clinical Cases ───
        function evaluateCase(caseNum) {
            const feedback = document.getElementById('case' + caseNum + '-feedback');
            feedback.classList.remove('hidden');

            const sel = document.querySelector('input[name="case' + caseNum + '"]:checked');
            if (!sel) {
                feedback.className = 'mt-3 p-4 bg-slate-50 text-slate-600 rounded-xl border border-slate-200 text-sm animate-slide-up';
                feedback.innerHTML = '<i class="fa-solid fa-hand-pointer mr-1"></i> Selecciona una opción antes de evaluar.';
                return;
            }

            const cases = {
                1: {
                    correct: 'B',
                    ok: '✅ <strong>¡Correcto!</strong> Con DIVA = 4 y terapia ácida prolongada (10 días), la indicación de elección es <strong>Línea Media o PICC guiado por ecografía</strong>. La Vancomicina (pH 2.5-4.5) es altamente irritante y requiere un acceso de mayor calibre y duración.',
                    fail: '❌ <strong>Incorrecto.</strong> Canalizar vénulas distales a ciegas con fármacos irritantes como Vancomicina (pH 2.5-4.5) produce flebitis química rápida. Con DIVA 4, se necesita acceso guiado por ecografía.'
                },
                2: {
                    correct: 'B',
                    ok: '✅ <strong>¡Correcto!</strong> En <strong>Flebitis INS Grado 2</strong> (eritema + dolor), el retiro del catéter es mandatorio para evitar progresión a cordón palpable, trombosis o infección.',
                    fail: '❌ <strong>Incorrecto.</strong> Nunca forzar la infusión ni mantener el catéter con signos de flebitis Grado 2. Aumentar la velocidad agrava el daño endotelial.'
                },
                3: {
                    correct: 'B',
                    ok: '✅ <strong>¡Correcto!</strong> La NPT con osmolaridad >900 mOsm/L es <strong>obligatoriamente de Vía Central</strong> (CVC o PICC con punta en vena cava superior). Nunca se administra periféricamente.',
                    fail: '❌ <strong>Incorrecto.</strong> La NPT con osmolaridad de 1200 mOsm/L supera ampliamente el umbral de 900 mOsm/L. Es mandatorio administrar exclusivamente por Vía Central. Diluirla alteraría su formulación nutricional.'
                }
            };

            const c = cases[caseNum];
            if (sel.value === c.correct) {
                feedback.className = 'mt-3 p-4 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-sm animate-slide-up';
                feedback.innerHTML = c.ok;
                casesSolved[caseNum] = true;
            } else {
                feedback.className = 'mt-3 p-4 bg-red-50 text-red-800 rounded-xl border border-red-200 text-sm animate-slide-up';
                feedback.innerHTML = c.fail;
            }

            const totalSolved = Object.values(casesSolved).filter(Boolean).length;
            const badge = document.getElementById('cases-score-badge');
            if (badge) badge.textContent = `Casos resueltos: ${totalSolved}/3`;
        }

        // ─── Metrics ───
        async function loadMetrics() {
            try {
                const res = await fetch('/api/metrics?session_id=' + sessionId);
                const data = await res.json();

                document.getElementById('metric-total').textContent = data.stats.total_preguntas;
                document.getElementById('metric-answered').textContent = data.stats.respondidas;
                document.getElementById('metric-gaps').textContent = data.stats.brechas_detectadas;
                document.getElementById('metric-rate').textContent = data.stats.tasa_resolucion + '%';

                const recentEl = document.getElementById('recent-list');
                if (data.recent && data.recent.length > 0) {
                    recentEl.innerHTML = data.recent.map(r => `
                        <div class="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-start gap-2">
                            <span class="shrink-0 mt-0.5 ${r.had_answer ? 'text-emerald-500' : 'text-cardio-500'}">
                                <i class="fa-solid ${r.had_answer ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
                            </span>
                            <div class="min-w-0">
                                <p class="font-semibold text-slate-700 text-xs">Consulta registrada</p>
                                <p class="text-[11px] text-slate-400 mt-0.5">${escapeHtml(r.topic || '')} · ${escapeHtml(r.timestamp || '')}</p>
                            </div>
                        </div>
                    `).join('');
                } else {
                    recentEl.innerHTML = '<p class="text-slate-400 text-center py-4">Sin consultas registradas.</p>';
                }

                const gapsEl = document.getElementById('gaps-list');
                if (data.gaps && data.gaps.length > 0) {
                    gapsEl.innerHTML = data.gaps.map(g => `
                        <div class="p-3 bg-cardio-50/70 text-cardio-900 rounded-lg border border-cardio-200/60 text-xs">
                            <p class="font-semibold">Brecha registrada</p>
                            <p class="text-cardio-700 mt-0.5">${escapeHtml(g.topic || '')} · ${escapeHtml(g.timestamp || '')}</p>
                        </div>
                    `).join('');
                } else {
                    gapsEl.innerHTML = '<p class="text-emerald-600 font-semibold text-center py-4">🎉 Sin brechas de conocimiento pendientes.</p>';
                }
            } catch (e) {
                console.error('Error loading metrics:', e);
            }
        }

        // ─── Keyboard shortcut ───
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
                e.preventDefault();
                document.getElementById('user-input').focus();
            }
        });

        // Los manejadores viven aquí, no en atributos HTML. Así la CSP puede
        // bloquear JavaScript inline inyectado sin alterar los flujos visibles.
        document.addEventListener('click', (event) => {
            const button = event.target.closest('button');
            if (!button) return;

            if (button.dataset.tab) switchTab(button.dataset.tab);
            if (button.dataset.preset) askPreset(button.dataset.preset);
            if (button.id === 'reset-chat') resetChat();
            if (button.classList.contains('risk-filter-btn')) filterRisk(button.dataset.risk);
            if (button.dataset.case) evaluateCase(Number(button.dataset.case));
            if (button.id === 'refresh-metrics') loadMetrics();
            if (button.hasAttribute('data-copy-response')) copyBubbleText(button);
        });

        document.getElementById('chat-form').addEventListener('submit', handleChatSubmit);
        document.getElementById('med-search').addEventListener('input', filterMeds);
