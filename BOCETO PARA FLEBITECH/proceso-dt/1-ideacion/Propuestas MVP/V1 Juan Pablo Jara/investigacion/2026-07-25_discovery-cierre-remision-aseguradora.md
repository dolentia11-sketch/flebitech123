# Discovery 25-jul — el cierre real es remisión a la aseguradora

## Hallazgo

Colsubsidio **no vende el seguro directamente**. Actúa como originador: capta el lead, lo remite a la aseguradora del convenio, y esa aseguradora es quien cotiza en firme y recauda la prima. Hoy la remisión es un proceso **manual** (asesor → correo/CRM).

## Métricas del proceso actual (baseline para comparar)

| Métrica | Valor actual |
|---|---|
| Volumen de leads | ~1.200/mes |
| Conversión lead → venta (aseguradora) | ~15% |
| CAC (costo de adquisición del cliente) | ~$40.000 COP |
| Modo de remisión | Manual (asesor) |

## Consecuencias para el MVP

1. **El "cierre" que optimiza el asistente es la remisión**, no la póliza. Toda métrica de éxito del chat se mide contra remisiones (no contra pólizas — esas dependen de la aseguradora).
2. **Nuevo label en la DB de trazabilidad**: `remitido_aseguradora` en `labels` + columna `aseguradora_id` (nullable) en `sessions`. Cambio no rompe nada existente — la sesión dorada del PR #9 sigue con label `compro`.
3. **Copy de Caro** debe reflejarlo: *"te ponemos en contacto con {aseguradora}"* en el cierre, no *"acabas de contratar"*. Nota completa en `producto/dialogos/README.md`.
4. **Oportunidad del pitch**: hoy el proceso manual limita a 1.200 leads/mes con 15% de conversión y CAC $40K. El asistente automatiza la remisión → habilita 10× el volumen sin subir CAC (hipótesis a validar con la aseguradora piloto).

## Preguntas abiertas

- ¿Qué aseguradoras del convenio recibirán la remisión (una vs. multi-canal)?
- ¿Contrato/API para remitir automáticamente vs. seguir email + PDF?
- ¿Consentimiento del habeas data cubre la remisión, o hay que sumar una casilla explícita en el chat?
