# Endurecimiento por etapas

Fecha de consolidación: 2026-09-02  
Repositorio: `dolentia11-sketch/flebitech_bot`  
Rama auditada: `master`  
Commit remoto confirmado: `21502c111f1202e80f3a64c2e4fe0fb1d393daa8`  
Protección de rama en GitHub: no habilitada para `master`

## Regla de alcance

No cambiar arquitectura, contratos principales ni lógica clínica sin revisión. Este plan solo endurece las zonas donde el sistema muestra, registra o comunica vulnerabilidades:

- textos de documentación y línea base;
- mensajes clínicos que pueden inducir falsa validación;
- etiquetas visibles de estado clínico y privacidad;
- criterios de cierre y evidencia requerida por etapa.

## Etapa 1 - Línea base y control de alcance

Estado: parcial.

La línea base registra rama, commit y resultados previos, pero no debe afirmar ausencia de errores. La ejecución local previa usó Python 3.14.6, mientras CI declara Python 3.11; por tanto, la compatibilidad real queda limitada a lo que CI ejecute y publique.

Riesgo residual:

- la línea base anterior declaraba “Errores encontrados: Ninguno” pese a hallazgos abiertos;
- README describía TF-IDF aunque el motor aplica BM25;
- había cercas Markdown dañadas por caracteres de control;
- no existía matriz explícita entre Python local y CI.

Requisito de cierre:

- línea base con hallazgos abiertos y commit exacto;
- README consistente con BM25;
- Markdown legible;
- CI publicado sobre Python 3.11;
- cualquier otra versión de Python tratada como informativa hasta incorporarse a matriz.

## Etapa 2 - Seguridad clínica de vía central

Estado: funcional en código; pendiente de gobernanza clínica.

La respuesta a “¿Qué medicamentos requieren vía central obligatoria?” filtra `exclusiva` y excluye medicamentos condicionados. Esto corrige el falso positivo funcional, pero no valida clínicamente las fichas.

Distribución actual de las 15 fichas:

| Clasificación | Cantidad | Situación |
|---|---:|---|
| `exclusiva` | 1 | NPT |
| `condicionada` | 4 | Vancomicina, KCl, amiodarona y DAD 50% |
| `pendiente_revision` | 10 | Sin criterio ni fuente estructurada |

Riesgo residual:

- las fichas exclusiva/condicionada usan `PENDIENTE: referencia institucional validada`;
- cualquier texto visible que diga “validada” genera falsa confianza clínica;
- una clasificación operativa no equivale a aprobación institucional.

Requisito de cierre:

- revisar las 15 fichas con farmacia/enfermería;
- registrar fuente primaria, versión, fecha y aprobador;
- no usar “validada” mientras `fuente_via_central` siga pendiente;
- mostrar estado de fuente en las superficies clínicas.

## Etapa 3 - Métricas, sesiones y privacidad

Estado: mitigación parcial; riesgo residual alto.

El filtro por `session_id` reduce cruces accidentales y el contrato público de métricas ya omite consultas, respuestas, fuentes e identificadores de la transcripción. `session_id` sigue siendo un identificador generado en navegador, no una credencial ni un vínculo autenticado con un usuario.

Riesgo residual:

- el endpoint acepta cualquier identificador válido suministrado por el solicitante;
- el endpoint acepta cualquier identificador válido suministrado por el solicitante y por ello aún puede revelar metadatos de actividad;
- no hay retención, anonimización ni consentimiento explícito para datos clínicos escritos por el usuario;
- SQLite en memoria en Vercel reduce persistencia accidental, pero no es control de acceso.

Requisito de cierre:

- proteger o retirar `/api/metrics` público;
- vincular sesión a identidad autorizada si se conserva el endpoint;
- devolver solo campos mínimos necesarios;
- documentar retención y consentimiento;
- agregar pruebas que verifiquen ausencia de `response` en el payload público.

## Etapa 4 - Prompt injection, historial y XSS

Estado: mitigación técnica parcial; pruebas de seguridad aún incompletas.

La API rechaza roles no permitidos, limita `history` a 8 mensajes y el cuerpo de `/api/chat` a 18 KiB. El frontend sanitiza Markdown con DOMPurify, fija Marked 15.0.7 y aplica SRI/CSP. Los atributos de evento inline se sustituyeron por manejadores registrados desde el script autorizado por hash.

Evidencia local de DOM (2026-09-02): un payload con `<script>`, `onerror` y URL `javascript:` se renderizó sin ejecución, sin nodos `script`, sin atributos de evento y sin enlaces `javascript:`. La navegación a Medicamentos también confirmó que los manejadores registrados mantienen la interacción visible.

Riesgo residual:

