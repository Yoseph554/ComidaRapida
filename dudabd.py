import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('/Users/yosephflores/Desktop/Empresas/SuperPollos/menu.db')
c = conn.cursor()

# Consultar datos de la tabla
c.execute('SELECT * FROM menu')
rows = c.fetchall()

# Mostrar los datos
for row in rows:
    print(row)

# Cerrar conexión
conn.close()