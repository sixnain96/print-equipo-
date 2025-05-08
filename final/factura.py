from fpdf import FPDF
import datetime
import os

def generar_factura_pdf(id_producto, cantidad, total, usuario, nombre_producto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Factura de Venta", ln=True, align="C")
    pdf.cell(200, 10, f"Vendedor: {usuario}", ln=True)
    pdf.cell(200, 10, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, f"Producto: {nombre_producto}", ln=True)
    pdf.cell(200, 10, f"Cantidad Vendida: {cantidad}", ln=True)
    pdf.cell(200, 10, f"Total: ${total:.2f}", ln=True)

    nombre_archivo = f"factura_{usuario}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta_pdf = os.path.join("facturas", nombre_archivo)
    os.makedirs("facturas", exist_ok=True)
    pdf.output(ruta_pdf)

    return ruta_pdf