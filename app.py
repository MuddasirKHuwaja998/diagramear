from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import os
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Frequenze tonali e ossee aggiornate
freq_tonali = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
freq_ossee = [250, 500, 1000, 2000, 4000]

# Dati paziente
paziente_info = {
    'Nome': '',
    'Cognome': '',
    'CF': '',
    'Telefono': '',
    'Tessera_Sanitaria': '',
    'Data_Esame': datetime.now().strftime("%d/%m/%Y %H:%M")
}

LOGO_PATH = os.path.join(app.root_path, "static", "logo.png")

# Funzione per leggere i dati dal file di testo
def leggi_audiogramma(file_path):
    left_ear = {}
    right_ear = {}
    left_ossea = {}
    right_ossea = {}
    left_mascherata_tonale = {}
    right_mascherata_tonale = {}
    left_mascherata_ossea = {}
    right_mascherata_ossea = {}

    try:
        with open(file_path, 'r') as file:
            current_section = None
            for line in file:
                line = line.strip()
                
                if line.startswith("Nome:"):
                    paziente_info['Nome'] = line.split(":")[1].strip()
                    continue
                elif line.startswith("Cognome:"):
                    paziente_info['Cognome'] = line.split(":")[1].strip()
                    continue
                elif line.startswith("CF:"):
                    paziente_info['CF'] = line.split(":")[1].strip()
                    continue
                elif line.startswith("Telefono:"):
                    paziente_info['Telefono'] = line.split(":")[1].strip()
                    continue
                elif line.startswith("Tessera_Sanitaria:"):
                    paziente_info['Tessera_Sanitaria'] = line.split(":")[1].strip()
                    continue
                elif line.startswith("Data_Esame:"):
                    if line.split(":")[1].strip():
                        paziente_info['Data_Esame'] = line.split(":")[1].strip()
                    continue
                
                if line == "Left":
                    current_section = "Left"
                elif line == "Right":
                    current_section = "Right"
                elif line == "Left_ossea":
                    current_section = "Left_ossea"
                elif line == "Right_ossea":
                    current_section = "Right_ossea"
                elif line == "Left_mascherata_tonale":
                    current_section = "Left_mascherata_tonale"
                elif line == "Right_mascherata_tonale":
                    current_section = "Right_mascherata_tonale"
                elif line == "Left_mascherata_ossea":
                    current_section = "Left_mascherata_ossea"
                elif line == "Right_mascherata_ossea":
                    current_section = "Right_mascherata_ossea"
                elif "=" in line:
                    freq, threshold = line.split("=")
                    freq = int(freq)
                    threshold = int(threshold)
                    if current_section == "Left":
                        left_ear[freq] = threshold
                    elif current_section == "Right":
                        right_ear[freq] = threshold
                    elif current_section == "Left_ossea":
                        left_ossea[freq] = threshold
                    elif current_section == "Right_ossea":
                        right_ossea[freq] = threshold
                    elif current_section == "Left_mascherata_tonale":
                        left_mascherata_tonale[freq] = threshold
                    elif current_section == "Right_mascherata_tonale":
                        right_mascherata_tonale[freq] = threshold
                    elif current_section == "Left_mascherata_ossea":
                        left_mascherata_ossea[freq] = threshold
                    elif current_section == "Right_mascherata_ossea":
                        right_mascherata_ossea[freq] = threshold
    except FileNotFoundError:
        raise FileNotFoundError(f"File non trovato: {file_path}")

    return (
        left_ear, right_ear,
        left_ossea, right_ossea,
        left_mascherata_tonale, right_mascherata_tonale,
        left_mascherata_ossea, right_mascherata_ossea
    )

# Funzione per disegnare la "banana del parlato"
def disegna_banana_del_parlato():
    freqs = np.array([250, 500, 1000, 2000, 3000, 4000, 6000, 8000])
    thresh_top = np.array([12, 20, 23, 22, 17, 14, 11, 9])
    thresh_bottom = np.array([46, 57, 63, 62, 56, 53, 48, 44])
    plt.fill_between(freqs, thresh_top, thresh_bottom, color='gray', alpha=0.3)

