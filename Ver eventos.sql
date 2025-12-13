use sistema_residencial;
-- Verificar eventos próximos con inscripciones
SELECT 
    r.ID_RESERVA,
    r.NOMBRE as evento_nombre,
    r.FECHA_HORA,
    r.ESTADO,
    u.ID_USUARIO,
    u.NOMBRE as usuario_nombre,
    u.CORREO as usuario_correo
FROM reserva r
JOIN inscripcion_evento ie ON r.ID_RESERVA = ie.ID_RESERVA
JOIN usuario u ON ie.ID_USUARIO = u.ID_USUARIO
WHERE r.FECHA_HORA BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR)
AND r.ESTADO = 'EN PROCESO'
AND u.CORREO IS NOT NULL;

-- Ver TODOS los eventos con sus inscripciones
SELECT 
    r.ID_RESERVA,
    r.NOMBRE as evento_nombre,
    r.FECHA_HORA,
    r.ESTADO,
    COUNT(ie.ID_USUARIO) as total_inscritos,
    GROUP_CONCAT(u.NOMBRE) as nombres_inscritos
FROM reserva r
LEFT JOIN inscripcion_evento ie ON r.ID_RESERVA = ie.ID_RESERVA
LEFT JOIN usuario u ON ie.ID_USUARIO = u.ID_USUARIO
GROUP BY r.ID_RESERVA;

-- Ver eventos próximos (en las próximas 24 horas)
SELECT 
    r.ID_RESERVA,
    r.NOMBRE,
    r.FECHA_HORA,
    r.ESTADO,
    TIMESTAMPDIFF(HOUR, NOW(), r.FECHA_HORA) as horas_restantes
FROM reserva r
WHERE r.FECHA_HORA > NOW()
ORDER BY r.FECHA_HORA;

-- Ver TODAS las inscripciones existentes
SELECT 
    ie.ID_RESERVA,
    r.NOMBRE as evento_nombre,
    ie.ID_USUARIO,
    u.NOMBRE as usuario_nombre,
    u.CORREO,
    ie.FECHA_INSCRIPCION
FROM inscripcion_evento ie
JOIN reserva r ON ie.ID_RESERVA = r.ID_RESERVA
JOIN usuario u ON ie.ID_USUARIO = u.ID_USUARIO
ORDER BY ie.FECHA_INSCRIPCION DESC;
ALTER TABLE recordatorio_evento 
ADD COLUMN ESTADO ENUM('PENDIENTE', 'ENVIADO', 'ERROR') NOT NULL DEFAULT 'PENDIENTE';