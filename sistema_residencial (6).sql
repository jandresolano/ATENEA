-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 12-12-2025 a las 17:30:29
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sistema_residencial`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `actividad`
--

CREATE TABLE `actividad` (
  `ID_ACTIVIDAD` int(11) NOT NULL,
  `DESCRIPCION` text NOT NULL,
  `FECHA` datetime DEFAULT NULL,
  `USUARIO_ID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `anuncio`
--

CREATE TABLE `anuncio` (
  `ID_ANUNCIO` int(11) NOT NULL,
  `TITULO` varchar(100) NOT NULL,
  `MENSAJE` text NOT NULL,
  `FECHA` datetime DEFAULT NULL,
  `PUBLICADO_POR` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `aviso`
--

CREATE TABLE `aviso` (
  `ID_AVISO` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `CLASIFICACION` enum('PRIVADO','PUBLICO') NOT NULL,
  `DESTINATARIO` varchar(100) DEFAULT NULL,
  `FECHA_INICIO` date NOT NULL,
  `FECHA_FIN` date NOT NULL,
  `CANAL` varchar(50) DEFAULT NULL,
  `URL_AVISO` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `correspondencia`
--

CREATE TABLE `correspondencia` (
  `ID_CORRESPONDENCIA` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `CLASIFICACION` enum('RECIBO PERSONAL','RECIBO DOMESTICO','PAQUETE') NOT NULL,
  `EMPAQUE` enum('BOLSA','CAJA','SOBRE') NOT NULL,
  `ESTADO` enum('RECIBIDO','NO RECIBIDO','EN BODEGA') NOT NULL,
  `FECHA_LLEGADA` date DEFAULT NULL,
  `FECHA_ENTREGA` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_instrumental`
--

CREATE TABLE `detalle_instrumental` (
  `ID_PRESTAMO` int(11) NOT NULL,
  `ID_INSTRUMENTAL` int(11) NOT NULL,
  `CANTIDAD` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_prestamo`
--

CREATE TABLE `detalle_prestamo` (
  `ID_PRESTAMO` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_reserva`
--

CREATE TABLE `detalle_reserva` (
  `ID_RESERVA` int(11) NOT NULL,
  `ID_ESPACIO` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_sorteo`
--

CREATE TABLE `detalle_sorteo` (
  `ID_USUARIO` int(11) NOT NULL,
  `ID_SORTEO` int(11) NOT NULL,
  `ID_PARQUEADERO` int(11) NOT NULL,
  `ADMITIDO` enum('SI','NO') NOT NULL,
  `ASIGNADO` enum('SI','NO') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `documento_vehiculo`
--

CREATE TABLE `documento_vehiculo` (
  `ID_DOCUMENTO` int(11) NOT NULL,
  `ID_VEHICULO` int(11) NOT NULL,
  `TIPO_DOCUMENTO` enum('SOAT','IDENTIDAD','TARJETA_PROPIEDAD') NOT NULL,
  `NOMBRE_ARCHIVO` varchar(255) NOT NULL,
  `RUTA_ARCHIVO` varchar(500) NOT NULL,
  `FECHA_SUBIDA` datetime DEFAULT current_timestamp(),
  `ESTADO` enum('PENDIENTE','APROBADO','RECHAZADO') DEFAULT 'PENDIENTE',
  `OBSERVACIONES` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `espacio_comunal`
--

CREATE TABLE `espacio_comunal` (
  `ID_ESPACIO` int(11) NOT NULL,
  `NOMBRE` varchar(50) NOT NULL,
  `DISPONIBILIDAD` enum('SI','NO') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evento`
--

CREATE TABLE `evento` (
  `ID_EVENTO` int(11) NOT NULL,
  `TITULO` varchar(100) NOT NULL,
  `DESCRIPCION` text NOT NULL,
  `FECHA` datetime NOT NULL,
  `CREADO_POR` int(11) NOT NULL,
  `ESTADO` enum('PENDIENTE','APROBADO','RECHAZADO') DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestion_espera`
--

CREATE TABLE `gestion_espera` (
  `ID_ESPERA` int(11) NOT NULL,
  `DETALLE` text NOT NULL,
  `ESTADO` enum('PENDIENTE','ATENDIDO') DEFAULT NULL,
  `FECHA_SOLICITUD` datetime DEFAULT NULL,
  `SOLICITADO_POR` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidente`
--

CREATE TABLE `incidente` (
  `ID_INCIDENTE` int(11) NOT NULL,
  `DETALLE` text NOT NULL,
  `FECHA` datetime DEFAULT NULL,
  `REPORTADO_POR` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inscripcion_evento`
--

CREATE TABLE `inscripcion_evento` (
  `ID_RESERVA` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `FECHA_INSCRIPCION` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `inscripcion_evento`
--

INSERT INTO `inscripcion_evento` (`ID_RESERVA`, `ID_USUARIO`, `FECHA_INSCRIPCION`) VALUES
(8, 5, '2025-10-29 18:06:24'),
(9, 5, '2025-10-29 18:06:22'),
(11, 5, '2025-12-12 11:21:47');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `instrumental`
--

CREATE TABLE `instrumental` (
  `ID_INSTRUMENTAL` int(11) NOT NULL,
  `NOMBRE` varchar(50) NOT NULL,
  `CANTIDAD` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paquete`
--

CREATE TABLE `paquete` (
  `id` int(11) NOT NULL,
  `residente_id` int(11) DEFAULT NULL,
  `torre` varchar(10) NOT NULL,
  `apartamento` varchar(10) NOT NULL,
  `descripcion` text NOT NULL,
  `remitente` varchar(100) DEFAULT NULL,
  `numero_seguimiento` varchar(50) DEFAULT NULL,
  `fecha_ingreso` timestamp NULL DEFAULT current_timestamp(),
  `fecha_notificacion` timestamp NULL DEFAULT NULL,
  `fecha_entrega` timestamp NULL DEFAULT NULL,
  `estado` enum('recibido','notificado','entregado') DEFAULT NULL,
  `notificado_correo` tinyint(1) DEFAULT NULL,
  `notificado_whatsapp` tinyint(1) DEFAULT NULL,
  `observaciones` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `paquete`
--

INSERT INTO `paquete` (`id`, `residente_id`, `torre`, `apartamento`, `descripcion`, `remitente`, `numero_seguimiento`, `fecha_ingreso`, `fecha_notificacion`, `fecha_entrega`, `estado`, `notificado_correo`, `notificado_whatsapp`, `observaciones`) VALUES
(1, 9, '5', '201', 'Caja verde', 'asda', '1002', '2025-10-29 22:13:38', '2025-10-29 22:13:45', NULL, 'notificado', 1, 0, 'sada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parqueadero`
--

CREATE TABLE `parqueadero` (
  `ID_PARQUEADERO` int(11) NOT NULL,
  `CLASIFICACION` enum('CARRO','MOTO','BICICLETA') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prestamo`
--

CREATE TABLE `prestamo` (
  `ID_PRESTAMO` int(11) NOT NULL,
  `FECHA_PRESTAMO` date NOT NULL,
  `FECHA_DEVOLUCION` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prestamo_parqueadero`
--

CREATE TABLE `prestamo_parqueadero` (
  `ID_PRESTAMO` int(11) NOT NULL,
  `VEHICULO` varchar(50) NOT NULL,
  `INICIO` datetime NOT NULL,
  `FIN` datetime NOT NULL,
  `RESIDENTE_ID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recibo`
--

CREATE TABLE `recibo` (
  `ID_RECIBO` int(11) NOT NULL,
  `MONTO` float NOT NULL,
  `FECHA` datetime DEFAULT NULL,
  `PAGADO` tinyint(1) DEFAULT NULL,
  `RESIDENTE_ID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recordatorio_evento`
--

CREATE TABLE `recordatorio_evento` (
  `ID_RECORDATORIO` int(11) NOT NULL,
  `ID_RESERVA` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `FECHA_ENVIO` datetime NOT NULL,
  `ESTADO` enum('PENDIENTE','ENVIADO','ERROR') DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte`
--

CREATE TABLE `reporte` (
  `ID_REPORTE` int(11) NOT NULL,
  `TITULO` varchar(100) NOT NULL,
  `DETALLE` text NOT NULL,
  `FECHA_REPORTE` datetime DEFAULT NULL,
  `CREADO_POR` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reserva`
--

CREATE TABLE `reserva` (
  `ID_RESERVA` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `NOMBRE` varchar(50) DEFAULT NULL,
  `DESCRIPCION` varchar(255) DEFAULT NULL,
  `FECHA_HORA` datetime NOT NULL,
  `COMENTARIO` varchar(255) DEFAULT NULL,
  `ESTADO` enum('ACTIVO','CANCELADO','FINALIZADO','EN PROCESO') NOT NULL,
  `TIPO` enum('PUBLICO','PRIVADO') NOT NULL,
  `CLASE` enum('FRECUENTE','RECURRENTE') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `reserva`
--

INSERT INTO `reserva` (`ID_RESERVA`, `ID_USUARIO`, `NOMBRE`, `DESCRIPCION`, `FECHA_HORA`, `COMENTARIO`, `ESTADO`, `TIPO`, `CLASE`) VALUES
(8, 1, 'Evento 1', 'sdad', '2025-11-01 21:12:00', NULL, 'ACTIVO', 'PUBLICO', 'FRECUENTE'),
(9, 1, 'Evento 2', 'sa das', '2025-11-11 11:11:00', NULL, 'ACTIVO', 'PUBLICO', 'FRECUENTE'),
(10, 2, 'Adriana', 'lpklñk´ñlçkl´mk,lkmlñl-', '2025-11-27 07:01:00', NULL, 'ACTIVO', 'PUBLICO', 'FRECUENTE'),
(11, 1, 'Evento Prueba', 'SAFASF', '2025-12-14 11:11:00', NULL, 'ACTIVO', 'PUBLICO', 'FRECUENTE');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sorteo`
--

CREATE TABLE `sorteo` (
  `ID_SORTEO` int(11) NOT NULL,
  `FECHA` datetime NOT NULL DEFAULT current_timestamp(),
  `TIPO` enum('CARRO','MOTO') NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `RESULTADO` enum('GANADOR','ESPERA') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sorteo`
--

INSERT INTO `sorteo` (`ID_SORTEO`, `FECHA`, `TIPO`, `ID_USUARIO`, `RESULTADO`) VALUES
(157, '2025-12-11 23:47:21', 'CARRO', 66, 'GANADOR'),
(158, '2025-12-11 23:47:21', 'CARRO', 50, 'GANADOR'),
(159, '2025-12-11 23:47:34', 'MOTO', 66, 'GANADOR');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `ID_USUARIO` int(11) NOT NULL,
  `NOMBRE` varchar(50) NOT NULL,
  `APELLIDO` varchar(50) NOT NULL,
  `CORREO` varchar(100) NOT NULL,
  `TELEFONO` varchar(20) DEFAULT NULL,
  `TORRE` varchar(10) DEFAULT NULL,
  `APARTAMENTO` varchar(10) DEFAULT NULL,
  `ROL` enum('ADMINISTRADOR','RESIDENTE','PORTERO') NOT NULL,
  `ESTADO` enum('ACTIVO','INACTIVO','PENDIENTE') NOT NULL,
  `CONTRASENA` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`ID_USUARIO`, `NOMBRE`, `APELLIDO`, `CORREO`, `TELEFONO`, `TORRE`, `APARTAMENTO`, `ROL`, `ESTADO`, `CONTRASENA`) VALUES
(1, 'Santiago', 'Padilla', 'santiagopa0717@gmail.com', '123456789', 'N/A', 'N/A', 'ADMINISTRADOR', 'ACTIVO', 'pbkdf2:sha256:600000$XrnDkstGlm5AmsW3$38a3e8f67279baa9d42e36dae45ef250ec1779cef17eec7c0e636bdefb03d395'),
(2, 'Jhon', 'Solano', 'jsolanofigueredo@gmail.com', '12345', NULL, NULL, 'ADMINISTRADOR', 'ACTIVO', 'scrypt:32768:8:1$DIGMRSiq3JeqeX2l$24e3b5bc2c00441061da19e671db8d7a6a5036b6835542b547e5aea239a2e0535affc03afec361db086b7521486ca8c7f43f7bb15a284e9fe2de20305730058a'),
(3, 'jhoin', 'santiago', 'santiago@gmail.com', '123456', '4', '5', 'PORTERO', 'ACTIVO', 'pbkdf2:sha256:600000$O8fxao8TpmrMnv3N$b1365a71c3b8773246b232192496f72df506ca4ec2c989321a064c1c86fbc350'),
(4, 'jhon', 'solano', 'residente@gmail.com', '12548', NULL, NULL, 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$4bSVTGE6oitGF8J1$35e3d22dfe8650f6119aedd15f5dca0a3c14ded820a0771ba3b49892e9fdf2fa'),
(5, 'Santiago', 'Padilla', 'padillinmc@gmail.com', '12345678', 'None', 'None', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$ctTmjf78h7hFfgug$2ed0f7a651b3f07d305bb67d1d8e699ac2c44b7ca7b1bd8225de80a61ed4bd92'),
(7, 'jhon', 'solano', 'asdasd@gmail.com', '3202476120', '5', '5567', 'RESIDENTE', 'INACTIVO', 'pbkdf2:sha256:600000$Rwvu46sLIZafr7Ef$c6e1f7b63a993c0e8341242eb21762c7cd24dfe3ab9654e11b2059ac9ea2ff19'),
(9, 'Valey', 'Martinez', 'jhosianyxd@gmail.com', '3114980306', '5', '201', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$NWy3aXacCe52OzDJ$f9d64d6dee996410452dd19f08b945fceeb4e6ba814f54b06ac2a3ef9e263b42'),
(50, 'Carlos', 'Gómez', 'carlos.gomez@email.com', '3001111111', '1', '101', 'RESIDENTE', 'ACTIVO', 'scrypt:32768:8:1$EPUw8knoEzoS3vbj$10a558e0ac6cec3e4db2e9cc390cc7448390799d25b049617098255f71b0841c11fde2c1b83e740274d500ceefab9c9f2d0b4f9051d62270694f8c09ffa6dac0'),
(51, 'Ana', 'Rodríguez', 'ana.rodriguez@email.com', '3001111112', '1', '102', 'RESIDENTE', 'INACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(52, 'Luis', 'Martínez', 'luis.martinez@email.com', '3001111113', '1', '103', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(53, 'María', 'López', 'maria.lopez@email.com', '3001111114', '1', '104', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(54, 'Javier', 'Hernández', 'javier.hernandez@email.com', '3001111115', '1', '105', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(55, 'Laura', 'García', 'laura.garcia@email.com', '3001111116', '1', '106', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(56, 'Miguel', 'Pérez', 'miguel.perez@email.com', '3001111117', '1', '107', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(57, 'Isabel', 'Sánchez', 'isabel.sanchez@email.com', '3001111118', '1', '108', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(58, 'Ricardo', 'Ramírez', 'ricardo.ramirez@email.com', '3001111119', '1', '109', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(59, 'Patricia', 'Flores', 'patricia.flores@email.com', '3001111120', '1', '110', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(60, 'Fernando', 'Díaz', 'fernando.diaz@email.com', '3001111121', '2', '201', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(61, 'Carmen', 'Torres', 'carmen.torres@email.com', '3001111122', '2', '202', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(62, 'Roberto', 'Vargas', 'roberto.vargas@email.com', '3001111123', '2', '203', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(63, 'Elena', 'Castro', 'elena.castro@email.com', '3001111124', '2', '204', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(64, 'Diego', 'Ortega', 'diego.ortega@email.com', '3001111125', '2', '205', 'RESIDENTE', 'ACTIVO', 'scrypt:32768:8:1$VsOYwkjMzxEDh4EV$cfc55122300ff4f8b97effb22b44951617e9f0ded3fbb30a4f24cad4ec886aa1f44b89bcc7573c297392acf5d2551d05efd65867ba14ff95f0eabd1d0cd36269'),
(65, 'Sandra', 'Reyes', 'sandra.reyes@email.com', '3001111126', '2', '206', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(66, 'Andrés', 'Morales', 'andres.morales@email.com', '3001111127', '2', '207', 'RESIDENTE', 'ACTIVO', 'scrypt:32768:8:1$BdRBuY0MJcIIOu5I$7a7b4facf5453daf647097f76cfa3dfb89591ec7d1b1facfbe6e16ea69c5291b4eb261be71812099796ac680e0b6661dcdd6fb5ad41aaedb2e2953a004dd8506'),
(67, 'Gabriela', 'Rojas', 'gabriela.rojas@email.com', '3001111128', '2', '208', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(68, 'Oscar', 'Guerrero', 'oscar.guerrero@email.com', '3001111129', '2', '209', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(69, 'Lucía', 'Mendoza', 'lucia.mendoza@email.com', '3001111130', '2', '210', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(70, 'Héctor', 'Silva', 'hector.silva@email.com', '3001111131', '3', '301', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(71, 'Verónica', 'Peña', 'veronica.pena@email.com', '3001111132', '3', '302', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(72, 'Raúl', 'Cruz', 'raul.cruz@email.com', '3001111133', '3', '303', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(73, 'Daniela', 'Navarro', 'daniela.navarro@email.com', '3001111134', '3', '304', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(74, 'Arturo', 'Salazar', 'arturo.salazar@email.com', '3001111135', '3', '305', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(75, 'Adriana', 'Mejía', 'adriana.mejia@email.com', '3001111136', '3', '306', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(76, 'Felipe', 'Córdoba', 'felipe.cordoba@email.com', '3001111137', '3', '307', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(77, 'Natalia', 'Herrera', 'natalia.herrera@email.com', '3001111138', '3', '308', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(78, 'Mauricio', 'Aguilar', 'mauricio.aguilar@email.com', '3001111139', '3', '309', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(79, 'Claudia', 'Paredes', 'claudia.paredes@email.com', '3001111140', '3', '310', 'RESIDENTE', 'ACTIVO', 'pbkdf2:sha256:600000$default$default_hash'),
(80, 'Uldarico', 'Andrade', 'uldandra@gmail.com', '3144902872', NULL, NULL, 'ADMINISTRADOR', 'ACTIVO', 'scrypt:32768:8:1$kL7gZeOSlUVEkWTX$ff3cff28a9a76d1f42d7f51de0ba30654f28c852bb8d190f55ef22413d383d56b4ea303a322c1cfccba21ab456c5cf6696f271809322f3450eb5a749fabcbd57');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vehiculo`
--

CREATE TABLE `vehiculo` (
  `ID_VEHICULO` int(11) NOT NULL,
  `ID_USUARIO` int(11) NOT NULL,
  `TIPO` enum('CARRO','MOTO','BICICLETA') NOT NULL,
  `PLACA` varchar(10) DEFAULT NULL,
  `FECHA_FIN_SOAT` date DEFAULT NULL,
  `DOC_SOAT` varchar(255) DEFAULT NULL,
  `DOC_IDENTIDAD` varchar(255) DEFAULT NULL,
  `DOC_TARJETA_PROPIEDAD` varchar(255) DEFAULT NULL,
  `FECHA_REGISTRO` datetime DEFAULT current_timestamp(),
  `ESTADO` enum('PENDIENTE','APROBADO','RECHAZADO') DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `vehiculo`
--

INSERT INTO `vehiculo` (`ID_VEHICULO`, `ID_USUARIO`, `TIPO`, `PLACA`, `FECHA_FIN_SOAT`, `DOC_SOAT`, `DOC_IDENTIDAD`, `DOC_TARJETA_PROPIEDAD`, `FECHA_REGISTRO`, `ESTADO`) VALUES
(1, 50, 'CARRO', 'NET817', NULL, 'NET817_soat_20251119_215544.pdf', 'NET817_identidad_20251119_215544.pdf', 'NET817_tarjeta_propiedad_20251119_215544.pdf', '2025-11-19 21:55:44', 'APROBADO'),
(2, 66, 'CARRO', 'NET342', NULL, 'NET342_soat_20251120_082357.pdf', 'NET342_identidad_20251120_082357.pdf', 'NET342_tarjeta_propiedad_20251120_082357.pdf', '2025-11-20 08:23:57', 'APROBADO');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `voluntariado`
--

CREATE TABLE `voluntariado` (
  `ID_VOLUNTARIADO` int(11) NOT NULL,
  `NOMBRE` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `voluntario`
--

CREATE TABLE `voluntario` (
  `ID_VOLUNTARIO` int(11) NOT NULL,
  `NOMBRE` varchar(100) NOT NULL,
  `ACTIVIDAD` varchar(100) NOT NULL,
  `DISPONIBILIDAD` varchar(50) NOT NULL,
  `CONTACTO` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `actividad`
--
ALTER TABLE `actividad`
  ADD PRIMARY KEY (`ID_ACTIVIDAD`),
  ADD KEY `USUARIO_ID` (`USUARIO_ID`);

--
-- Indices de la tabla `anuncio`
--
ALTER TABLE `anuncio`
  ADD PRIMARY KEY (`ID_ANUNCIO`),
  ADD KEY `PUBLICADO_POR` (`PUBLICADO_POR`);

--
-- Indices de la tabla `aviso`
--
ALTER TABLE `aviso`
  ADD PRIMARY KEY (`ID_AVISO`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `correspondencia`
--
ALTER TABLE `correspondencia`
  ADD PRIMARY KEY (`ID_CORRESPONDENCIA`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `detalle_instrumental`
--
ALTER TABLE `detalle_instrumental`
  ADD PRIMARY KEY (`ID_PRESTAMO`,`ID_INSTRUMENTAL`),
  ADD KEY `ID_INSTRUMENTAL` (`ID_INSTRUMENTAL`);

--
-- Indices de la tabla `detalle_prestamo`
--
ALTER TABLE `detalle_prestamo`
  ADD PRIMARY KEY (`ID_PRESTAMO`,`ID_USUARIO`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `detalle_reserva`
--
ALTER TABLE `detalle_reserva`
  ADD PRIMARY KEY (`ID_RESERVA`,`ID_ESPACIO`),
  ADD KEY `ID_ESPACIO` (`ID_ESPACIO`);

--
-- Indices de la tabla `detalle_sorteo`
--
ALTER TABLE `detalle_sorteo`
  ADD PRIMARY KEY (`ID_USUARIO`,`ID_SORTEO`,`ID_PARQUEADERO`),
  ADD KEY `ID_SORTEO` (`ID_SORTEO`),
  ADD KEY `ID_PARQUEADERO` (`ID_PARQUEADERO`);

--
-- Indices de la tabla `documento_vehiculo`
--
ALTER TABLE `documento_vehiculo`
  ADD PRIMARY KEY (`ID_DOCUMENTO`),
  ADD KEY `ID_VEHICULO` (`ID_VEHICULO`);

--
-- Indices de la tabla `espacio_comunal`
--
ALTER TABLE `espacio_comunal`
  ADD PRIMARY KEY (`ID_ESPACIO`);

--
-- Indices de la tabla `evento`
--
ALTER TABLE `evento`
  ADD PRIMARY KEY (`ID_EVENTO`),
  ADD KEY `CREADO_POR` (`CREADO_POR`);

--
-- Indices de la tabla `gestion_espera`
--
ALTER TABLE `gestion_espera`
  ADD PRIMARY KEY (`ID_ESPERA`),
  ADD KEY `SOLICITADO_POR` (`SOLICITADO_POR`);

--
-- Indices de la tabla `incidente`
--
ALTER TABLE `incidente`
  ADD PRIMARY KEY (`ID_INCIDENTE`),
  ADD KEY `REPORTADO_POR` (`REPORTADO_POR`);

--
-- Indices de la tabla `inscripcion_evento`
--
ALTER TABLE `inscripcion_evento`
  ADD PRIMARY KEY (`ID_RESERVA`,`ID_USUARIO`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `instrumental`
--
ALTER TABLE `instrumental`
  ADD PRIMARY KEY (`ID_INSTRUMENTAL`);

--
-- Indices de la tabla `paquete`
--
ALTER TABLE `paquete`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `parqueadero`
--
ALTER TABLE `parqueadero`
  ADD PRIMARY KEY (`ID_PARQUEADERO`);

--
-- Indices de la tabla `prestamo`
--
ALTER TABLE `prestamo`
  ADD PRIMARY KEY (`ID_PRESTAMO`);

--
-- Indices de la tabla `prestamo_parqueadero`
--
ALTER TABLE `prestamo_parqueadero`
  ADD PRIMARY KEY (`ID_PRESTAMO`),
  ADD KEY `RESIDENTE_ID` (`RESIDENTE_ID`);

--
-- Indices de la tabla `recibo`
--
ALTER TABLE `recibo`
  ADD PRIMARY KEY (`ID_RECIBO`),
  ADD KEY `RESIDENTE_ID` (`RESIDENTE_ID`);

--
-- Indices de la tabla `recordatorio_evento`
--
ALTER TABLE `recordatorio_evento`
  ADD PRIMARY KEY (`ID_RECORDATORIO`),
  ADD KEY `ID_RESERVA` (`ID_RESERVA`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD PRIMARY KEY (`ID_REPORTE`),
  ADD KEY `CREADO_POR` (`CREADO_POR`);

--
-- Indices de la tabla `reserva`
--
ALTER TABLE `reserva`
  ADD PRIMARY KEY (`ID_RESERVA`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `sorteo`
--
ALTER TABLE `sorteo`
  ADD PRIMARY KEY (`ID_SORTEO`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`ID_USUARIO`);

--
-- Indices de la tabla `vehiculo`
--
ALTER TABLE `vehiculo`
  ADD PRIMARY KEY (`ID_VEHICULO`),
  ADD KEY `ID_USUARIO` (`ID_USUARIO`);

--
-- Indices de la tabla `voluntariado`
--
ALTER TABLE `voluntariado`
  ADD PRIMARY KEY (`ID_VOLUNTARIADO`);

--
-- Indices de la tabla `voluntario`
--
ALTER TABLE `voluntario`
  ADD PRIMARY KEY (`ID_VOLUNTARIO`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `actividad`
--
ALTER TABLE `actividad`
  MODIFY `ID_ACTIVIDAD` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `anuncio`
--
ALTER TABLE `anuncio`
  MODIFY `ID_ANUNCIO` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `documento_vehiculo`
--
ALTER TABLE `documento_vehiculo`
  MODIFY `ID_DOCUMENTO` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `evento`
--
ALTER TABLE `evento`
  MODIFY `ID_EVENTO` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gestion_espera`
--
ALTER TABLE `gestion_espera`
  MODIFY `ID_ESPERA` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `incidente`
--
ALTER TABLE `incidente`
  MODIFY `ID_INCIDENTE` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `paquete`
--
ALTER TABLE `paquete`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `prestamo_parqueadero`
--
ALTER TABLE `prestamo_parqueadero`
  MODIFY `ID_PRESTAMO` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recibo`
--
ALTER TABLE `recibo`
  MODIFY `ID_RECIBO` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recordatorio_evento`
--
ALTER TABLE `recordatorio_evento`
  MODIFY `ID_RECORDATORIO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `reporte`
--
ALTER TABLE `reporte`
  MODIFY `ID_REPORTE` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reserva`
--
ALTER TABLE `reserva`
  MODIFY `ID_RESERVA` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `sorteo`
--
ALTER TABLE `sorteo`
  MODIFY `ID_SORTEO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=160;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `ID_USUARIO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=81;

--
-- AUTO_INCREMENT de la tabla `vehiculo`
--
ALTER TABLE `vehiculo`
  MODIFY `ID_VEHICULO` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `voluntario`
--
ALTER TABLE `voluntario`
  MODIFY `ID_VOLUNTARIO` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `actividad`
--
ALTER TABLE `actividad`
  ADD CONSTRAINT `actividad_ibfk_1` FOREIGN KEY (`USUARIO_ID`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `anuncio`
--
ALTER TABLE `anuncio`
  ADD CONSTRAINT `anuncio_ibfk_1` FOREIGN KEY (`PUBLICADO_POR`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `aviso`
--
ALTER TABLE `aviso`
  ADD CONSTRAINT `aviso_ibfk_1` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `correspondencia`
--
ALTER TABLE `correspondencia`
  ADD CONSTRAINT `correspondencia_ibfk_1` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `detalle_instrumental`
--
ALTER TABLE `detalle_instrumental`
  ADD CONSTRAINT `detalle_instrumental_ibfk_1` FOREIGN KEY (`ID_PRESTAMO`) REFERENCES `prestamo` (`ID_PRESTAMO`),
  ADD CONSTRAINT `detalle_instrumental_ibfk_2` FOREIGN KEY (`ID_INSTRUMENTAL`) REFERENCES `instrumental` (`ID_INSTRUMENTAL`);

--
-- Filtros para la tabla `detalle_prestamo`
--
ALTER TABLE `detalle_prestamo`
  ADD CONSTRAINT `detalle_prestamo_ibfk_1` FOREIGN KEY (`ID_PRESTAMO`) REFERENCES `prestamo` (`ID_PRESTAMO`),
  ADD CONSTRAINT `detalle_prestamo_ibfk_2` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `detalle_reserva`
--
ALTER TABLE `detalle_reserva`
  ADD CONSTRAINT `detalle_reserva_ibfk_1` FOREIGN KEY (`ID_RESERVA`) REFERENCES `reserva` (`ID_RESERVA`),
  ADD CONSTRAINT `detalle_reserva_ibfk_2` FOREIGN KEY (`ID_ESPACIO`) REFERENCES `espacio_comunal` (`ID_ESPACIO`);

--
-- Filtros para la tabla `detalle_sorteo`
--
ALTER TABLE `detalle_sorteo`
  ADD CONSTRAINT `detalle_sorteo_ibfk_1` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`),
  ADD CONSTRAINT `detalle_sorteo_ibfk_2` FOREIGN KEY (`ID_SORTEO`) REFERENCES `sorteo` (`ID_SORTEO`),
  ADD CONSTRAINT `detalle_sorteo_ibfk_3` FOREIGN KEY (`ID_PARQUEADERO`) REFERENCES `parqueadero` (`ID_PARQUEADERO`);

--
-- Filtros para la tabla `documento_vehiculo`
--
ALTER TABLE `documento_vehiculo`
  ADD CONSTRAINT `documento_vehiculo_ibfk_1` FOREIGN KEY (`ID_VEHICULO`) REFERENCES `vehiculo` (`ID_VEHICULO`) ON DELETE CASCADE;

--
-- Filtros para la tabla `evento`
--
ALTER TABLE `evento`
  ADD CONSTRAINT `evento_ibfk_1` FOREIGN KEY (`CREADO_POR`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `gestion_espera`
--
ALTER TABLE `gestion_espera`
  ADD CONSTRAINT `gestion_espera_ibfk_1` FOREIGN KEY (`SOLICITADO_POR`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `incidente`
--
ALTER TABLE `incidente`
  ADD CONSTRAINT `incidente_ibfk_1` FOREIGN KEY (`REPORTADO_POR`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `inscripcion_evento`
--
ALTER TABLE `inscripcion_evento`
  ADD CONSTRAINT `inscripcion_evento_ibfk_1` FOREIGN KEY (`ID_RESERVA`) REFERENCES `reserva` (`ID_RESERVA`),
  ADD CONSTRAINT `inscripcion_evento_ibfk_2` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `prestamo_parqueadero`
--
ALTER TABLE `prestamo_parqueadero`
  ADD CONSTRAINT `prestamo_parqueadero_ibfk_1` FOREIGN KEY (`RESIDENTE_ID`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `recibo`
--
ALTER TABLE `recibo`
  ADD CONSTRAINT `recibo_ibfk_1` FOREIGN KEY (`RESIDENTE_ID`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `recordatorio_evento`
--
ALTER TABLE `recordatorio_evento`
  ADD CONSTRAINT `recordatorio_evento_ibfk_1` FOREIGN KEY (`ID_RESERVA`) REFERENCES `reserva` (`ID_RESERVA`),
  ADD CONSTRAINT `recordatorio_evento_ibfk_2` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD CONSTRAINT `reporte_ibfk_1` FOREIGN KEY (`CREADO_POR`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `reserva`
--
ALTER TABLE `reserva`
  ADD CONSTRAINT `reserva_ibfk_1` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `sorteo`
--
ALTER TABLE `sorteo`
  ADD CONSTRAINT `sorteo_ibfk_1` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);

--
-- Filtros para la tabla `vehiculo`
--
ALTER TABLE `vehiculo`
  ADD CONSTRAINT `vehiculo_ibfk_1` FOREIGN KEY (`ID_USUARIO`) REFERENCES `usuario` (`ID_USUARIO`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