# Funzione per disegnare l'audiogramma
def disegna_audiogramma(
    left_ear, right_ear,
    left_ossea, right_ossea,
    left_mascherata_tonale, right_mascherata_tonale,
    left_mascherata_ossea, right_mascherata_ossea,
    output_path="static/audiogramma.png"
):
    plt.figure(figsize=(10, 6))
    disegna_banana_del_parlato()

    left_x, left_y = [], []
    right_x, right_y = [], []
    left_ossea_x, left_ossea_y = [], []
    right_ossea_x, right_ossea_y = [], []

    for freq in freq_tonali:
        if freq in left_ear:
            threshold = left_ear[freq]
            if threshold != 0:
                left_x.append(freq)
                left_y.append(threshold)
                if threshold > 120:
                    plt.plot(freq, 120, 'kv', markersize=8, fillstyle='none')
                elif freq in left_mascherata_tonale and left_mascherata_tonale[freq] == threshold:
                    plt.plot(freq, threshold, 'bs', markersize=8, fillstyle='none')
                else:
                    plt.plot(freq, threshold, 'bx', markersize=8, fillstyle='none')

        if freq in right_ear:
            threshold = right_ear[freq]
            if threshold != 0:
                right_x.append(freq)
                right_y.append(threshold)
                if threshold > 120:
                    plt.plot(freq, 120, 'kv', markersize=8, fillstyle='none')
                elif freq in right_mascherata_tonale and right_mascherata_tonale[freq] == threshold:
                    plt.plot(freq, threshold, 'r^', markersize=8, fillstyle='none')
                else:
                    plt.plot(freq, threshold, 'ro', markersize=8, fillstyle='none')

    if left_x and left_y:
        plt.plot(left_x, left_y, 'b-', linewidth=1.5, marker='', markersize=8)
    if right_x and right_y:
        plt.plot(right_x, right_y, 'r-', linewidth=1.5, marker='', markersize=8)

    for freq in freq_ossee:
        if freq in left_ossea:
            threshold = left_ossea[freq]
            if threshold != 0:
                left_ossea_x.append(freq)
                left_ossea_y.append(threshold)
                if freq in left_mascherata_ossea and left_mascherata_ossea[freq] == threshold:
                    plt.text(freq, threshold, ']', color='b', fontsize=10, ha='center', va='center')
                else:
                    plt.text(freq, threshold, '>', color='b', fontsize=10, ha='center', va='center')

        if freq in right_ossea:
            threshold = right_ossea[freq]
            if threshold != 0:
                right_ossea_x.append(freq)
                right_ossea_y.append(threshold)
                if freq in right_mascherata_ossea and right_mascherata_ossea[freq] == threshold:
                    plt.text(freq, threshold, '[', color='r', fontsize=10, ha='center', va='center')
                else:
                    plt.text(freq, threshold, '<', color='r', fontsize=10, ha='center', va='center')

    if left_ossea_x and left_ossea_y:
        plt.plot(left_ossea_x, left_ossea_y, 'b--', linewidth=1.5, marker='', markersize=8)
    if right_ossea_x and right_ossea_y:
        plt.plot(right_ossea_x, right_ossea_y, 'r--', linewidth=1.5, marker='', markersize=8)

    plt.gca().set_xscale('log')
    plt.gca().set_xticks(freq_tonali)
    plt.gca().set_xticklabels(freq_tonali)
    plt.yticks(np.arange(-10, 130, 10))
    plt.grid(True, which="both", ls="-")
    plt.title(f"Audiogramma - {paziente_info['Nome']} {paziente_info['Cognome']}", pad=20, fontsize=12)
    plt.xlabel("Frequenza (Hz)", fontsize=10)
    plt.ylabel("Soglia (dB HL)", fontsize=10)
    plt.gca().invert_yaxis()
    plt.xlim(100, 10000)
    plt.ylim(120, -10)

    plt.legend(handles=[
        plt.Line2D([0], [0], marker='x', color='b', label='SX Aria', markersize=8, linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='r', label='DX Aria', markersize=8, linestyle='None'),
        plt.Line2D([0], [0], marker='>', color='b', label='SX Ossea', markersize=8, linestyle='None'),
        plt.Line2D([0], [0], marker='<', color='r', label='DX Ossea', markersize=8, linestyle='None'),
        plt.Line2D([0], [0], marker='s', color='b', label='SX Masc.', markersize=8, linestyle='None'),
        plt.Line2D([0], [0], marker='^', color='r', label='DX Masc.', markersize=8, linestyle='None'),
        plt.Line2D([0], [0], marker='v', color='k', label='Non rilev.', markersize=8, linestyle='None')
    ], loc='upper right', bbox_to_anchor=(1.35, 1), fontsize=8)

    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    return output_path

