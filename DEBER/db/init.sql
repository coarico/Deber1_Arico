-- Script de inicialización de la base de datos
IF NOT EXISTS(SELECT * FROM sys.databases WHERE name='automotriz_db')
BEGIN
    CREATE DATABASE automotriz_db;
    PRINT 'Base de datos automotriz_db creada correctamente';
END
GO

USE automotriz_db;
GO

-- Tabla de productos automotrices
IF NOT EXISTS(SELECT * FROM sys.tables WHERE name='productos_automotrices')
BEGIN
    CREATE TABLE productos_automotrices (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo NVARCHAR(50) NOT NULL UNIQUE,
        nombre NVARCHAR(100) NOT NULL,
        descripcion NVARCHAR(MAX),
        categoria NVARCHAR(50) NOT NULL,
        marca NVARCHAR(50),
        precio DECIMAL(10,2) NOT NULL,
        stock INT DEFAULT 0,
        especificaciones NVARCHAR(MAX),
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        activo BIT DEFAULT 1
    );
    PRINT 'Tabla productos_automotrices creada correctamente';
    
    -- Crear índices para mejorar el rendimiento
    CREATE INDEX idx_productos_categoria ON productos_automotrices(categoria);
    CREATE INDEX idx_productos_marca ON productos_automotrices(marca);
    CREATE INDEX idx_productos_activo ON productos_automotrices(activo);
    CREATE INDEX idx_productos_codigo ON productos_automotrices(codigo);
END
GO

-- Datos iniciales
IF NOT EXISTS (SELECT 1 FROM productos_automotrices)
BEGIN
    -- Insertar categorías comunes
    INSERT INTO productos_automotrices (codigo, nombre, descripcion, categoria, marca, precio, stock, especificaciones, activo)
    VALUES 
    ('ACE-001', 'Aceite Sintético 5W-30', 'Aceite de motor sintético de alto rendimiento', 'Aceites', 'Mobil', 29.99, 100, '{"viscosidad": "5W-30", "tipo": "Sintético", "capacidad_litros": 4, "api": "SN Plus", "aceite_base": "Grupo III"}', 1),
    
    ('FREN-001', 'Pastillas de Freno Delanteras', 'Juego de pastillas de freno delanteras', 'Frenos', 'Brembo', 89.99, 50, '{"tipo": "Cerámicas", "material": "Compuesto cerámico", "compatible_con": ["Toyota", "Honda", "Nissan"], "duracion_km": 60000}', 1),
    
    ('FILT-001', 'Filtro de Aire Premium', 'Filtro de aire de alto flujo', 'Filtros', 'K&N', 49.99, 75, '{"tipo": "Alto flujo", "material": "Algodón engrasado", "lavable": true, "duracion_km": 80000}', 1),
    
    ('BAT-001', 'Batería 12V 60Ah', 'Batería de plomo-ácido sellada', 'Baterías', 'Bosch', 129.99, 30, '{"tipo": "Plomo-ácido", "voltaje": 12, "capacidad_ah": 60, "polaridad": "Directa", "garantia_meses": 24}', 1),
    
    ('LUCES-001', 'Kit de Luces LED H7', 'Juego de luces LED para faros principales', 'Iluminación', 'Philips', 79.99, 40, '{"tipo": "LED", "temperatura_color": 6000, "lumenes": 3200, "vida_util_horas": 50000, "resistente_agua": true}', 1),
    
    ('ACE-002', 'Aceite Semisintético 10W-40', 'Aceite semisintético para todo tipo de motores', 'Aceites', 'Castrol', 24.99, 150, '{"viscosidad": "10W-40", "tipo": "Semisintético", "capacidad_litros": 5, "api": "SN", "aceite_base": "Grupo II+"}', 1),
    
    ('LUB-001', 'Grasa Multipropósito', 'Grasa de litio para múltiples aplicaciones', 'Lubricantes', 'Mobil', 12.99, 200, '{"tipo": "Grasa de litio", "temperatura_min": -30, "temperatura_max": 130, "unidad_medida": "400g", "aplicaciones": ["Chasis", "Ruedas", "Suspensión"]}', 1);
    
    PRINT 'Datos de ejemplo insertados correctamente';
END
ELSE
BEGIN
    PRINT 'La tabla ya contiene datos, no se insertaron registros de ejemplo';
END
GO
