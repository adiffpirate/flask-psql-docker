import psycopg2 as psql
import csv
import os
import random
import datetime

def main():
    random.seed(22)
    populate = Populate()
    populate.create_tables('queries/create_tables.sql')
    # populate.create_triggers('queries/create_triggers.sql')
    populate.create_partidos('test_data/partidos.csv')
    populate.create_individuos('test_data/individuos.csv')
    populate.create_processos_judiciais()

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

# Connection class responsible for handle database operations
class Connection(Config):
    def __init__(self):
        Config.__init__(self)
        try:
            self.conn = psql.connect(**self.config['postgres'])
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.info('Erro na conexão ao database', e)
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

    def rollback(self):
        self.connection.rollback()

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            affected_rows_count = self.cursor.rowcount
            self.commit()
            return affected_rows_count
        except:
            self.rollback()

    def query(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            content = self.fetchall()
            self.commit()
            return content
        except:
            self.rollback()


class Populate(Connection):
    def __init__(self):
        Connection.__init__(self)


    def create_tables(self, queries_filepath):
        try:
            print("Creating tables")
            queries = open(queries_filepath).read()
            self.execute(queries)
            print("Successfully created tables")
        except Exception as e:
            print(f"Error when creating tables\n{e}")
            exit(1)


    def create_triggers(self, queries_filepath):
        try:
            print("Creating triggers")
            queries = open(queries_filepath).read()
            self.execute(queries)
            print("Successfully created triggers")
        except Exception as e:
            print(f"Error when creating triggers\n{e}")
            exit(1)


    def create_partidos(self, csv_filepath):
        try:
            print("Creating partidos")
            partidos_iterator = csv.reader(open(csv_filepath))
        except Exception as e:
            print(f"Error when reading csv file containing partidos\n{e}")
            exit(1)

        reading_headers = True
        for partido in partidos_iterator:
            try:
                if reading_headers:
                    reading_headers = False
                    continue
                nome = partido[0]
                sigla = partido[1]
                numero = partido[2]
                programa = partido[3]
                sql = 'INSERT INTO partido (nome, sigla, numero, programa) values (%s, %s, %s, %s)'
                self.execute(sql, [nome, sigla, numero, programa])
                print(f"Partido ({nome} | {sigla} | {numero}) created")
            except Exception as e:
                print(f"Error when creating partido\n{e}")


    def create_individuos(self, csv_filepath):
        try:
            print("Creating individuos")
            individuos_iterator = csv.reader(open(csv_filepath))
        except Exception as e:
            print(f"Error when reading csv file containing individuos\n{e}")
            exit(1)

        # Get list of partidos from database
        partidos = self.query("SELECT nome FROM partido")

        reading_headers = True
        for individuo in individuos_iterator:
            try:
                if reading_headers:
                    reading_headers = False
                    continue
                nome = individuo[0]
                tipo = individuo[1]
                # Generate random CPF or CNPJ
                if tipo == 'PF':
                    cpf_cnpj = random.randint(11111111111,99999999999)
                elif tipo == 'PJ':
                    cpf_cnpj = random.randint(11111111111111,99999999999999)
                # Assign a random partido
                partido = random.choice(partidos)
                # Run query
                sql = 'INSERT INTO individuo (nome, tipo, cpf_cnpj, partido) values (%s, %s, %s, %s)'
                self.execute(sql, [nome, tipo, cpf_cnpj, partido])
                print(f"Individuo ({nome} | {tipo} | {cpf_cnpj} | {partido}) created")
            except Exception as e:
                print(f"Error when creating individuo\n{e}")


    def create_processos_judiciais(self):
        # Get list of individuos from database
        individuos = self.query("SELECT nome FROM individuo WHERE tipo = 'PF'")

        processos_amount = random.randint(50, len(individuos))
        for i in range(processos_amount):
            try:
                # Procedente
                procedente = random.choice([True, False])
                # Reu
                reu = random.choice(individuos)
                # Run query
                sql = 'INSERT INTO processojudicial (procedente, reu) values (%s, %s)'
                self.execute(sql, [procedente, reu])
                print(f"Processo Judicial ({procedente} | {reu}) created")
            except Exception as e:
                print(f"Error when creating processojudicial\n{e}")

if __name__ == "__main__":
    main()
