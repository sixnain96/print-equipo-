-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 05-05-2025 a las 13:47:47
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `ferreteria`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimientos_stock`
--

CREATE TABLE `movimientos_stock` (
  `id` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `tipo_movimiento` enum('entrada','salida') NOT NULL,
  `cantidad` int(11) NOT NULL,
  `usuario` int(11) NOT NULL,
  `fecha_movimiento` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `movimientos_stock`
--

INSERT INTO `movimientos_stock` (`id`, `id_producto`, `tipo_movimiento`, `cantidad`, `usuario`, `fecha_movimiento`) VALUES
(2, 2, 'salida', 5, 2, '2025-04-25 19:29:57'),
(3, 3, 'salida', 20, 2, '2025-04-25 19:29:57'),
(4, 4, 'salida', 2, 1, '2025-04-25 19:29:57'),
(6, 2, 'entrada', 30, 1, '2025-04-25 19:29:57'),
(7, 3, 'entrada', 100, 2, '2025-04-25 19:29:57'),
(8, 4, 'entrada', 15, 2, '2025-04-25 19:29:57'),
(10, 2, 'salida', 3, 1, '2025-04-27 20:21:42');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `categoria` varchar(255) NOT NULL,
  `codigo_sku` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio_venta` decimal(10,2) NOT NULL,
  `precio_compra` decimal(10,2) DEFAULT NULL,
  `stock_actual` int(11) NOT NULL DEFAULT 0,
  `proveedor` varchar(255) DEFAULT NULL,
  `ubicacion_almacen` varchar(255) DEFAULT NULL,
  `cantidad_minima` int(11) DEFAULT 0,
  `fecha_ingreso` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `nombre`, `categoria`, `codigo_sku`, `descripcion`, `precio_venta`, `precio_compra`, `stock_actual`, `proveedor`, `ubicacion_almacen`, `cantidad_minima`, `fecha_ingreso`) VALUES
(2, 'Martillo', 'Ferretería', 'SKU002', 'Martillo de 500 gramos', 250.00, 150.00, 47, 'Proveedora Ferretera S.A.', 'Estante B', 10, '2025-04-25 19:29:57'),
(3, 'Destornillador', 'Ferretería', 'SKU003', 'Destornillador de precisión', 80.00, 50.00, 200, 'Herramientas XYZ', 'Estante C', 30, '2025-04-25 19:29:57'),
(4, 'Taladro', 'Ferretería', 'SKU004', 'Taladro eléctrico de 500W', 1600.00, 300.00, 50, 'Herramientas Pro', 'Estante D', 5, '2025-04-25 19:29:57');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respaldos`
--

CREATE TABLE `respaldos` (
  `id` int(11) NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `fecha_respaldo` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre_usuario` varchar(255) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  `rol` enum('admin','empleado') NOT NULL,
  `email` varchar(255) NOT NULL,
  `clave_2fa` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre_usuario`, `contraseña`, `rol`, `email`, `clave_2fa`) VALUES
(1, 'admin', '$2b$12$oTVr8QP2PRl5PITCAIhHU.cl/TRGdyg4HD/fy7970rbcxO6zo3kwC', 'admin', 'admin@ferreteria.com', 'OWRMS44ZUFTH42IQRGJKILNBWL3EXMQX'),
(2, 'empleado', '$2b$12$dz8.6Ay2mpjG1R8jn/M/7OCcpN9XYn6j2wXOdP.H5DUNdtvAhNnkO', 'empleado', 'empleado@ferreteria.com', 'I5YFGQEJNAI7ILPIVITVA57MWYHCZTKN');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad_vendida` int(11) NOT NULL,
  `total_venta` decimal(10,2) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_venta` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`id`, `id_producto`, `cantidad_vendida`, `total_venta`, `id_usuario`, `fecha_venta`) VALUES
(2, 2, 5, 1250.00, 2, '2025-04-25 19:29:57'),
(4, 2, 2, 900.00, 1, '2025-04-25 19:29:57'),
(9, 2, 3, 750.00, 1, '2025-04-27 20:21:42');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `movimientos_stock`
--
ALTER TABLE `movimientos_stock`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_producto` (`id_producto`),
  ADD KEY `usuario` (`usuario`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo_sku` (`codigo_sku`);

--
-- Indices de la tabla `respaldos`
--
ALTER TABLE `respaldos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre_usuario` (`nombre_usuario`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_producto` (`id_producto`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `movimientos_stock`
--
ALTER TABLE `movimientos_stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `respaldos`
--
ALTER TABLE `respaldos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `movimientos_stock`
--
ALTER TABLE `movimientos_stock`
  ADD CONSTRAINT `movimientos_stock_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `movimientos_stock_ibfk_2` FOREIGN KEY (`usuario`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
