# database.py
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from mysql.connector import Error

db = SQLAlchemy()

def test_db_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,  
            database='sistema_residencial',
            user='root',
            password=''  
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Conectado a MySQL Server versión {db_info}")
            return True
            
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔌 Conexión MySQL cerrada")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        try:
            if test_db_connection():
                db.create_all()
                print("✅ Tablas creadas exitosamente")
            else:
                print("❌ No se pudo conectar a la base de datos. Verifica la configuración.")
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")