from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class PDFGenerator:
    def generate(self, title, out_path):
        c = canvas.Canvas(out_path, pagesize=A4)
        c.setFont('Helvetica', 14)
        c.drawString(2*cm, 27*cm, title[:80])
        c.setFont('Helvetica', 10)
        c.drawString(2*cm, 26*cm, 'Сгенерировано AO3Time')
        c.save()
        return out_path
