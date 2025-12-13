from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from mysql.connector import Error
import os

# Inicialización de SQLAlchemy
db = SQLAlchemy()

# =========================
# Validación de variables de entorno
# =========================
required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]

for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Falta la variable de entorno: {var}")

# =========================
# Prueba de conexión a la base de datos
# =========================
def test_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
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

# =========================
# Inicialización de la base de datos
# =========================
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
