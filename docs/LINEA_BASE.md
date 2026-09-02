# Línea base de Flebitech

- Fecha: 2026-09-02
- Rama auditada: `master`
- Commit auditado localmente: `21502c1`
- Commit remoto confirmado en GitHub: `21502c111f1202e80f3a64c2e4fe0fb1d393daa8`
- Python local usado en la línea base previa: 3.14.6
- Python de CI declarado: 3.11
- Sistema operativo local: Windows
- Pruebas conversacionales previas: 39/39
- Pruebas de API heredadas previas: 225/225
- Prueba mock previa: 1000/1000
- Responsable del registro previo: Antigravity

## Alcance

Esta línea base no certifica ausencia de defectos. Solo registra el punto de comparación antes de endurecer la superficie clínica, de privacidad, seguridad de frontend y CI.

## Hallazgos residuales abiertos

| ID | Severidad | Hallazgo | Estado |
|---|---|---|---|
| A-01 | Alta | Métricas accesibles por `session_id` de navegador, sin identidad autenticada. El payload ya no incluye consultas ni respuestas. | Mitigado; requiere control de acceso |
| A-02 | Alta | Clasificación de vía central aún sin fuente clínica validada. | Pendiente |
| A-03 | Alta | Cobertura de seguridad incompleta. Pytest ya cubre API/privacidad/frontend y CI exige 55 %, pero falta protección de rama. | Mitigado; requiere gobernanza de GitHub |
| A-04 | Media | `history` y el cuerpo de `/api/chat` carecían de límites aplicados antes del procesamiento. | Corregido en API |
| A-05 | Media | `.env.example` contenía bytes NUL en `FLEBITECH_CORS_ORIGINS`. | Corregido en superficie de configuración |
| A-06 | Media | Dependencias sin lockfile o restricciones reproducibles. | Corregido con `requirements.lock` y versiones directas fijadas |
| A-07 | Media | Prompt injection evaluado principalmente de forma estructural. | Mitigado con prueba canario; falta evaluación contra proveedor real |
| A-08 | Media | CDN sin CSP/SRI y Marked sin versión fijada. | Mitigado con CSP, SRI y versión fijada; falta revisión de despliegue |
| A-09 | Baja | README y línea base contenían inconsistencias de BM25/TF-IDF y Markdown. | Corregido en documentación |
| A-10 | Baja | Binarios eliminados permanecen en historia Git; requiere procedimiento aprobado. | Pendiente |

## Compatibilidad mínima a demostrar

- CI: Python 3.11.
- Desarrollo local: Python 3.11 recomendado.
- Cualquier ejecución en Python 3.14 debe considerarse informativa hasta que la matriz de compatibilidad la incluya explícitamente.

## Regla de auditoría

No usar “sin errores” o “validado” para cerrar una etapa si existen hallazgos residuales documentados. El cierre debe indicar qué quedó corregido, qué quedó mitigado y qué requiere aprobación clínica, control de acceso o política de repositorio.

## Evidencia técnica de esta consolidación

- `/api/chat` limita el cuerpo a 18 KiB y `history` a 8 mensajes antes de llegar al orquestador.
- `/api/metrics` expone únicamente marca de tiempo, tema y resultado; nunca transcripciones, consultas ni respuestas.
- `public/index.html` usa CSP con hashes para sus dos scripts locales, SRI para las cuatro dependencias externas y manejadores sin atributos `on*`.
- `requirements.lock` fija el árbol de dependencias usado por CI; el umbral de cobertura inicial es 55 %.
- La evidencia es local hasta que se confirme un run de CI sobre Python 3.11 y se habilite la protección de `master`.
