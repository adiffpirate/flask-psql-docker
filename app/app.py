from flask import Flask, render_template, request
from .db import Connector

app = Flask(__name__)
db = Connector()

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/consulta')
def select_all():
    table = request.args.get("tabela")
    db.execute(f"SELECT * FROM {table} LIMIT 0")
    all_fields = [desc[0] for desc in db.cursor.description]
    fields = request.args.getlist("campo") if 'campo' in request.args else all_fields
    where = request.args.get("condicao")
    order_by = request.args.get("ordenar-por") if 'ordenar-por' in request.args else all_fields[0]
    if where:
        query = f"SELECT {','.join(fields)} FROM {table} WHERE ({where}) ORDER BY {order_by}"
    else:
        query = f"SELECT {','.join(fields)} FROM {table} ORDER BY {order_by}"
    app.logger.info("Consulta: " + query)
    rows = db.query(query)
    app.logger.info(rows)
    return render_template('table.html', table=table, title=table.title(), fields=fields, all_fields=all_fields, rows=rows)

@app.route('/delete/all')
def delete_all():
    table = request.args.get("table")
    deleted_rows_count = db.execute(f"DELETE FROM {table}")
    deleted_all_warning = f"{deleted_rows_count} were deleted from {table}"
    return render_template('homepage.html', deleted_all_warning=deleted_all_warning)

@app.route('/relatorio')
def report():
    subject = request.args.get("assunto")
    if subject == "candidaturas":
        title = "Candidatos Eleitos"
        fields = ['Nome', 'Cargo', 'Ano']
        rows = db.query(open('queries/report_candidaturas.sql').read())
        app.logger.info("Get candidaturas report: " + str(rows))
    elif subject == "fichas-limpas":
        title = "Indivíduos Ficha-Limpa"
        fields = ['Indivíduo', 'Procedente', 'Data Termino']
        rows = db.query(open('queries/report_fichas_limpas.sql').read())
        app.logger.info("Get fichas-limpas report: " + str(rows))
    else:
        headers = []
        rows = []
    return render_template('table.html', title=title, fields=fields, rows=rows)
