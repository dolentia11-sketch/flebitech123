-- Extensión al schema del PR #9 (schema.sql) para el puente con negocio.db.
-- Aplicar después de schema.sql. Idempotente (ADD COLUMN falla si existe;
-- puente_negocio.aplicar_extension() lo maneja).
--
-- `sessions.serie` es el link lógico con `usuario_demo.serie` de negocio.db
-- (paquete producto/engines/db). Los join se hacen en app-code — SQLite no
-- soporta FK cross-database sin ATTACH.

ALTER TABLE sessions ADD COLUMN serie TEXT;
CREATE INDEX IF NOT EXISTS idx_sessions_serie ON sessions(serie);
