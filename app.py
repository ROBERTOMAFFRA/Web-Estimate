from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = "spero-secret"

# Caminho da planilha
PLAN_PATH = os.path.join(os.path.dirname(__file__), "estimate.xlsx")

# Página inicial
@app.route("/")
def index():
    return redirect(url_for("new_estimate"))

# Nova estimativa
@app.route("/estimate", methods=["GET", "POST"])
def new_estimate():
    df = pd.read_excel(PLAN_PATH)
    descriptions = df["Description"].dropna().unique().tolist()

    if request.method == "POST":
        client = request.form.get("client")
        description = request.form.get("description")
        qty = float(request.form.get("qty", 0))
        unit_price = float(request.form.get("unit_price", 0))
        total = qty * unit_price

        # Gera PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        logo_path = os.path.join("static", "logo.png")
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 40, height - 100, width=150, preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 80, "Estimate")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 140, f"Client: {client}")
        c.drawString(50, height - 160, f"Description: {description}")
        c.drawString(50, height - 180, f"Qty: {qty}")
        c.drawString(50, height - 200, f"Unit Price: ${unit_price:,.2f}")
        c.drawString(50, height - 220, f"Total: ${total:,.2f}")

        c.showPage()
        c.save()
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name=f"{client}_estimate.pdf")

    return render_template("estimate.html", descriptions=descriptions)