# Function to generate PDF report
def generate_pdf(image_path, paziente_info):
    buffer = os.path.join(app.config['UPLOAD_FOLDER'], 'report.pdf')
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = styles['Title']
    title_style.alignment = 1
    elements.append(Paragraph("Referto Audiometrico", title_style))
    elements.append(Spacer(1, 12))

    # Patient information
    info_table_data = [
        ["Paziente: ", paziente_info['Nome'] + " " + paziente_info['Cognome']],
        ["CF: ", paziente_info['CF']],
        ["Data Esame:", paziente_info['Data_Esame']],
        ["Tel:", paziente_info['Telefono']],
        ["Tessera Sanitaria: ", paziente_info['Tessera_Sanitaria']]
    ]
    info_table = Table(info_table_data, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))

    # Audiogram image
    elements.append(Image(image_path, width=500, height=300))
    elements.append(Spacer(1, 12))

    # Legend
    legend_text = """
    <b>Legenda:</b><br/>
    <b>SX Aria (X blu):</b> Orecchio sinistro via aerea<br/>
    <b>DX Aria (O rosso):</b> Orecchio destro via aerea<br/>
    <b>SX Ossea (&gt; blu):</b> Orecchio sinistro via ossea<br/>
    <b>DX Ossea (&lt; rosso):</b> Orecchio destro via ossea<br/>
    <b>SX Masc. ([] blu):</b> Orecchio sinistro mascherato via aerea<br/>
    <b>DX Masc. (Δ rosso):</b> Orecchio destro mascherato via aerea<br/>
    <b>Non rilev. (v nero):</b> Soglia non rilevabile
    """
    elements.append(Paragraph(legend_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Report note
    report_note = """
    <b>REFERTO:</b> Rilevata una lieve ipoacusia si consiglia di approfondire lo stato del proprio udito con una visita in telemedicina<br/>
    <b>NOTE:</b>
    """
    elements.append(Paragraph(report_note, styles['Normal']))
    elements.append(Spacer(1, 36))

    # Footer
    footer_text = f"Firma del medico: _______________________  {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')} - Sistema di Refertazione Audiometrica"
    elements.append(Paragraph(footer_text, styles['Normal']))

    doc.build(elements)
    return buffer

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        flash('File successfully uploaded')
        
        # Process the uploaded file
        left_ear, right_ear, left_ossea, right_ossea, left_mascherata_tonale, right_mascherata_tonale, left_mascherata_ossea, right_mascherata_ossea = leggi_audiogramma(filepath)
        
        # Draw the audiogram
        img_path = disegna_audiogramma(left_ear, right_ear, left_ossea, right_ossea, left_mascherata_tonale, right_mascherata_tonale, left_mascherata_ossea, right_mascherata_ossea)
        
        # Generate PDF report
        pdf_path = generate_pdf(img_path, paziente_info)
        
        return render_template('result.html', image_path=img_path, pdf_path=pdf_path, paziente_info=paziente_info)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 