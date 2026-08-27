# Benchmarks de venta digital de seguros — Colombia y Latam

> Construido con Claude Sonnet 4.6 (investigación web dirigida). Fecha: 2026-07-23.

---

## Las 3 cifras para el pitch

### 1. Solo el 0,24 % de las pólizas en Colombia se vende por canal electrónico
**Fuente:** El Tiempo / datos de distribución del sector asegurador colombiano citados en artículo de 2017, con canal electrónico en 0.24 % frente a bancaseguros (49 %), intermediarios (20 %) y compañías directas (18 %). [Artículo El Tiempo](https://www.eltiempo.com/economia/sectores/colombianos-y-su-baja-confianza-en-los-seguros-214196)

**Por qué sirve frente al jurado:** Es el argumento de oportunidad más concreto disponible. El mercado físico domina abrumadoramente. Un sistema de venta conversacional-automático directamente en el canal donde ya están los 1,6 M afiliados de Colsubsidio salta esa brecha sin agregar fricción. El jurado de Colsubsidio sabe que sus afiliados categoría A no entran a una app de bancaseguros.

**Precaución:** El dato es de 2017. No existe cifra pública más reciente desagregada por canal electrónico. El mercado ha crecido, pero no hay evidencia de que el canal digital haya superado el 5 % en seguros voluntarios. Citar como "punto de partida del mercado" y no como cifra 2024 exacta.

---

### 2. Más de la mitad de los colombianos (>50 %) no tiene ningún seguro voluntario; en microseguros la penetración es de apenas 9,1 % de las pólizas totales del sector
**Fuentes:**
- "Más del 50 % de colombianos carece de cualquier tipo de seguro" — [El Tiempo](https://www.eltiempo.com/economia/sectores/colombianos-y-su-baja-confianza-en-los-seguros-214196)
- Microseguros: 2 % de las primas emitidas y 9,1 % de las pólizas totales del sector — [La República / Fasecolda 2024](https://www.larepublica.co/finanzas/penetracion-del-sector-asegurador-2024-4148826)
- 90,7 % de las viviendas en Colombia no tiene seguro de hogar — [Semana / Fasecolda mar 2026](https://www.semana.com/economia/macroeconomia/articulo/el-907-de-las-viviendas-en-colombia-no-tiene-seguro-de-hogar-que-pasaria-ante-un-desastre-como-el-de-venezuela/202638/)
- Estrato 2: solo el 22 % considera que su familia está suficientemente asegurada, vs. 50 % en estrato 6 — [búsqueda Fasecolda microseguros]

**Por qué sirve frente al jurado:** La audiencia objetivo del hackathon son afiliados categoría A de Colsubsidio (bajos ingresos). La brecha de aseguramiento en ese segmento es estructural y conocida por el sector. Citar la brecha estrato 2 vs. estrato 6 (22 % vs. 50 %) conecta directo con el perfil del afiliado Colsubsidio y da urgencia al reto.

---

### 3. El sector de seguros masivos en Colombia ya representa el 33,1 % de las primas y el 52,1 % de las pólizas activas; los seguros para estratos bajos crecieron 26,6 % en un año
**Fuentes:**
- Seguros masivos: 33,1 % primas / 52,1 % pólizas activas — [La República / Fasecolda cierre 2024](https://www.larepublica.co/finanzas/penetracion-del-sector-asegurador-2024-4148826)
- Seguros para estratos 1, 2 y 3: crecimiento del 26,6 % interanual, primas de $765 mil millones, suma asegurada de $81 billones — [La República](https://www.larepublica.co/finanzas/el-negocio-de-seguros-para-estratos-bajos-logro-un-crecimiento-de-26-6-en-un-ano-2789789)

**Por qué sirve frente al jurado:** Prueba que el segmento masivo y de bajos ingresos no es solo RSE: ya es el corazón volumétrico del sector (más de la mitad de las pólizas). El crecimiento 26,6 % YoY en estratos bajos es el argumento de mercado más potente para justificar la inversión. Colsubsidio como distribuidor ya está en ese juego (convenios MetLife y Chubb).

---

## Tabla de jugadores digitales

| Jugador | Qué vende digital | Canal | Cifra pública |
|---|---|---|---|
| **R5 (Grupo R5)** | SOAT 100 % online; también créditos con seguro incorporado | Web, app | +2 millones de pólizas SOAT vendidas desde 2018; socio de AXA Colpatria. US$7 M de financiación. [Wikipedia Grupo R5](https://es.wikipedia.org/wiki/Grupo_R5) [no verificado parcialmente] |
| **Seguros Falabella** | SOAT 100 % digital en 2 pasos; seguros de motos, hogar | Web | Operación consolidada; sin cifra de volumen pública confirmada. [Web Falabella](https://soat.segurosfalabella.com.co/sale/step0) |
| **123Seguro** | Comparador y broker 100 % digital de autos y motos | Web | USD 190 M en suma asegurada último año reportado; crecimiento 200 % interanual en Colombia [ACIS](https://acis.org.co/portal/content/noticiasdeinteres/123seguro-se-consolida-en-colombia-con-un-crecimiento-de-200-interanual-y-se-expande-brasil). Operaciones en AR, BR, CL, CO. |
| **Rappi + Chubb** | Seguros de viaje 100 % digitales vía Rappi Travel | App Rappi | Lanzamiento 2022, sin cifras de volumen públicas. [La República 2022](https://www.larepublica.co/empresas/chubb-y-rappi-introducen-para-2022-un-nuevo-seguro-de-viaje-que-sera-100-digital-3277958) |
| **Mercado Pago + Chubb** | Microseguros embebidos en compras; seguros de vida sencillos | App Mercado Pago / Mercado Libre | Parte de Chubb Studio para embedded insurance en Latam. Sin cifras Colombia específicas públicas. [Chubb Latam](https://www.chubb.com/latammarketing/bloglatam/comercializacion-de-seguros-multiples-canales.html) |
| **SURA digital** | Seguros de vida, autos, hogar contratables 100 % online | Web / app | Plataforma activa; sin cifras de pólizas digitales publicadas. [SURA digital](https://www.sura.co/seguros/digitales) |
| **WeSura (Sura + comunidad)** | Seguros comunitarios con fondo compartido; modelo peer-to-peer | App | Producto de innovación; sin cifras públicas de escala. [Valoraanalitik](https://www.valoraanalitik.com/este-es-el-top-20-de-las-insurtechs-de-colombia/) |
| **Scotiabank Colpatria + AXA** | SOAT 100 % digital | App banco | 9.000 pólizas SOAT digitales emitidas en un año; proyección 20.000 en 2024. [DaviBank](https://www.davibank.com/sala-de-prensa/productos-servicios/soat) |
| **Seküre** | Seguros para personas y empresas; también herramienta para aseguradoras | Web / app | US$500.000 de financiación. Sin cifras de pólizas. [Valoraanalitik](https://www.valoraanalitik.com/este-es-el-top-20-de-las-insurtechs-de-colombia/) |
| **Agentemotor** | Broker digital de seguros de autos | Web | Reconocido en top insurtechs Colombia por Digital Insurance jun 2024. Sin cifras. [Agentemotor](https://www.agentemotor.com/blog/agentemotor/el-futuro-de-los-seguros-en-colombia-agentemotor-en-el-top-de-insurtechs-de-digital-insurance/) |
| **Seguros Alfa digital** | Seguros de accidentes 100 % digital | Web | Sin cifras públicas. [Seguros Alfa](https://segurosdigitales.segurosalfa.com.co/) |
| **Bancolombia seguros** | Seguros de vida, hogar, vehículos via app | App Bancolombia | Canal bancaseguros dominante (49 % del total del sector); sin cifra desagregada digital. |
| **Chatbots / plataformas de venta conversacional** | Cotización automática, venta sin agente (SOAT, vida, autos) | WhatsApp / chat | Múltiples proveedores activos: Aurora Inbox, Responde Seguro, Glofera, Tecca — ninguno publica tasas de conversión ni volúmenes. Benchmark genérico: si cotización tarda >5 min, el cliente migra a otra correduría. |

**Convención:** Colsubsidio tiene convenios activos con:
- **MetLife**: cobertura de accidentes, vida, ITP para afiliados con cuota monetaria, cupo de crédito, recreación y renta garantizada. [MetLife Colsubsidio](https://www.metlife.com.co/seguros-masivos/colsubsidio/)
- **Chubb**: accidentes personales, oncológico, protección urbana, AP Digital. [Chubb Colsubsidio](https://www.chubb.com/co-es/personas-y-familias/colsubsidio.html)

Estos convenios hoy operan con contacto humano o formulario; no hay evidencia pública de proceso totalmente automatizado.

---

## Contexto de mercado Colombia

### Penetración general
- **Primas / PIB (2024):** 3,29 % — ligeramente por debajo del promedio Latam (3,22 %) y muy lejos de OCDE (9,3 %). [Fasecolda Q3 2024](https://www.fasecolda.com/cada-vez-mas-colombianos-asegurados-crecimiento-del-sector-en-el-tercer-trimestre-de-2024/)
- **Prima per cápita (2024):** $1.065.064 COP al año (~USD 265). [La República](https://www.larepublica.co/finanzas/penetracion-del-sector-asegurador-2024-4148826)
- **Primas totales emitidas (ene-sep 2024):** $40,1 billones COP (+10,2 %).
- **Siniestros pagados (2024):** $25,5 billones COP (+13,6 % vs. 2023).
- **Proyección crecimiento 2026:** CAGR del 6,5 % para Colombia. [Fasecolda / análisis regional 2024](https://www.fasecolda.com/noticias-2024/analisis-regional-del-mercado-asegurador-colombia-proyecta-un-crecimiento-del-65-para-2026/)

### Brecha de aseguramiento
- **+50 % de colombianos sin ningún seguro voluntario.** El Tiempo.
- **90,7 % de las viviendas sin seguro de hogar** (1.667.044 aseguradas vs. ~17,9 M de viviendas) — Fasecolda mar 2026.
- **Barreras principales:** bajos ingresos (36 %), autoexclusión (34 %), falta de educación financiera (13 %).
- **Brecha por género:** Mujeres, 6,7 puntos porcentuales por debajo de los hombres en acceso a seguros (2024).
- **Brecha por estrato:** Solo el 22 % del estrato 2 cree tener suficiente cobertura frente al 50 % del estrato 6.
- **72 % de las microempresas sin ningún seguro.** El Tiempo.

### Canal masivo y microseguros
- **Seguros masivos** (productos simples, estandarizados, vendidos en masa): 33,1 % de primas / 52,1 % de pólizas activas — son el canal de mayor volumen de pólizas en el país.
- **Microseguros:** 2 % de primas / 9,1 % de pólizas. Prima promedio 2024: $29.340 COP/mes. Canal digital de microseguros creció 27 % en ventas. [Forbes 2026](https://forbes.co/2026/05/20/economia-y-finanzas/microseguros-el-lujo-que-cambia-vidas/)
- **Adopción con créditos bancarios:** 65–75 % de solicitantes de crédito contratan seguros voluntarios asociados.
- **Canales para seguros masivos e inclusivos:** bancaseguros, cajas de compensación, cooperativas, empresas de servicios públicos, grandes superficies, microfinancieras y plataformas digitales. Las cajas de compensación son canal reconocido por el sector.

### Ecosistema insurtech Colombia
- **67 startups activas** en insurtech Colombia a mediados de 2024 (+18 % en 2024). Colombia = 12 % del total latinoamericano. [búsqueda MAPFRE / SegurosNews]
- 53 % de las insurtechs se enfocan en distribución digital; 47 % son habilitadores tecnológicos para aseguradoras.
- Colombia atrae 48 % de insurtechs extranjeras (tercer lugar Latam tras Perú y Ecuador).
- Latam Insurtech: $92 M de inversión en 2024 (–38 % vs. 2023 por contexto macro); rebote +156 % en H2 2024. [SegurosNews](https://segurosnews.com/news/el-sector-insurtech-latinoamericano-cierra-2024-con-92-millones-de-dolares-de-inversion-y-mas-de-500-de-startups)

### Digitalización financiera general (contexto)
- Operaciones financieras no presenciales en Colombia: **84,6 % del total** de transacciones (SFC Q1 2025). [Pulzo / SFC](https://www.pulzo.com/economia/digitalizacion-en-el-sistema-financiero-colombiano-canales-mas-usados-y-tendencias-2024-PP5218963A)
- App móvil: 66 % de operaciones monetarias. Esto muestra que el colombiano ya hace su banca en el celular — pero los seguros no han seguido ese ritmo.

---

## Vacíos: qué cifra NO existe públicamente

Los siguientes datos serían ideales para el pitch pero **no están disponibles públicamente** (no inventar):

1. **Tasa de conversión de seguros vendidos por chat / WhatsApp en Colombia.** No existe ningún jugador local que haya publicado esta cifra. Los proveedores de chatbots (Aurora Inbox, Glofera, Tecca) no publican tasas de cierre.
2. **Porcentaje actualizado (2023-2025) de pólizas vendidas por canal digital.** El único dato disponible es 0,24 % de un artículo de 2017. Fasecolda no publica esta desagregación en sus comunicados públicos.
3. **Volumen de seguros vendidos a afiliados de Colsubsidio** (número de pólizas activas MetLife + Chubb en el convenio). MetLife y Chubb no publican cifras del convenio; Colsubsidio tampoco en su informe 2024.
4. **Tasa de penetración de seguros en categoría A específicamente.** Fasecolda publica por estrato económico pero no por categoría de caja de compensación.
5. **Número de afiliados Colsubsidio categoría A con seguro activo hoy.** No hay cifra pública desagregada.
6. **Tiempo promedio de contratación de seguros masivos en Colombia.** Ninguna aseguradora publica este benchmark.
7. **NPS o satisfacción del proceso de venta de seguros en cajas de compensación.** No hay dato público.
8. **Cifras de Bancolombia Seguros, Movii o billeteras digitales colombianas vendiendo seguros.** Operan pero no publican volúmenes de pólizas.

---

## Fuentes

| Afirmación | URL | Estado |
|---|---|---|
| Canal electrónico = 0,24 % de pólizas; bancaseguros = 49 % | https://www.eltiempo.com/economia/sectores/colombianos-y-su-baja-confianza-en-los-seguros-214196 | Verificado (dato 2017) |
| +50 % colombianos sin seguro voluntario | https://www.eltiempo.com/economia/sectores/colombianos-y-su-baja-confianza-en-los-seguros-214196 | Verificado |
| 90,7 % de viviendas sin seguro de hogar | https://www.semana.com/economia/macroeconomia/articulo/el-907-de-las-viviendas-en-colombia-no-tiene-seguro-de-hogar-que-pasaria-ante-un-desastre-como-el-de-venezuela/202638/ | Verificado (Fasecolda mar 2026) |
| Seguros masivos = 33,1 % primas / 52,1 % pólizas | https://www.larepublica.co/finanzas/penetracion-del-sector-asegurador-2024-4148826 | Verificado |
| Microseguros = 2 % primas / 9,1 % pólizas | https://www.larepublica.co/finanzas/penetracion-del-sector-asegurador-2024-4148826 | Verificado |
| Seguros para estratos bajos +26,6 % YoY; $765 MM primas | https://www.larepublica.co/finanzas/el-negocio-de-seguros-para-estratos-bajos-logro-un-crecimiento-de-26-6-en-un-ano-2789789 | Verificado |
| Canal digital microseguros +27 % en ventas | https://forbes.co/2026/05/20/economia-y-finanzas/microseguros-el-lujo-que-cambia-vidas/ | Verificado |
| Prima promedio microseguro $29.340 COP | https://forbes.co/2026/05/20/economia-y-finanzas/microseguros-el-lujo-que-cambia-vidas/ | Verificado |
| 65–75 % de solicitantes de crédito contratan seguro voluntario asociado | https://forbes.co/2026/05/20/economia-y-finanzas/microseguros-el-lujo-que-cambia-vidas/ | Verificado |
| Penetración 3,29 % PIB; primas $40,1 T; siniestros $25,5 T (2024) | https://www.fasecolda.com/cada-vez-mas-colombianos-asegurados-crecimiento-del-sector-en-el-tercer-trimestre-de-2024/ | Verificado |
| Prima per cápita $1.065.064 COP (2024) | https://www.larepublica.co/finanzas/penetracion-del-sector-asegurador-2024-4148826 | Verificado |
| Proyección CAGR 6,5 % Colombia 2026 | https://www.fasecolda.com/noticias-2024/analisis-regional-del-mercado-asegurador-colombia-proyecta-un-crecimiento-del-65-para-2026/ | Verificado |
| 22 % estrato 2 cree estar bien asegurado vs. 50 % estrato 6 | Búsqueda web Fasecolda / microseguros | [no verificado directamente — sin URL fuente primaria] |
| R5: +2 M de pólizas SOAT desde 2018 | https://es.wikipedia.org/wiki/Grupo_R5 | [no verificado — Wikipedia; confirmar con fuente primaria] |
| 123Seguro: USD 190 M suma asegurada (autos/motos) | https://acis.org.co/portal/content/noticiasdeinteres/123seguro-se-consolida-en-colombia-con-un-crecimiento-de-200-interanual-y-se-expande-brasil | Verificado (citado en artículo ACIS) |
| 123Seguro: +200 % crecimiento interanual en Colombia | https://acis.org.co/portal/content/noticiasdeinteres/123seguro-se-consolida-en-colombia-con-un-crecimiento-de-200-interanual-y-se-expande-brasil | Verificado |
| Scotiabank / AXA: 9.000 SOAT digitales/año | https://www.davibank.com/sala-de-prensa/productos-servicios/soat | Verificado |
| 67 insurtechs activas Colombia 2024 | Búsqueda Digital Insurance / MAPFRE | [no verificado directamente — sin URL fuente primaria] |
| 84,6 % operaciones financieras no presenciales (SFC Q1 2025) | https://www.pulzo.com/economia/digitalizacion-en-el-sistema-financiero-colombiano-canales-mas-usados-y-tendencias-2024-PP5218963A | Verificado |
| MetLife — convenio Colsubsidio activo | https://www.metlife.com.co/seguros-masivos/colsubsidio/ | Verificado |
| Chubb — convenio Colsubsidio + AP Digital | https://www.chubb.com/co-es/personas-y-familias/colsubsidio.html | Verificado |
| Colsubsidio: 1.615.957 afiliados en 2024 | Informe de Gestión y Sostenibilidad Colsubsidio 2024 (PDF) | Verificado (PDF oficial) |
| Cajas de compensación = canal reconocido para seguros inclusivos | https://www.bancadelasoportunidades.gov.co/es/programas/proyecto-para-la-dinamizacion-de-los-seguros-inclusivos-en-colombia | Verificado |
| Rappi + Chubb seguro viaje 100 % digital | https://www.larepublica.co/empresas/chubb-y-rappi-introducen-para-2022-un-nuevo-seguro-de-viaje-que-sera-100-digital-3277958 | Verificado |
| Seguros Latam insurtech $92 M inversión 2024 | https://segurosnews.com/news/el-sector-insurtech-latinoamericano-cierra-2024-con-92-millones-de-dolares-de-inversion-y-mas-de-500-de-startups | Verificado |
