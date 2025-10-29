# 🏎️ Sistema de Gestión Automotriz con Docker

## 📌 Detalles del Proyecto
- **Desarrollado por**: Cesar Arico
- **Curso**: Aplicaciones Distribuidas (30046)
- **Tipo de trabajo**: Implementación con Contenedores - API Automotriz
- **Stack Tecnológico**:
  - Lenguaje: Python 3.9
  - Framework Web: Flask
  - Base de Datos: SQL Server 2019
  - ORM: SQLAlchemy
  - Contenedorización: Docker y Docker Compose

## 🔍 Visión General
Solución tecnológica para la administración de inventario de repuestos automotrices, implementando una API RESTful con arquitectura en contenedores para garantizar portabilidad y consistencia en diferentes entornos.

## 📂 Organización del Código
```
.
├── api/
│   ├── app.py           # Lógica principal de la aplicación
│   └── requirements.txt # Bibliotecas de Python necesarias
├── db/
│   └── init.sql         # Configuración inicial de la base de datos
├── .env                 # Configuración de entorno
├── Dockerfile           # Definición del contenedor de la API
├── Dockerfile.db        # Configuración de SQL Server
└── docker-compose.yml   # Orquestación de servicios
```

## ⚙️ Configuración del Entorno

### Archivo de Variables (.env)
```env
# Configuración de la Base de Datos
DB_NAME=automotriz_db
DB_HOST=db
DB_USER=sa
DB_PASSWORD=Deber2023Api
SA_PASSWORD=Deber2023Api
```

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Motor de contenedores Docker
- Herramienta Docker Compose

### Comandos Básicos
```bash
# Iniciar la infraestructura completa
docker-compose up --build -d

# Monitorear registros
docker-compose logs -f

# Detener los servicios
docker-compose down
```

## 📊 Estructura de Datos

### Modelo de Producto
```json
{
  "id": 1,
  "codigo": "ACE-001",
  "nombre": "Aceite Sintético 5W-30",
  "descripcion": "Aceite de alto rendimiento para motores modernos",
  "categoria": "Aceites",
  "marca": "Mobil",
  "precio": 29.99,
  "stock": 100,
  "especificaciones": {
    "viscosidad": "5W-30",
    "tipo": "Sintético",
    "capacidad_litros": 4,
    "api": "SN Plus"
  },
  "fecha_creacion": "2023-10-28T00:00:00",
  "activo": true
}
```

## 🌐 Documentación de la API

### Consulta de Productos
```bash
# Obtener todos los productos
curl http://localhost:5000/api/productos

# Filtrar por categoría específica
curl "http://localhost:5000/api/productos?categoria=Aceites"
```

### Gestión de Productos

#### Consultar por Identificador
```bash
curl http://localhost:5000/api/productos/1
```

#### Registrar Nuevo Producto
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "codigo": "ACE-005",
  "nombre": "Aceite Premium 0W-20",
  "categoria": "Aceites",
  "marca": "Castrol",
  "precio": 49.99,
  "stock": 60,
  "especificaciones": {
    "viscosidad": "0W-20",
    "tipo": "Full Sintético",
    "api": "SP"
  }
}' http://localhost:5000/api/productos
```

#### Modificar Producto Existente
```bash
curl -X PUT -H "Content-Type: application/json" -d '{
  "precio": 54.99,
  "stock": 45
}' http://localhost:5000/api/productos/1
```

#### Desactivar Producto
```bash
curl -X DELETE http://localhost:5000/api/productos/1
```

## 🛠️ Solución de Problemas

### Problemas de Autenticación
1. Confirmar credenciales en el archivo .env
2. Verificar que el usuario SA tenga los permisos necesarios

### Errores de Conexión
1. Revisar el estado de los contenedores:
   ```bash
   docker ps
   ```
2. Examinar registros de la aplicación:
   ```bash
   docker-compose logs -f api
   ```
3. Verificar conectividad entre contenedores:
   ```bash
   docker network inspect bridge
   ```

---
<div align="center">
  🏁 Proyecto académico - Aplicaciones Distribuidas 2023
</div>
