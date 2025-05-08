import bcrypt

# Contraseñas en texto plano
password_admin = "admin"
password_empleado = "empleado"

# Ciframos las contraseñas con bcrypt
hashed_admin = bcrypt.hashpw(password_admin.encode('utf-8'), bcrypt.gensalt())
hashed_empleado = bcrypt.hashpw(password_empleado.encode('utf-8'), bcrypt.gensalt())

# Imprimir los hashes cifrados
print("Hash para Admin:", hashed_admin.decode('utf-8'))
print("Hash para Empleado:", hashed_empleado.decode('utf-8'))