- no existe evaluación contra un proveedor real para medir incumplimientos ante un corpus adversarial;
- el canario comprueba que un secreto de entorno no se promueve a instrucciones de sistema, pero no sustituye una evaluación extremo a extremo;
- el widget embebible impide usar una política global `frame-ancestors 'self'` o `X-Frame-Options: DENY` sin cambiar su funcionalidad;
- falta una prueba automatizada de XSS con DOM real en CI.

Requisito de cierre:

- limitar cantidad total de mensajes y tamaño de cuerpo HTTP;
- crear corpus adversarial con ataques directos, indirectos, extracción de prompt y exfiltración;
- probar con un secreto canario, no con el nombre de la variable;
- fijar Marked o servir dependencias localmente;
- agregar CSP/SRI o política equivalente;
- validar XSS con navegador automatizado.

## Etapa 5 - Pruebas automáticas y CI

Estado: CI reforzado localmente; garantía de repositorio incompleta.

CI ejecuta los scripts heredados, pytest con cobertura de `backend` y `api`, e impone un umbral inicial de 55 %. Se añadieron pruebas de límites de API, privacidad, canario de prompt y configuración de frontend. `requirements.lock` fija las restricciones transitivas para Python 3.11.

Riesgo residual:

- scripts heredados no contribuyen al informe de cobertura final;
- Ruff todavía no cubre scripts raíz y no hay linter JavaScript/HTML en CI;
- GitHub reporta `master` sin protección de rama.

Requisito de cierre:

- migrar pruebas API y seguridad a pytest;
- incluir cobertura de `api/index.py`;
- definir umbral progresivo de cobertura;
- revisar lint/format de scripts raíz y frontend;
- añadir lockfile o constraints reproducibles;
- exigir check de CI obligatorio antes del merge.

## Cierre de las primeras cinco etapas

| Etapa | Evidencia ya incorporada | Para declararla cerrada |
|---|---|---|
| 1. Línea base | Hallazgos y matriz Python/CI documentados; configuración de entorno normalizada. | Confirmar un run recuperable de CI Python 3.11 sobre el commit a fusionar. |
| 2. Vía central | Clasificación exclusiva/condicionada separada y fuente visible como pendiente. | Farmacia/enfermería debe aprobar las 15 fichas con fuente, versión, fecha y aprobador. |
| 3. Métricas | El endpoint devuelve solo metadatos; prueba asegura ausencia de consulta/respuesta. | Retirar o proteger el endpoint con identidad autorizada y definir retención/consentimiento. |
| 4. Entrada y XSS | Límite 18 KiB/8 mensajes, canario, CSP/SRI y DOMPurify. | Ejecutar y conservar prueba XSS en DOM real y evaluación adversarial contra proveedor real. |
| 5. CI | `requirements.lock`, pruebas de seguridad/API y cobertura mínima 55 %. | Publicar CI verde en Python 3.11, cubrir scripts raíz/frontend y hacer obligatorio el check en `master`. |

## Hallazgos priorizados

| ID | Severidad | Hallazgo | Requisito de cierre |
|---|---|---|---|
| A-01 | Alta | Métricas sin autenticación/autorización; el payload ya está minimizado. | Proteger o retirar endpoint público y vincular sesión a identidad autorizada. |
| A-02 | Alta | Clasificación clínica presentada como validada sin fuente validada. | Revisar 15 fichas; registrar fuente, versión, fecha y aprobador; no usar “validada” mientras esté pendiente. |
| A-03 | Alta | Cobertura de seguridad aún incompleta, con umbral técnico inicial de 55 %. | Ampliar cobertura, ejecutar CI en Python 3.11 y exigirlo antes del merge. |
| A-04 | Media | Historial y cuerpo HTTP sin límite previo. | Corregido: 8 mensajes y 18 KiB; conservar prueba de regresión. |
| A-05 | Media | `.env.example` tenía codificación mixta con bytes NUL. | Normalizar a UTF-8 y mantener ejemplo verificable. |
| A-06 | Media | Dependencias no bloqueadas. | Corregido con restricciones fijadas; mantener política de actualización. |
| A-07 | Media | Defensa de prompt evaluada solo estructuralmente. | Ampliar corpus adversarial y evaluar tasa de incumplimiento del proveedor real. |
| A-08 | Media | CDN sin CSP/SRI y Marked sin versión. | Mitigado con versión fijada, SRI, CSP y prueba DOM local; validar en despliegue/CI. |
| A-09 | Baja | README y línea base inconsistentes. | Corregir BM25, cercas Markdown y criterios de línea base. |
| A-10 | Baja | Binarios eliminados permanecen en historia Git. | Evaluar limpieza de historia solo con procedimiento aprobado. |
