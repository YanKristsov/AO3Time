from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class PDFGenerator:
    def generate(self, title, text, out_path):
        c = canvas.Canvas(out_path, pagesize=A4)
        c.setFont('Helvetica', 12)
        # simple placeholder
        c.drawString(50, 800, title[:60])
        c.save()
        return out_path
