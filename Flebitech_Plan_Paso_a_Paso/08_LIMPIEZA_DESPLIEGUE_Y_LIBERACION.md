# Etapa 8 — Limpiar, desplegar y liberar de forma gradual

## Objetivo

Reducir peso y confusión del repositorio, luego publicar las correcciones sin comprometer la versión estable.

## Parte A. Inventario antes de limpiar

No borres `BOCETO PARA FLEBITECH` directamente. Primero:

```bash
git ls-files "BOCETO PARA FLEBITECH/**" > inventario_boceto.txt
git grep -n "BOCETO PARA FLEBITECH" -- ':!BOCETO PARA FLEBITECH/**'
```

Revisa si `vercel.json`, imports, scripts o README usan alguna ruta del directorio.

Clasifica cada archivo como:

- requerido por Flebitech;
- documentación histórica;
- material de otro proyecto;
- multimedia reemplazable;
- dudoso, requiere confirmación del propietario.

## Parte B. Separar material sin perderlo

1. Crea un repositorio aparte para el material legítimo no clínico.
2. Copia y verifica los archivos allí.
3. Conserva el enlace/commit de respaldo.
4. Abre una rama exclusiva:

```bash
git switch master
git pull --ff-only
git switch -c chore/remove-unrelated-assets
```

5. Retira solo archivos confirmados, revisa el diff y crea un commit.
6. No uses `git filter-repo`, `git reset --hard` ni reescritura de historia en esta fase.

## Parte C. Verificar el paquete de despliegue

```bash
du -sh .
find . -type f -size +5M -print
git status
```

Comprueba que Vercel no incluya pruebas, multimedia o material ajeno en la función serverless. Conserva `api/`, `backend/`, `knowledge_base/`, `public/`, `requirements.txt` y `vercel.json` según la arquitectura actual.

## Parte D. Alinear documentación

Corrige README para que incluya:

- Python soportado;
- instalación real;
- diferencia entre web estática y Streamlit;
- BM25, no TF-IDF si ya fue reemplazado;
- variables efectivamente usadas;
- comandos de pruebas;
- limitaciones de uso clínico;
- proceso de actualización de fuentes.

## Parte E. Versiones pequeñas

Publica en este orden:

| Versión sugerida | Contenido único |
|---|---|
| `v1.3.1` | Vía central + prueba clínica |
| `v1.3.2` | Aislamiento de métricas + CORS |
| `v1.3.3` | Historial seguro + sanitización XSS |
| `v1.3.4` | CI y pruebas reproducibles |
| `v1.4.0` | Fuentes gobernadas + evaluación conversacional ampliada |

No combines todas las etapas en `v1.4.0` sin haber probado antes las versiones de parche.

## Parte F. Preview antes de producción

Para cada versión:

1. desplegar preview;
2. ejecutar preguntas del conjunto dorado;
3. probar Groq activo y desactivado;
4. probar navegador móvil y escritorio;
5. verificar CORS, métricas, XSS y fuentes;
6. revisar logs sin datos sensibles;
7. aprobar o revertir.

## Parte G. Piloto educativo

Condiciones:

- usuarios seleccionados;
- sin datos identificables de pacientes;
- supervisión profesional;
- canal para reportar respuestas dudosas;
- revisión semanal de brechas;
- posibilidad de desactivar Groq y usar fallback local.

## Detener y revertir si ocurre

- dato clínico incorrecto;
- mezcla de dos medicamentos;
- sesión que ve información de otra;
- HTML o JavaScript ejecutado;
- pérdida de tablas o escalas;
- el chat deja de responder sin Groq;
- aumento de respuestas fuera de dominio con `had_answer=true`.

Reversión de una versión:

```bash
git revert <SHA_DEL_COMMIT_PROBLEMATICO>
git push origin master
```

Usa `git revert`, no borres historia compartida.

## Definición de terminado

- [ ] Todas las etapas críticas están fusionadas por separado.
- [ ] CI está verde.
- [ ] Validación clínica está documentada.
- [ ] Preview y piloto no presentan fallos críticos.
- [ ] Existe reversión probada.
- [ ] El repositorio contiene solo material pertinente.
- [ ] Flebitech sigue funcionando con y sin Groq.

