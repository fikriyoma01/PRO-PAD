from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io
from openpyxl import Workbook

env = Environment(loader=FileSystemLoader("app/templates"))

def build_pdf_report(context: dict) -> bytes:
    html = env.get_template("report.html").render(**context)
    pdf = HTML(string=html).write_pdf()
    return pdf

def build_xlsx_report(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["Periode", "Jenis Pajak", "Nilai"])
    for r in rows:
        ws.append([r["periode"], r["jenis_pajak"], float(r["nilai"])])
    bio = io.BytesIO()
    wb.save(bio); bio.seek(0)
    return bio.read()
