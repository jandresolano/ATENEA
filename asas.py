from werkzeug.security import generate_password_hash

# Fuerza el uso de pbkdf2:sha256
password_hash = generate_password_hash('tu_contraseña_administrador', method='pbkdf2:sha256')
print(password_hash)

# Fuerza el uso de pbkdf2:sha256
password_hash = generate_password_hash('123456', method='pbkdf2:sha256')
print(password_hash)