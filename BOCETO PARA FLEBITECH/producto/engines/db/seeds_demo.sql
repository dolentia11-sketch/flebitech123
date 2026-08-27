-- Reto 02 · Seeds demo para el pitch
-- Hackathon Colsubsidio 2026 · Scala Labs
--
-- 5 historias sintéticas que cubren el arco completo del producto:
--   1. Laura   — afiliada, sabe qué quiere, compra vida            → póliza emitida
--   2. Diego   — afiliado, no sabe qué quiere, cotiza y abandona    → fuga en precio
--   3. Marta   — afiliada, sabe: cáncer (producto asistida)         → derivación a asesor
--   4. Camilo  — afiliado, compra exequial + paquete sugerido      → póliza + upsell
--   5. Yeni    — NO afiliada, compra hogar                          → póliza + lead_afiliacion
--
-- Todos los datos son ficticios pero contextualmente coherentes.
-- Los hashes de póliza son sha256 reales de: numero|serie|producto|prima|consentimiento_ts

BEGIN TRANSACTION;

-- ─── usuario_demo ──────────────────────────────────────────────────────────
INSERT INTO usuario_demo (serie, es_afiliado, segmento, categoria, rango_salarial, rango_edad, genero, situacion_laboral, composicion_familiar) VALUES
    ('SER-000001', 1, 'S2', 'B', '3-5 SMLV',   '30-39', 'F', 'empleado',      'pareja+2_hijos'),
    ('SER-000002', 1, 'S1', 'C', '1-2 SMLV',   '20-29', 'M', 'empleado',      'soltero'),
    ('SER-000003', 1, 'S2', 'B', '1-2 SMLV',   '40-49', 'F', 'independiente', 'monoparental_1_hijo'),
    ('SER-000004', 1, 'S3', 'A', '>5 SMLV',    '50-59', 'M', 'empleado',      'pareja+3_hijos'),
    ('LEAD-0001',  0, NULL, NULL,'1-2 SMLV',   '20-29', 'F', 'independiente', 'soltera');

-- ─── score_resultado ───────────────────────────────────────────────────────
-- Cada perfil corre por el scoring_engine con las V1..V7 aplicables.
INSERT INTO score_resultado (id, serie, variables_json, ranking_json, timestamp) VALUES
    (1, 'SER-000001',
     '{"V1":"30-39","V2":"F","V3":"empleado","V5":"pareja+2_hijos","V6":"3-5 SMLV","V7":"vivienda_propia"}',
     '[{"producto_id":"vida","puntaje":0.87},{"producto_id":"exequial","puntaje":0.62},{"producto_id":"accidentes","puntaje":0.48}]',
     '2026-07-24 10:12:04'),
    (2, 'SER-000002',
     '{"V1":"20-29","V2":"M","V3":"empleado","V5":"soltero","V6":"1-2 SMLV"}',
     '[{"producto_id":"accidentes","puntaje":0.71},{"producto_id":"bicicletas","puntaje":0.58},{"producto_id":"renta","puntaje":0.44}]',
     '2026-07-24 11:33:19'),
    (3, 'SER-000003',
     '{"V1":"40-49","V2":"F","V3":"independiente","V5":"monoparental_1_hijo","V6":"1-2 SMLV","V11":"antecedente_familiar_cancer"}',
     '[{"producto_id":"cancer","puntaje":0.79},{"producto_id":"salud","puntaje":0.65},{"producto_id":"vida","puntaje":0.51}]',
     '2026-07-24 13:22:47'),
    (4, 'SER-000004',
     '{"V1":"50-59","V2":"M","V3":"empleado","V5":"pareja+3_hijos","V6":">5 SMLV","V7":"vivienda_propia"}',
     '[{"producto_id":"exequial","puntaje":0.91},{"producto_id":"vida","puntaje":0.83},{"producto_id":"salud","puntaje":0.72}]',
     '2026-07-24 15:04:12'),
    (5, 'LEAD-0001',
     '{"V1":"20-29","V2":"F","V3":"independiente","V5":"soltera","V6":"1-2 SMLV","V7":"arriendo_reciente"}',
     '[{"producto_id":"hogar","puntaje":0.76},{"producto_id":"arrendamiento","puntaje":0.54},{"producto_id":"accidentes","puntaje":0.39}]',
     '2026-07-24 18:37:22');

