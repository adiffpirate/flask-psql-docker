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
