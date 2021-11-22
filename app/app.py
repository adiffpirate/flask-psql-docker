from flask import Flask
import psycopg2 as psql
import os


# Config access to database
class Config:
    def __init__(self):
        self.config = {
            'postgres' : {
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'database': os.getenv('DB_DATABASE'),
                'host': os.getenv('DB_HOST'),
                'port': os.getenv('DB_PORT')
            }
        }


# Create connection class responsible for handle database operations
class Connection(Config):
    def __init__(self):
        Config.__init__(self)
        try:
            self.conn = psql.connect(**self.config['postgres'])
            self.cur = self.conn.cursor()
        except Exception as e:
            print('Erro na conexão ao database', e)
            exit(1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        return self.cur

    def commit(self):
        self.connection.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


class Populate(Connection):
    def __init__(self):
        Connection.__init__(self)

    def create_table(self, *args):
        try:
            sql = 'CREATE TABLE something (foo VARCHAR(20) NOT NULL)'
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            return f"Erro ao criar tabela\n{e}"
        return "Tabela criada com sucesso"

    def insert(self, *args):
        try:
            sql = 'INSERT INTO something (foo) VALUES (%s)'
            self.execute(sql, args)
            self.commit()
        except Exception as e:
            return f"Erro ao inserir na tabela\n{e}"
        return f"{args} inseridos na tabela com sucesso"


populate = Populate()
app = Flask(__name__)

@app.route('/')
def hello_world():
    return """<h1>Hello</h1>

<form action="/populate/table">
    <input type="submit" value="Create table" />
</form>

<form action="/populate/row">
    <input type="submit" value="Add row to table" />
</form>

<form action="/select">
    <input type="submit" value="List table" />
</form>
"""

@app.route('/populate/table')
def populate_table():
    result = populate.create_table()
    return f"""<h1>{result}</h1>

<form action="/">
    <input type="submit" value="Home" />
</form>
"""

@app.route('/populate/row')
def populate_row():
    result = populate.insert("bar")
    return f"""<h1>{result}</h1>

<form action="/">
    <input type="submit" value="Home" />
</form>
"""

@app.route('/select')
def select():
    result = populate.query("SELECT * FROM something")
    return f"""<h1>{result}</h1>

<form action="/">
    <input type="submit" value="Home" />
</form>
"""
