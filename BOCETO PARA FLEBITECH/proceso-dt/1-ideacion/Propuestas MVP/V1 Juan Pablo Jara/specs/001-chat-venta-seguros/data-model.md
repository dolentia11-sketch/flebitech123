# Data Model — 001 · Agente de venta de seguros (Phase 1)

Esquema único, una sola DB (FR-008). Base: `schema_seguros.sql` de JD, extendido
con lo que la spec v2 exige. Todo dato de persona es sintético (constitución III).

## Entidades

### usuario_demo
| Campo | Tipo | Notas |
|---|---|---|
| serie | TEXT PK | SERIE sintética; para no afiliados: `LEAD-XXXX` |
| es_afiliado | BOOLEAN | bifurcación paso 0 |
| segmento | TEXT | valor enmascarado de base v2, usado sin interpretar |
| categoria | TEXT | A/B/C |
| rango_salarial | TEXT | banda SMLV (legible en base v2) |
| rango_edad | TEXT | V1 del modelo de scoring |
| genero | TEXT | V2 |
| situacion_laboral | TEXT | V3 (declarada en chat si no afiliado) |
| composicion_familiar | TEXT | V5 |

### producto (catálogo JSON, no tabla — se carga en memoria)
| Campo | Notas |
|---|---|
| id, nombre, familia | 26 productos, 7 familias |
| aseguradora, url | MetLife/Chubb/BMI/SURA |
| prima_base, cobertura_base | simuladas salvo SOAT (tarifa pública) |
| tipo_venta | **nuevo v2**: `automatica` \| `asistida` (clasificación de Caro) |
| sinonimos_intencion | **nuevo v2**: palabras clave para la bifurcación de intención (D7) |

### score_resultado
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| serie | FK usuario_demo | |
| variables_json | TEXT | claves V1..V7 usadas (traza de explicabilidad, SC-003) |
| ranking_json | TEXT | [{producto_id, puntaje}] ordenado |
| timestamp | DATETIME | |

### cotizacion
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| serie, producto_id | FK | |
| prima | INTEGER | COP/mes, calculada por el motor |
| veredicto_idoneidad | TEXT | apto / alternativa_asequible / asistida |
| variables_json | TEXT | qué entró al cálculo |
| score_id | FK score_resultado | encadena la traza |

### poliza
| Campo | Tipo | Notas |
|---|---|---|
| numero | TEXT PK | formato COL-2026-XXXXX |
| serie, producto_id, prima | | |
| consentimiento_texto | TEXT | frase aceptada, inline |
| consentimiento_ts | DATETIME | |
| hash | TEXT | sha256(numero+serie+producto+prima+ts) — trazabilidad |
| cotizacion_id | FK | cierra la cadena señal→score→oferta→decisión |

### evento_trazabilidad
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| serie | TEXT | o LEAD-XXXX |
| paso | TEXT | maquina de estados: `paso0`, `intencion`, `p1`..`p5`, `precio`, `consentimiento`, `cierre`, `abandono`, `derivacion`, `lead_afiliacion`, `paquete` |
| dato_json | TEXT | respuesta/valor capturado |
| timestamp | DATETIME | |

## Reglas de validación

- Ninguna fila de `poliza` sin `consentimiento_ts` y sin `cotizacion_id` (constitución II).
- `cotizacion.prima` solo la escribe el motor (la UI nunca envía primas).
- `evento_trazabilidad` se escribe en CADA transición de estado, incluido abandono (FR-008).
- Producto con `tipo_venta = asistida` → el flujo debe ofrecer derivación antes de emitir (US3).

## Transiciones de estado (máquina del chat)

```
inicio → paso0(afiliado?) → intencion(¿sabe qué quiere?)
  ├─ con intención → oferta(pedido + 2 alternativas por score) → precio
  └─ sin intención → p1..p5 (descubrimiento) → recomendación → precio
precio → consentimiento → poliza_emitida → cierre [→ paquete_sugerido (P2)]
precio → abandono (registra fuga)                     [P3]
cualquier_punto → derivacion_asesor (si asistida)     [P3]
cierre (no afiliado) → lead_afiliacion
```

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24*