-- ─── cotizacion ────────────────────────────────────────────────────────────
-- Marta también genera cotización (con veredicto=asistida) aunque no habrá póliza automática.
INSERT INTO cotizacion (id, serie, producto_id, prima, veredicto_idoneidad, variables_json, score_id, creado_en) VALUES
    (1, 'SER-000001', 'vida',     28400, 'apto',
     '{"cobertura":80000000,"factor_edad":1.0,"factor_dependientes":1.8}', 1, '2026-07-24 10:13:11'),
    (2, 'SER-000002', 'accidentes',12500, 'alternativa_asequible',
     '{"cobertura":30000000,"factor_edad":0.85,"factor_ingreso":0.7}', 2, '2026-07-24 11:35:02'),
    (3, 'SER-000003', 'cancer',    41200, 'asistida',
     '{"cobertura":120000000,"factor_edad":1.35,"nota":"requiere firma con asesor"}', 3, '2026-07-24 13:24:30'),
    (4, 'SER-000004', 'exequial',  14500, 'apto',
     '{"cobertura":15000000,"factor_edad":1.35,"grupo_familiar":5}', 4, '2026-07-24 15:05:47'),
    (5, 'LEAD-0001',  'hogar',     22000, 'apto',
     '{"cobertura":60000000,"factor_edad":0.85,"tipo_vivienda":"apartamento_arriendo"}', 5, '2026-07-24 18:39:14');

-- ─── poliza ────────────────────────────────────────────────────────────────
-- Solo se emiten 3: Laura, Camilo, Yeni. Diego abandonó; Marta se derivó.
-- hash = sha256("numero|serie|producto_id|prima|consentimiento_ts")
INSERT INTO poliza (numero, serie, producto_id, prima, consentimiento_texto, consentimiento_ts, hash, cotizacion_id, emitida_en) VALUES
    ('COL-2026-00001', 'SER-000001', 'vida', 28400,
     'Acepto la contratación del Seguro de Vida por $28.400/mes con cobertura de $80.000.000 y autorizo el débito automático de mi cuenta Colsubsidio.',
     '2026-07-24 10:14:32',
     '88d6f52c54f8198cc93c29f20591bd10a73ae4dcbc27acb7241aa13ecf66d160',
     1, '2026-07-24 10:14:33'),
    ('COL-2026-00002', 'SER-000004', 'exequial', 14500,
     'Acepto contratar el Exequial Familiar por $14.500/mes para mi grupo familiar de 5 personas y autorizo el débito automático.',
     '2026-07-24 15:07:18',
     'de761336da6174df849e9fce5458fd9b19dab36aa6c7a86522bef35356bc4e0c',
     4, '2026-07-24 15:07:19'),
    ('COL-2026-00003', 'LEAD-0001', 'hogar', 22000,
     'Acepto contratar el Seguro de Hogar por $22.000/mes para mi apartamento en arriendo y autorizo el pago mensual via PSE.',
     '2026-07-24 18:41:05',
     '9c9b14e4122e5d379d216c67b2ca9471d0135e08bd3c84bd51bc2af943392733',
     5, '2026-07-24 18:41:06');

-- ─── evento_trazabilidad ───────────────────────────────────────────────────
-- Cada historia queda como una tira de eventos legibles en la demo.

-- Historia 1: Laura (afiliada, sabe qué quiere, compra) ---------------------
INSERT INTO evento_trazabilidad (serie, paso, dato_json, timestamp) VALUES
    ('SER-000001', 'paso0',         '{"afiliada":true,"canal":"whatsapp"}',                                              '2026-07-24 10:10:02'),
    ('SER-000001', 'intencion',     '{"sabe_que_quiere":true,"texto":"quiero un seguro de vida para mis hijos","match":"vida"}', '2026-07-24 10:11:15'),
    ('SER-000001', 'p1',            '{"pregunta":"¿cuántas personas dependen de ti?","respuesta":"2"}',                  '2026-07-24 10:11:47'),
    ('SER-000001', 'precio',        '{"prima_ofrecida":28400,"veredicto":"apto"}',                                       '2026-07-24 10:13:11'),
    ('SER-000001', 'consentimiento','{"aceptado":true,"texto_hash":"88d6f52c..."}',                                      '2026-07-24 10:14:32'),
    ('SER-000001', 'cierre',        '{"poliza":"COL-2026-00001","tiempo_total_seg":270}',                                '2026-07-24 10:14:33');

-- Historia 2: Diego (afiliado, cotiza y abandona) ---------------------------
INSERT INTO evento_trazabilidad (serie, paso, dato_json, timestamp) VALUES
    ('SER-000002', 'paso0',    '{"afiliado":true,"canal":"web"}',                                                        '2026-07-24 11:30:00'),
    ('SER-000002', 'intencion','{"sabe_que_quiere":false,"texto":"no sé, algo básico"}',                                 '2026-07-24 11:30:44'),
    ('SER-000002', 'p1',       '{"pregunta":"edad","respuesta":"27"}',                                                    '2026-07-24 11:31:10'),
    ('SER-000002', 'p2',       '{"pregunta":"¿tienes personas a cargo?","respuesta":"no"}',                              '2026-07-24 11:31:38'),
    ('SER-000002', 'p3',       '{"pregunta":"¿te movilizas en bici?","respuesta":"sí, todos los días"}',                 '2026-07-24 11:32:05'),
    ('SER-000002', 'p4',       '{"pregunta":"¿ingreso mensual?","respuesta":"1.400.000"}',                               '2026-07-24 11:32:41'),
    ('SER-000002', 'p5',       '{"pregunta":"¿te preocupa más un accidente o proteger algo material?","respuesta":"accidente"}', '2026-07-24 11:33:12'),
    ('SER-000002', 'precio',   '{"prima_ofrecida":12500,"veredicto":"alternativa_asequible","alternativa_ofrecida":8900}','2026-07-24 11:35:02'),
    ('SER-000002', 'abandono', '{"motivo":"precio","ultimo_mensaje":"me lo pienso, gracias","punto_de_fuga":"precio"}',   '2026-07-24 11:36:47');

