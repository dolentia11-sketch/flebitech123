# Etapa 1 — Preparar la línea base sin tocar el chatbot

## Objetivo

Crear un punto seguro de comparación. En esta etapa no se cambia ninguna respuesta, regla clínica, prompt, API ni interfaz; solo se registra evidencia verificable del estado inicial y de los riesgos abiertos.

## Paso 1. Clonar y verificar el commit

```bash
git clone https://github.com/dolentia11-sketch/flebitech_bot.git
cd flebitech_bot
git switch master
git pull --ff-only
git rev-parse --short HEAD
git status
```

Registra el SHA mostrado. La auditoría se realizó sobre `1e82f71`; si el SHA actual es distinto, anota el nuevo punto de partida antes de modificar nada.

## Paso 2. Crear entorno virtual

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si una dependencia falla, detente y registra el error. No cambies versiones al azar.

## Paso 3. Ejecutar la línea base existente

```bash
python -m compileall -q backend api app.py indexer.py dev_server.py
python test_conversacional.py
python test_orchestrator.py
python test_mock_1000.py
python test_flebitech.py
```

Resultado esperado según la auditoría:

- compilación sin errores;
- `test_conversacional.py`: 39/39;
- `test_mock_1000.py`: 1,000/1,000;
- las pruebas de API requieren todas las dependencias instaladas.

## Paso 4. Crear un registro de línea base

Crea `docs/LINEA_BASE.md` con esta plantilla:

```markdown
# Línea base de Flebitech

- Fecha:
- Rama:
- Commit:
- Python:
- Sistema operativo:
- Pruebas conversacionales:
- Pruebas de API:
- Prueba mock:
- Hallazgos abiertos:
- Riesgos aceptados temporalmente:
- Versiones de Python probadas:
- Responsable:
```

No incluyas claves, consultas reales ni datos de pacientes.

No escribas “ninguno” si el plan ya identifica vulnerabilidades residuales. Si una prueba pasa, registra el resultado; si un riesgo sigue abierto, regístralo como pendiente.

## Paso 5. Crear rama para la primera corrección

```bash
git switch -c fix/clinical-central-route
git status
```

## Paso 6. Confirmar que el árbol está limpio

Antes de la primera modificación:

```bash
git status --short
```

Solo debería aparecer `docs/LINEA_BASE.md` si decidiste guardarlo. Haz un commit separado:

```bash
git add docs/LINEA_BASE.md
git commit -m "docs: registrar linea base antes del endurecimiento"
```

## Lista de comprobación

- [ ] Conozco el commit exacto de partida.
- [ ] Instalé dependencias en un entorno virtual.
- [ ] Ejecuté todas las pruebas disponibles.
- [ ] Guardé los resultados reales.
- [ ] Registré hallazgos abiertos sin declararlos como errores ausentes.
- [ ] Diferencié Python local de Python usado por CI.
- [ ] Creé una rama exclusiva para la vía central.
- [ ] No modifiqué código de producción.

Cuando todo esté marcado, continúa con `02_CORREGIR_VIA_CENTRAL.md`.
