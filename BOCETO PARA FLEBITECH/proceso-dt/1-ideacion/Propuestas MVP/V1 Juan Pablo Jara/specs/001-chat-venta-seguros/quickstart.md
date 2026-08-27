# Quickstart — validar el demo end-to-end

Guía de validación (no de implementación). Si estos pasos pasan, la P1 está viva.

## Prerrequisitos

- Python 3.11+ (el motor corre con stdlib; `pytest` para casos dorados)
- Navegador
- (Opcional) API key de Gemini — sin ella el chat corre con plantillas de fallback

## Arranque

```bash
cd producto/engines
python3 -m pytest tests/test_casos_dorados.py   # motor OK: 2 perfiles → resultados fijos
python3 servidor.py                              # o el transporte que decida el equipo dev (D4)
# abrir producto/demo/index.html (o la URL local que sirva el backend)
```

## Validación P1 (los 3 caminos del demo)

**Camino 1 — afiliada sin intención (perfil ancla del pitch):**
mujer 29, monoparental, categoría A, ingreso 1–1,5 SMLV.
Esperado: ≤5 preguntas (varias pre-respondidas por su perfil) → UNA recomendación
con "por qué" → prima del motor → consentimiento inline → póliza COL-2026-XXXXX
con hash → cierre celebratorio. Todo en <3 min.

**Camino 2 — usuario con intención:** escribir "quiero un SOAT".
Esperado: sin descubrimiento completo; SOAT (tarifa pública real) + 2 alternativas
rankeadas por score con primas del motor.

**Camino 3 — no afiliado:** elegir "no soy afiliado".
Esperado: 5 preguntas completas → venta normal → al cierre, oferta de afiliación
(lead registrado).

## Validación de trazabilidad (pregunta del jurado, SC-003)

```bash
sqlite3 producto/engines/db/trazabilidad.db \
  "SELECT paso, dato_json, timestamp FROM evento_trazabilidad WHERE serie='DEMO-00123' ORDER BY timestamp;"
sqlite3 producto/engines/db/trazabilidad.db \
  "SELECT numero, prima, hash, consentimiento_ts FROM poliza;"
```
Esperado: cadena completa señal → score → oferta → decisión, y póliza con hash y
consentimiento. Responde "¿por qué esta cifra?" en <30 s.

## Validación P3 (abandono)

Llegar a la pantalla de precio y cerrar. Esperado: fila `abandono` con punto de
fuga en `evento_trazabilidad`. Pedir "seguro de vida con asesoría" → oferta de
derivación a humano antes de emitir.

## Checklist pre-demo (domingo)

- [ ] 2 perfiles demo producen recomendaciones y primas DISTINTAS y explicables (SC-001)
- [ ] Flujo en vivo ≥60 s sin cortes, guion total ≤3 min (SC-002)
- [ ] Al menos una bifurcación mostrada en vivo (SC-005)
- [ ] Cero nombres/datos reales en pantalla, DB y logs (SC-004)
- [ ] Matar el LLM (sin API key) y verificar que el flujo completo sigue corriendo con plantillas

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24*
