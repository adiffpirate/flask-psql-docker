from flask import Flask, render_template, request
from .backend import Connector

app = Flask(__name__)
db = Connector()

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/select/all')
def select_all():
    table = request.args.get("table")
    db.execute(f"SELECT * FROM {table} LIMIT 0")
    headers = [desc[0].title() for desc in db.cursor.description]
    rows = db.query(f"SELECT * FROM {table}")
    return render_template('table.html', headers=headers, rows=rows)

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
        headers = ['Nome', 'Cargo', 'Ano']
        rows = db.query(f"SELECT nome,nomecargo,ano FROM cargo RIGHT JOIN individuo ON cargo.candidato=individuo.nome")
    if subject == "fichas-limpas":
        headers = ['Reu', 'Procedente', 'DataTermino']
        rows = db.query(
            "SELECT (Reu, Procedente, DataTermino) FROM ProcessoJudicial "
            "WHERE (Reu = new.Candidato AND Procedente = TRUE AND (date_part('year', DataTermino) - new.Ano) < 5)"
        )
    else:
        headers = []
        rows = []
    return render_template('table.html', headers=headers, rows=rows)