-- Historia 3: Marta (producto asistida → derivación a asesor) ---------------
INSERT INTO evento_trazabilidad (serie, paso, dato_json, timestamp) VALUES
    ('SER-000003', 'paso0',     '{"afiliada":true,"canal":"whatsapp"}',                                                   '2026-07-24 13:20:00'),
    ('SER-000003', 'intencion', '{"sabe_que_quiere":true,"texto":"me interesa el seguro de cáncer, mi mamá lo tuvo","match":"cancer"}', '2026-07-24 13:21:33'),
    ('SER-000003', 'precio',    '{"prima_ofrecida":41200,"veredicto":"asistida","razon":"requiere firma con asesor"}',   '2026-07-24 13:24:30'),
    ('SER-000003', 'derivacion','{"asesor_asignado":"caro.gomez@colsubsidio.co","razon":"producto_asistida","canal_derivacion":"agenda_calendly"}', '2026-07-24 13:25:10');

-- Historia 4: Camilo (afiliado, compra exequial, recibe paquete) ------------
INSERT INTO evento_trazabilidad (serie, paso, dato_json, timestamp) VALUES
    ('SER-000004', 'paso0',         '{"afiliado":true,"canal":"app"}',                                                    '2026-07-24 15:02:11'),
    ('SER-000004', 'intencion',     '{"sabe_que_quiere":true,"texto":"necesito el exequial familiar","match":"exequial"}', '2026-07-24 15:03:20'),
    ('SER-000004', 'p1',            '{"pregunta":"¿cuántas personas en el grupo?","respuesta":"5"}',                      '2026-07-24 15:03:52'),
    ('SER-000004', 'precio',        '{"prima_ofrecida":14500,"veredicto":"apto"}',                                        '2026-07-24 15:05:47'),
    ('SER-000004', 'consentimiento','{"aceptado":true,"texto_hash":"de761336..."}',                                       '2026-07-24 15:07:18'),
    ('SER-000004', 'cierre',        '{"poliza":"COL-2026-00002","tiempo_total_seg":307}',                                 '2026-07-24 15:07:19'),
    ('SER-000004', 'paquete',       '{"sugerencia":"vida","razon":"score_alto=0.83","aceptado":false,"respuesta_usuario":"lo pienso"}', '2026-07-24 15:08:44');

-- Historia 5: Yeni (no afiliada, compra hogar, se genera lead) --------------
INSERT INTO evento_trazabilidad (serie, paso, dato_json, timestamp) VALUES
    ('LEAD-0001', 'paso0',           '{"afiliada":false,"canal":"web","origen":"landing_arriendo"}',                       '2026-07-24 18:33:41'),
    ('LEAD-0001', 'intencion',       '{"sabe_que_quiere":true,"texto":"quiero un seguro para mi apartamento en arriendo","match":"hogar"}', '2026-07-24 18:35:02'),
    ('LEAD-0001', 'p1',              '{"pregunta":"¿estrato del apartamento?","respuesta":"3"}',                           '2026-07-24 18:36:11'),
    ('LEAD-0001', 'p2',              '{"pregunta":"¿tienes electrodomésticos por más de 20M?","respuesta":"sí"}',          '2026-07-24 18:37:00'),
    ('LEAD-0001', 'precio',          '{"prima_ofrecida":22000,"veredicto":"apto"}',                                        '2026-07-24 18:39:14'),
    ('LEAD-0001', 'consentimiento',  '{"aceptado":true,"texto_hash":"9c9b14e4..."}',                                       '2026-07-24 18:41:05'),
    ('LEAD-0001', 'cierre',          '{"poliza":"COL-2026-00003","tiempo_total_seg":444}',                                 '2026-07-24 18:41:06'),
    ('LEAD-0001', 'lead_afiliacion', '{"oferta":"afiliarse_categoria_C","canal_seguimiento":"whatsapp","respuesta_usuario":"me interesa, cuéntame más"}', '2026-07-24 18:42:33');

COMMIT;
