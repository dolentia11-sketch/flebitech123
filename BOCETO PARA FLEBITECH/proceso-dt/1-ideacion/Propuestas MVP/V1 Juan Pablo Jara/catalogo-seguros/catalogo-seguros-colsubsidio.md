# Catálogo de seguros Colsubsidio — Reto 02 (v2)

Recopilado el 2026-07-22 desde las páginas oficiales de `colsubsidio.com/seguros`, sus
subpáginas de producto, clausulados PDF y páginas de aliados (Chubb, Sura). **26
productos** en 7 familias; **23 relevantes** para la venta individual del reto.

> **v2:** corregida tras revisión multiagéntica. Cambios: SOAT reestructurado como
> producto ancla con sus coberturas legales y tarifa regulada; agregados los productos
> Chubb que faltaban (Protección Urbana, AP Digital, AP Chubb), la asistencia médica en
> viajes y la medicina prepagada de mascotas; corregida la contradicción Chubb/MetLife
> en accidentes personales; URL rota de incendio reemplazada.

> **Colsubsidio es sponsor, no asegurador.** Distribuye pólizas de varias aseguradoras.
> El flujo del reto ayuda a elegir el producto adecuado del catálogo y a vincularse.

> **Sobre precios:** las primas **no son públicas** (la web exige cotización) y se
> simulan en el MVP — **excepto el SOAT**, cuya tarifa es regulada y pública (la fija
> anualmente la Superintendencia Financiera por tipo de vehículo, cilindraje y
> antigüedad). En la demo, el SOAT debe usar tarifa real, no simulada.

> **Formas de pago (dato, no recomendación):** cupo de crédito de la Tarjeta de
> Afiliación, cuota monetaria, u otro canal autorizado por la aseguradora. Además, el
> doc oficial del reto de crédito lista un "crédito rotativo para seguros e impuestos"
> (hasta $5.000.000, plazos hasta 11 meses). Si financiar primas con crédito es buena
> idea para categoría A es **decisión del equipo** — tiene el trade-off obvio de
> convertir el seguro en deuda con costo financiero.

## ⭐ SOAT — nota destacada

Según los organizadores (presentación en vivo del reto, 22-jul), **SOAT es una de las
líneas de seguros con mayor volumen de ventas de Colsubsidio**. Características que lo
hacen relevante para el diseño del flujo:

- **Obligatorio por ley** para todo vehículo → demanda garantizada.
- **Renovación anual** → contacto recurrente natural con el afiliado (posible puerta de
  entrada y momento de venta cruzada, a evaluar en equipo).
- **Tarifa regulada y pública** → es el único producto donde la demo puede mostrar
  precio real.
- Coberturas legales: gastos médicos por accidente de tránsito, incapacidad permanente,
  muerte y gastos funerarios, transporte de víctimas.

## Aseguradoras aliadas identificadas

| Aseguradora | Respalda |
|---|---|
| **MetLife Colombia Seguros de Vida** | Accidentes personales (clausulado propio); vida con anexo de desempleo del crédito de consumo |
| **Chubb Seguros Colombia** | Oncológico, Protección Urbana, Accidentes Personales (anual), AP Digital |
| **BMI Seguros Colombia** | Exequial / funerario; Vida y Ahorro (por confirmar) |
| **Seguros SURA** | Arrendamiento digital |

Nota: en accidentes personales **coexisten dos productos** (clausulado MetLife y
paquete Chubb). Confirmar cuál vende el canal que simule el MVP.

---

## 1. Vida y exequial (8)

| Producto | Cubre | Dirigido a | Aseguradora |
|---|---|---|---|
| **Seguro de Vida** (personal y familiar) | Fallecimiento, incapacidad, respaldo a beneficiarios | Personas/familias que protegen su ingreso | — |
| **Vida y Ahorro (Doble Beneficio)** | Fallecimiento accidental + capital creciente + ahorro | Quien protege y ahorra a la vez | BMI (por confirmar) |
| **Accidentes Personales (MetLife)** | Muerte accidental, atraco, incapacidad, gastos médicos y funerarios | Entrada de bajo costo | MetLife |
| **Accidentes Personales (Chubb, anual)** | AP cobertura básica anual | Paquete Chubb-Colsubsidio | Chubb |
| **AP Digital (Chubb)** | AP por canal digital | Venta digital — encaja con el funnel del reto | Chubb |
| **Protección Urbana (Chubb)** | Riesgos urbanos | Afiliados en entornos urbanos | Chubb |
| **Accidentes + Exequial** | Muerte accidental + servicio exequial | Ambos en un producto | — |
| **Exequial (funerario)** | Gastos funerarios completos | Cubrir funeral propio y del grupo | BMI |

## 2. Salud y asistencias (4)

| Producto | Cubre | Dirigido a | Aseguradora |
|---|---|---|---|
| **Oncológico (Chubb)** | Diagnóstico/tratamiento de cáncer, suma asegurada | Protección financiera ante el cáncer (el Crédito Mujer lo incluye como beneficio) | Chubb |
| **Asistencias Múltiples Hogar y Vehículo** | Asistencias + emergencias 24/7 | Imprevistos domésticos y del carro | — |
| **Asistencias médicas familiares** | Orientación y atención médica | Respaldo médico complementario | — |
| **Asistencia médica en viajes** | Protección en viajes nacionales e internacionales | Afiliados que viajan (cross-sell con agencia Colsubsidio) | — |

## 3. Hogar y patrimonio (2)

