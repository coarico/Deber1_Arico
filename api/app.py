from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'db')
db_name = os.getenv('DB_NAME', 'master')

# Cadena de conexión mejorada
connection_string = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=no&encrypt=no"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Producto Automotriz
class ProductoAutomotriz(db.Model):
    __tablename__ = 'productos_automotrices'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50), nullable=False)  # aceite, frenos, filtros, etc.
    marca = db.Column(db.String(50))
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    especificaciones = db.Column(db.Text)  # JSON con especificaciones técnicas
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'marca': self.marca,
            'precio': float(self.precio) if self.precio else None,
            'stock': self.stock,
            'especificaciones': json.loads(self.especificaciones) if self.especificaciones else {},
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'activo': self.activo
        }

    def __repr__(self):
        return f'<ProductoAutomotriz {self.codigo} - {self.nombre}>'

# Crear tablas al iniciar
try:
    with app.app_context():
        db.create_all()
    print("Tablas creadas correctamente")
except Exception as e:
    print("Error al crear tablas")
    print(str(e))

# Función para esperar a que SQL Server esté listo
def wait_for_db():
    max_retries = 10
    for i in range(1, max_retries + 1):
        try:
            print(f"Intento {i}/{max_retries}: Conectando a la base de datos...")
            print(f"Cadena de conexión: {connection_string.replace(db_password, '********')}")

            with app.app_context():
                # Verificar si la base de datos existe, si no, crearla
                if db_name != 'master':
                    print(f"Verificando/creando base de datos {db_name}...")
                    db.session.execute(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{db_name}') CREATE DATABASE {db_name}")
                    db.session.commit()

                # Crear tablas
                db.create_all()

            print("✅ Conexión exitosa a la base de datos")
            return True

        except Exception as e:
            error_msg = str(e).replace(db_password, '********')
            print(f"❌ Error en el intento {i}/{max_retries}: {error_msg}")
            if i < max_retries:
                print("Esperando 5 segundos antes de reintentar...\n")
                time.sleep(5)

    print("❌ Error: No se pudo conectar a la base de datos después de varios intentos")
    return False

# Funciones de utilidad
def validar_especificaciones(especificaciones):
    try:
        if especificaciones:
            if isinstance(especificaciones, str):
                json.loads(especificaciones)
            else:
                json.dumps(especificaciones)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def handle_error(message, status_code=400):
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

# Decorador para manejar errores comunes

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return handle_error(str(e), 500)
    return wrapper

# Endpoints de la API

@app.route('/api/productos', methods=['GET'])
@handle_errors
def obtener_productos():
    # Filtros
    categoria = request.args.get('categoria')
    marca = request.args.get('marca')
    activo = request.args.get('activo', 'true').lower() == 'true'
    
    query = ProductoAutomotriz.query.filter_by(activo=activo)
    
    if categoria:
        query = query.filter(ProductoAutomotriz.categoria.ilike(f'%{categoria}%'))
    if marca:
        query = query.filter(ProductoAutomotriz.marca.ilike(f'%{marca}%'))
    
    productos = query.all()
    return jsonify([p.to_dict() for p in productos])

@app.route('/api/productos/<int:id>', methods=['GET'])
@handle_errors
def obtener_producto(id):
    producto = ProductoAutomotriz.query.get_or_404(id)
    return jsonify(producto.to_dict())

@app.route('/api/productos', methods=['POST'])
@handle_errors
def crear_producto():
    data = request.get_json()
    
    # Validaciones
    if not data.get('codigo') or not data.get('nombre') or not data.get('categoria') or 'precio' not in data:
        return handle_error('Faltan campos requeridos', 400)
    
    if not validar_especificaciones(data.get('especificaciones')):
        return handle_error('Formato de especificaciones inválido. Debe ser un JSON válido', 400)
    
    # Verificar si ya existe un producto con el mismo código
    if ProductoAutomotriz.query.filter_by(codigo=data['codigo']).first():
        return handle_error('Ya existe un producto con este código', 400)
    
    try:
        producto = ProductoAutomotriz(
            codigo=data['codigo'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            categoria=data['categoria'],
            marca=data.get('marca'),
            precio=data['precio'],
            stock=data.get('stock', 0),
            especificaciones=json.dumps(data.get('especificaciones', {})) if data.get('especificaciones') else None,
            activo=data.get('activo', True)
        )
        
        db.session.add(producto)
        db.session.commit()
        
        return jsonify(producto.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return handle_error(str(e), 500)

@app.route('/api/productos/<int:id>', methods=['PUT'])
@handle_errors
def actualizar_producto(id):
    producto = ProductoAutomotriz.query.get_or_404(id)
    data = request.get_json()
    
    if 'especificaciones' in data and not validar_especificaciones(data['especificaciones']):
        return handle_error('Formato de especificaciones inválido', 400)
    
    try:
        # Actualizar solo los campos proporcionados
        if 'codigo' in data and data['codigo'] != producto.codigo:
            if ProductoAutomotriz.query.filter_by(codigo=data['codigo']).first():
                return handle_error('Ya existe otro producto con este código', 400)
            producto.codigo = data['codigo']
        
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'categoria' in data:
            producto.categoria = data['categoria']
        if 'marca' in data:
            producto.marca = data['marca']
        if 'precio' in data:
            producto.precio = data['precio']
        if 'stock' in data:
            producto.stock = data['stock']
        if 'especificaciones' in data:
            producto.especificaciones = json.dumps(data['especificaciones']) if data['especificaciones'] else None
        if 'activo' in data:
            producto.activo = data['activo']
        
        db.session.commit()
        return jsonify(producto.to_dict())
    except Exception as e:
        db.session.rollback()
        return handle_error(str(e), 500)

@app.route('/api/productos/<int:id>', methods=['DELETE'])
@handle_errors
def eliminar_producto(id):
    producto = ProductoAutomotriz.query.get_or_404(id)
    
    try:
        # En lugar de eliminar, marcamos como inactivo (borrado lógico)
        producto.activo = False
        db.session.commit()
        return jsonify({'mensaje': 'Producto desactivado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return handle_error(str(e), 500)

# Endpoint adicional para búsqueda avanzada
@app.route('/api/productos/buscar', methods=['GET'])
@handle_errors
def buscar_productos():
    termino = request.args.get('q', '').strip()
    if not termino:
        return jsonify([])
    
    resultados = ProductoAutomotriz.query.filter(
        (ProductoAutomotriz.nombre.ilike(f'%{termino}%')) |
        (ProductoAutomotriz.descripcion.ilike(f'%{termino}%')) |
        (ProductoAutomotriz.codigo.ilike(f'%{termino}%'))
    ).filter_by(activo=True).all()
    
    return jsonify([p.to_dict() for p in resultados])

@app.route('/')
def index():
    return jsonify({
        'mensaje': 'API de Productos Automotrices',
        'version': '1.0.0',
        'endpoints': {
            'obtener_todos': {'method': 'GET', 'ruta': '/api/productos'},
            'obtener_por_id': {'method': 'GET', 'ruta': '/api/productos/<id>'},
            'crear': {'method': 'POST', 'ruta': '/api/productos'},
            'actualizar': {'method': 'PUT', 'ruta': '/api/productos/<id>'},
            'eliminar': {'method': 'DELETE', 'ruta': '/api/productos/<id>', 'nota': 'Eliminación lógica'},
            'buscar': {'method': 'GET', 'ruta': '/api/productos/buscar?q=<termino>'}
        }
    })

if __name__ == '__main__':
    # Esperar a que SQL Server esté listo antes de iniciar la API
    if wait_for_db():
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Error: No se pudo iniciar la API - SQL Server no disponible")
