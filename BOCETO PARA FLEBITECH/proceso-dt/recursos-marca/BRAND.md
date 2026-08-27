# Marca Colsubsidio — tokens oficiales

Fuente: brandbook compartido por la organización (Drive del reto, 23-jul-2026).
Archivos originales en esta carpeta. Este doc existe para que cualquier sesión de
Claude Code (o cualquier persona) use la marca sin interpretar imágenes.

## Paleta oficial

| Color | Pantone | HEX | RGB | CMYK | Tints permitidos |
|---|---|---|---|---|---|
| **Amarillo Colsubsidio** | 109 C | `#FFD000` | 255, 208, 0 | 0 18 100 0 | 80% · 60% · 40% |
| **Azul Colsubsidio** | 2196 C | `#0067B1` | 0, 103, 177 | 90 55 0 0 | 80% · 60% · 40% |
| **Grafito** | Cool Gray 11 C | `#575756` | 87, 87, 87 | 0 0 0 80 | 60% · 40% · 20% |

### Variables listas para copiar

```css
:root {
  --colsubsidio-amarillo: #FFD000;
  --colsubsidio-azul: #0067B1;
  --colsubsidio-grafito: #575756;
  /* tints (sobre blanco) */
  --colsubsidio-amarillo-80: #FFD933;
  --colsubsidio-amarillo-60: #FFE366;
  --colsubsidio-amarillo-40: #FFEC99;
  --colsubsidio-azul-80: #3385C1;
  --colsubsidio-azul-60: #66A4D0;
  --colsubsidio-azul-40: #99C2E0;
  --colsubsidio-grafito-60: #9A9A99;
  --colsubsidio-grafito-40: #BCBCBB;
  --colsubsidio-grafito-20: #DDDDDD;
}
```

```python
COLSUBSIDIO = {"amarillo": "#FFD000", "azul": "#0067B1", "grafito": "#575756"}
```

Nota: los tints hex son equivalencia calculada del % sobre blanco (el brandbook los
define como porcentajes de tinta; ver `Colores Oficiales.png` para la referencia
visual exacta).

## Logos

| Archivo | Qué es | Cuándo usarlo |
|---|---|---|
| `LogoV1.png` | Isotipo amarillo (#FFD000) + wordmark BLANCO · 1200×1200, fondo transparente | Sobre fondos oscuros o azul Colsubsidio. ⚠️ Invisible sobre blanco |
| `Logov2.png` | Logo horizontal TODO blanco · 820×174, fondo transparente | Sobre fotografías o fondos de color. ⚠️ Invisible sobre blanco |
| `Colores Oficiales.png` | Lámina de la paleta con Pantone/CMYK/RGB/HEX y tints | Referencia visual |

⚠️ **No hay en el paquete una versión del logo para fondo claro** (wordmark azul o
grafito). Si el frontend del MVP usa fondo blanco, opciones: usar solo el isotipo
amarillo (recortarlo de LogoV1), poner el logo sobre una franja azul `#0067B1`, o
pedir a la organización la versión positiva.

## Uso rápido en el MVP

- Fondo de marca: azul `#0067B1` con acentos amarillo `#FFD000`
- CTA/botones: amarillo `#FFD000` con texto grafito `#575756` (mejor contraste que
  texto blanco sobre amarillo)
- Texto sobre blanco: grafito `#575756` (no negro puro)
- El chat puede usar azul para burbujas del sistema y amarillo solo como acento
  (precio, número de póliza, CTA)
