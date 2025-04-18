import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from fpdf import FPDF

# Conexión a la base de datos
conn = sqlite3.connect('menu.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT,
    producto TEXT,
    precio REAL
)
''')

# Datos del menú
menu_items = [
    ('Pollo Frito', 'Pollo Entero', 350),
    ('Pollo Frito', 'Medio Pollo', 200),
    ('Pollo Frito', 'Cuarto de Pollo', 50),
    ('Pollo Frito', 'Pollo con Tajadas', 90),
    ('Pollo Frito', 'Sopa de Pollo', 90),
    ('Variedad', 'Pastelitos (sencillo)', 15),
    ('Variedad', 'Pastelitos (con más ingredientes)', 35),
    ('Variedad', 'Baleadas (sencillo)', 10),
    ('Variedad', 'Baleadas (con más ingredientes)', 20),
    ('Variedad', 'Arroz con frijoles', 90),
    ('Bebidas', 'Coca Cola 2L', 50),
    ('Bebidas', 'Coca Cola 1L', 25),
    ('Bebidas', 'Jugo de caja 1L', 35),
    ('Bebidas', 'Coffee', 15)
]

# Insertar datos en la tabla
c.executemany('''
INSERT INTO menu (categoria, producto, precio)
VALUES (?, ?, ?)
''', menu_items)

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

class SuperPollosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Pollos - Sistema de Facturación")

        # Crear widgets
        self.create_widgets()

        # Cargar datos del menú
        self.load_menu()

        # Lista para almacenar los productos seleccionados
        self.selected_items = []

    def create_widgets(self):
        # Etiqueta y entrada para el nombre del cliente
        tk.Label(self.root, text="Nombre del Cliente:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_cliente = tk.Entry(self.root)
        self.entry_cliente.grid(row=0, column=1, padx=10, pady=10)

        # Tabla para mostrar el menú
        columns = ('ID', 'Categoría', 'Producto', 'Precio')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        # Botón para agregar producto a la factura
        tk.Button(self.root, text="Agregar a la Factura", command=self.add_to_invoice).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Botón para eliminar producto de la factura
        tk.Button(self.root, text="Eliminar de la Factura", command=self.remove_from_invoice).grid(row=2, column=2, columnspan=2, padx=10, pady=10)

        # Tabla para mostrar los productos seleccionados
        columns_selected = ('Producto', 'Cantidad', 'Precio Unitario', 'Precio Total')
        self.tree_selected = ttk.Treeview(self.root, columns=columns_selected, show='headings')
        for col in columns_selected:
            self.tree_selected.heading(col, text=col)
            self.tree_selected.column(col, width=100)
        self.tree_selected.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        # Etiqueta para mostrar el total de la factura
        tk.Label(self.root, text="Total:").grid(row=4, column=2, padx=10, pady=10)
        self.label_total = tk.Label(self.root, text="0")
        self.label_total.grid(row=4, column=3, padx=10, pady=10)

        # Botón para generar factura PDF
        tk.Button(self.root, text="Generar Factura PDF", command=self.generate_invoice).grid(row=5, column=0, columnspan=4, padx=10, pady=10)

    def load_menu(self):
        # Conexión a la base de datos
        conn = sqlite3.connect('menu.db')
        c = conn.cursor()

        # Consultar datos del menú
        c.execute('SELECT * FROM menu')
        rows = c.fetchall()

        # Insertar datos en la tabla del menú
        for row in rows:
            self.tree.insert('', 'end', values=row)

        # Cerrar conexión
        conn.close()

    def add_to_invoice(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto del menú.")
            return

        item_values = self.tree.item(selected_item[0], 'values')
        
        producto = item_values[2]
        precio_unitario = float(item_values[3])
        
        cantidad = 1
        
        for item in self.selected_items:
            if item['producto'] == producto:
                item['cantidad'] += 1
                item['precio_total'] += precio_unitario
                break
        else:
            self.selected_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'precio_total': precio_unitario * cantidad
            })

        self.update_selected_items()

    def remove_from_invoice(self):
        selected_item = self.tree_selected.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto de la factura.")
            return

        item_values = self.tree_selected.item(selected_item[0], 'values')
        producto = item_values[0]

        for item in self.selected_items:
            if item['producto'] == producto:
                if item['cantidad'] > 1:
                    item['cantidad'] -= 1
                    item['precio_total'] -= item['precio_unitario']
                else:
                    self.selected_items.remove(item)
                break

        self.update_selected_items()

    def update_selected_items(self):
        for row in self.tree_selected.get_children():
            self.tree_selected.delete(row)

        total_factura = 0

        for item in self.selected_items:
            total_factura += item['precio_total']
            self.tree_selected.insert('', 'end', values=(item['producto'], item['cantidad'], item['precio_unitario'], item['precio_total']))

        self.label_total.config(text=str(total_factura))

    def generate_invoice(self):
        cliente = self.entry_cliente.get()
        
        if not cliente:
            messagebox.showwarning("Advertencia", "Por favor ingrese el nombre del cliente.")
            return

        if not self.selected_items:
            messagebox.showwarning("Advertencia", "No hay productos seleccionados para generar la factura.")
            return

        total_factura = sum(item['precio_total'] for item in self.selected_items)

        pdf = FPDF()
        
        pdf.add_page()
        
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt="Super Pollos - Factura", ln=True, align='C')
        
        pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
        
        pdf.cell(200, 10, txt="", ln=True)  # Línea en blanco
        
        pdf.cell(50, 10, txt="Producto", border=1)
        
        pdf.cell(30, 10, txt="Cantidad", border=1)
        
        pdf.cell(50, 10, txt="Precio Unitario", border=1)
        
        pdf.cell(50, 10, txt="Precio Total", border=1)
        
        pdf.ln()
        
        for item in self.selected_items:
            pdf.cell(50, 10, txt=item['producto'], border=1)
            
            pdf.cell(30, 10, txt=str(item['cantidad']), border=1)
            
            pdf.cell(50, 10, txt=str(item['precio_unitario']), border=1)
            
            pdf.cell(50, 10, txt=str(item['precio_total']), border=1)
            
            pdf.ln()
        
        pdf.cell(200, 10, txt="", ln=True)  # Línea en blanco
        
        pdf.cell(200, 10, txt=f"Total: {total_factura}", ln=True, align='R')
        
        pdf.output("factura.pdf")
        
        messagebox.showinfo("Información", "Factura generada exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperPollosApp(root)
    root.mainloop()