| Producto | Cubre | Dirigido a | Aseguradora |
|---|---|---|---|
| **Hogar y Contenido** | Terremoto, incendio, robo, erupción, contenidos | Propietarios y arrendatarios | — |
| **Arrendamiento** (garantía de arriendo) | Canon, contrato e inmueble | Propietarios que arriendan | SURA (digital) |

## 4. Vehículos (4)

| Producto | Cubre | Dirigido a | Aseguradora |
|---|---|---|---|
| **⭐ SOAT (carro y moto)** | Gastos médicos, incapacidad permanente, muerte y funerarios, transporte de víctimas | Todo dueño de vehículo (obligatorio; renovación anual) | — |
| **Todo Riesgo Carro** | Daños, robo, RC a terceros, grúa 24/7 | Cobertura más allá del SOAT | — |
| **Todo Riesgo Moto** | Todo riesgo, terceros, grúa, protección legal | Cobertura más allá del SOAT | — |
| **Bici / Scooter / Patineta eléctrica** | Daños, robo, RC | Micromovilidad | — |

## 5. Mascotas (3)

| Producto | Cubre | Dirigido a |
|---|---|---|
| **Mascotas (perro y gato)** | Asistencia veterinaria, RC, daños | Dueños de perros y gatos |
| **Asistencia Veterinaria 24/7** | Orientación, consultas, emergencias | Respaldo de bajo costo |
| **Medicina Prepagada Mascotas** | Plan de medicina prepagada veterinaria | Verificar diferencia exacta vs. los otros dos |

## 6. Deudores / crédito (4)

| Producto | Cubre | Dirigido a |
|---|---|---|
| **Vida Deudor** | Cancela la deuda por muerte o incapacidad permanente | Quien toma un crédito |
| **Desempleo (atado a crédito)** | Paga cuotas del crédito ante desempleo — **no reemplaza ingreso** | Trabajadores con crédito |
| **Incendio (hipotecario)** | Incendio, daños, eventos naturales | Deudores hipotecarios (URL por verificar) |
| **Vida + desempleo (incluido en crédito de consumo)** | Fallecimiento, IPT (incapacidad permanente total), incapacidad temporal, desempleo | Viene activado con el crédito (MetLife) |

## 7. Empresas — fuera del reto de venta individual (1)

| Producto | Cubre | Dirigido a |
|---|---|---|
| **Colectivo de Vida para empleados** | Vida grupal de nómina | Empresas afiliadas |

Gap conocido: Colsubsidio también ofrece colectivo exequial y otros colectivos para
empresas; no se detallan aquí porque el reto es venta individual.

**Fuera de alcance conocido:** Colsubsidio vende medicina prepagada para personas
(vertical Salud, no /seguros, planes desde ~$48.200/mes). Decidir en equipo si el
motor la menciona como alternativa o queda fuera.

---

## Mapa de reglas segmento → producto (v1 — heurística, base para un modelo)

Cruce del catálogo con los segmentos de `investigacion/2026-07-22_analisis-base-afiliados.md`
(v2). Son **reglas explicables**, no un modelo estadístico de propensión: cada fila se
justifica con una variable observable. Es un punto de partida para discutir en equipo.

| Segmento (tamaño real) | Producto candidato | Alternativas | Variable que lo justifica |
|---|---|---|---|
| Sin grupo registrado, 20–35, cat. A (mayoría de la base) | **SOAT** (si tiene vehículo) / Accidentes Personales | AP Digital | Obligatorio + bajo costo; protege su ingreso |
| Monoparental (23,5%) | Vida con beneficiarios | Exequial; Accidentes+Exequial | Dependientes registrados a cargo de un solo adulto |
| Nuclear (9,4%) | Vida familiar | Hogar y Contenido | Hijos + patrimonio |
| Pareja conyugal (5,5% — mitad >55) | Vida y Ahorro (menores de 55) / Exequial y asistencias médicas (mayores) | Hogar | La edad modula el producto dentro del segmento |
| >55 (corte transversal, 11,3%) | Exequial | Asistencias médicas | Etapa de vida |

Notas del mapa:
- El desempleo del catálogo **solo paga cuotas de crédito** — no ofrecerlo como
  protección de ingreso general.
- El oncológico es una opción a evaluar por perfil de riesgo/interés, no una regla "por
  ser mujer" (segmentar por estereotipo es tumbable y con razón).
- Las características finas de cada oferta (coberturas, montos, deducibles por
  arquetipo) están por definir — es la capa de hiperpersonalización que pide el brief y
  se diseña en equipo.

## Fuentes

- colsubsidio.com/seguros y subpáginas: /personal, /familiares, /hogar, /vehiculos,
  /mascotas, /deudores-financieros, /empresas/bienestar/seguros.
- Clausulado PDF de Accidentes Personales (emite MetLife Colombia Seguros de Vida).
- Página de aliado Chubb (chubb.com/co-es/personas-y-familias/colsubsidio.html) — 4
  productos verificados.
- ayuda.colsubsidio.com (seguros del crédito de consumo y de la Tarjeta).
- "Recursos Reto Crédito.docx" oficial (crédito rotativo para seguros e impuestos).
- Presentación en vivo del reto, 22-jul (dato de volumen del SOAT).

---
*Construido con Claude Opus 4.8 (esfuerzo alto) el 22-jul-2026; corregido a v2 con
Claude Fable 5 (esfuerzo alto) tras revisión multiagéntica de 7 agentes el mismo día.*
