import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
 
app = Flask(__name__)
CORS(app)
 
# ================================================
# CONEXION A LA BASE DE DATOS
# Cambia "tu_password" por la contraseña de MySQL
# ================================================
def get_db():
    return mysql.connector.connect(
        host=os.environ.get('MYSQLHOST', 'localhost'),
        user=os.environ.get('MYSQLUSER', 'root'),
        password=os.environ.get('MYSQLPASSWORD', 'tu_password'),
        database=os.environ.get('MYSQLDATABASE', 'importaciones_db'),
        port=int(os.environ.get('MYSQLPORT', 3306))
    )
 
 
# ================================================
# PROVEEDORES
# ================================================
 
# Obtener todos los proveedores
@app.route('/proveedores', methods=['GET'])
def get_proveedores():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores")
    resultado = cursor.fetchall()
    db.close()
    return jsonify(resultado)
 
# Crear un proveedor
@app.route('/proveedores', methods=['POST'])
def create_proveedor():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO proveedores (nombre, pais, contacto, condiciones_pago) VALUES (%s, %s, %s, %s)",
        (data['nombre'], data.get('pais'), data.get('contacto'), data.get('condiciones_pago'))
    )
    db.commit()
    db.close()
    return jsonify({'mensaje': 'Proveedor creado', 'id': cursor.lastrowid}), 201
 
 
# ================================================
# IMPORTACIONES
# ================================================
 
# Obtener todas las importaciones con nombre del proveedor
@app.route('/importaciones', methods=['GET'])
def get_importaciones():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.*, p.nombre as proveedor_nombre
        FROM importaciones i
        JOIN proveedores p ON i.proveedor_id = p.id
        ORDER BY i.creado_en DESC
    """)
    resultado = cursor.fetchall()
    db.close()
    return jsonify(resultado)
 
# Obtener una importacion por id
@app.route('/importaciones/<int:id>', methods=['GET'])
def get_importacion(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.*, p.nombre as proveedor_nombre
        FROM importaciones i
        JOIN proveedores p ON i.proveedor_id = p.id
        WHERE i.id = %s
    """, (id,))
    resultado = cursor.fetchone()
    db.close()
    return jsonify(resultado)
 
# Crear una importacion
@app.route('/importaciones', methods=['POST'])
def create_importacion():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO importaciones
        (proveedor_id, fecha_pedido, monto_pedido, moneda, numero_seguimiento,
         forwarder, producto, comentario, estado, fecha_estimada_llegada)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['proveedor_id'],
        data['fecha_pedido'],
        data.get('monto_pedido'),
        data.get('moneda'),
        data.get('numero_seguimiento'),
        data.get('forwarder'),
        data.get('producto'),
        data.get('comentario'),
        data.get('estado', 'en_transito'),
        data.get('fecha_estimada_llegada')
    ))
    db.commit()
    db.close()
    return jsonify({'mensaje': 'Importacion creada', 'id': cursor.lastrowid}), 201
 
# Actualizar estado CDA
@app.route('/importaciones/<int:id>/cda', methods=['PUT'])
def update_cda(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE importaciones
        SET estado_cda = %s, fecha_cda = %s
        WHERE id = %s
    """, (data.get('estado_cda'), data.get('fecha_cda'), id))
    db.commit()
    db.close()
    return jsonify({'mensaje': 'CDA actualizado'})
 
 
# ================================================
# FACTURAS
# ================================================
 
# Obtener facturas de una importacion
@app.route('/importaciones/<int:id>/facturas', methods=['GET'])
def get_facturas(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas WHERE importacion_id = %s", (id,))
    resultado = cursor.fetchall()
    db.close()
    return jsonify(resultado)
 
# Crear una factura
@app.route('/importaciones/<int:id>/facturas', methods=['POST'])
def create_factura(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO facturas
        (importacion_id, numero_factura, proveedor_factura, monto, moneda, fecha_factura, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        id,
        data.get('numero_factura'),
        data.get('proveedor_factura'),
        data.get('monto'),
        data.get('moneda'),
        data.get('fecha_factura'),
        data.get('descripcion')
    ))
    db.commit()
    db.close()
    return jsonify({'mensaje': 'Factura creada', 'id': cursor.lastrowid}), 201
 
 
# ================================================
# PAGOS
# ================================================
 
# Obtener pagos de una importacion
@app.route('/importaciones/<int:id>/pagos', methods=['GET'])
def get_pagos(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pagos WHERE importacion_id = %s", (id,))
    resultado = cursor.fetchall()
    db.close()
    return jsonify(resultado)
 
# Crear un pago
@app.route('/importaciones/<int:id>/pagos', methods=['POST'])
def create_pago(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO pagos
        (importacion_id, monto_pagado, moneda, fecha_pago, comprobante, estado_pago)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        id,
        data.get('monto_pagado'),
        data.get('moneda'),
        data.get('fecha_pago'),
        data.get('comprobante'),
        data.get('estado_pago', 'pendiente')
    ))
    db.commit()
    db.close()
    return jsonify({'mensaje': 'Pago registrado', 'id': cursor.lastrowid}), 201
 
 
# ================================================
# INICIAR EL SERVIDOR
# ================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)