import psycopg2 as psql
import csv
import os
import random
import datetime
import time

def main():
    random.seed(22)
    populate = Populate()
    populate.create_tables('queries/create_tables.sql')
    populate.create_triggers('queries/create_triggers.sql')
    populate.create_partidos('test_data/partidos.csv')
    populate.create_individuos('test_data/individuos.csv')
    populate.create_processos_judiciais()
    populate.create_pleitos_and_candidaturas('test_data/referencias.csv')
    populate.create_cargos('test_data/referencias.csv')
    populate.create_equipes_de_apoio()
    populate.create_doacoes()

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


    # https://stackoverflow.com/a/553320
    def str_time_prop(self, start, end, time_format, prop):
        """Get a time at a proportion of a range of two formatted times.

        start and end should be strings specifying times formatted in the
        given format (strftime-style), giving an interval [start, end].
        prop specifies how a proportion of the interval to be taken after
        start.  The returned time will be in the specified format.
        """

        stime = time.mktime(time.strptime(start, time_format))
        etime = time.mktime(time.strptime(end, time_format))

        ptime = stime + prop * (etime - stime)

        return time.strftime(time_format, time.localtime(ptime))

    def random_date(self, start, end, prop):
        return self.str_time_prop(start, end, '%Y-%m-%d', prop)

    def create_processos_judiciais(self):
        # Get list of individuos from database
        individuos = self.query("SELECT nome FROM individuo WHERE tipo = 'PF'")

        for reu in individuos:
            if random.choice([True, False]):
                try:
                    procedente = random.choice([True, False])
                    data_termino = self.random_date("2000-1-1", "2021-11-22", random.random())
                    # Run query
                    sql = 'INSERT INTO processojudicial (procedente, datatermino, reu) values (%s, %s, %s)'
                    self.execute(sql, [procedente, data_termino, reu])
                    print(f"Processo Judicial ({procedente} | {data_termino} | {reu}) created")
                except Exception as e:
                    print(f"Error when creating processojudicial\n{e}")


    def create_pleitos_and_candidaturas(self, csv_filepath):
        try:
            referencias_iterator = csv.reader(open(csv_filepath))
        except Exception as e:
            print(f"Error when reading csv file containing referencias\n{e}")
            exit(1)

        # Parse referencias csv file
        country = list()
        state = list()
        city = list()
        for ref in referencias_iterator:
            name = ref[0]
            category = ref[1]
            if category == 'país':
                country.append(name)
            elif category == 'estado':
                state.append(name)
            elif category == 'cidade':
                city.append(name)

        # Get list of individuos from database
        individuos = self.query("SELECT nome FROM individuo WHERE tipo = 'PF'")

        i = 0
        for candidato in individuos:
            if random.choice([True, False]):
                try:
                    # Create pleito
                    total_de_votos = random.randint(1, 100000000) if random.choice([True, False]) else None
                    pleito = i
                    self.execute(
                        "INSERT INTO pleito (pleitoid, totaldevotos) VALUES (%s, %s)",
                        [pleito, total_de_votos]
                    )
                    print(f"Pleito ({i} | {total_de_votos}) created")
                    # Create candidatura
                    ano = random.randint(2000, 2021)
                    vice_candidato = random.choice(individuos) if random.choice([True, False]) else 'NULL'
                    numero = random.randint(10, 999999)
                    nomecargo = random.choice(['Presidente', 'DepFederal', 'Senador', 'Governador', 'Prefeito'])
                    if nomecargo == 'Presidente':
                        referencia = random.choice(country)
                    elif nomecargo == 'DepFederal':
                        referencia = random.choice(country)
                    elif nomecargo == 'Senador':
                        referencia = random.choice(country)
                    elif nomecargo == 'Governador':
                        referencia = random.choice(state)
                    elif nomecargo == 'Prefeito':
                        referencia = random.choice(city)
                    self.execute(
                        "INSERT INTO candidatura (candidato, ano, vicecandidato, numero, pleito, nomecargo, referencia) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        [candidato, ano, vice_candidato, numero, pleito, nomecargo, referencia]
                    )
                    print(f"Candidatura ({candidato} | {ano} | {vice_candidato} | {numero} | {pleito} | {nomecargo} | {referencia}) created")
                    i = i + 1
                except Exception as e:
                    print(f"Error when creating pleitos and candidaturas\n{e}")


    def create_cargos(self, csv_filepath):
        try:
            referencias_iterator = csv.reader(open(csv_filepath))
        except Exception as e:
            print(f"Error when reading csv file containing referencias\n{e}")
            exit(1)

        # Parse referencias csv file
        country = list()
        state = list()
        city = list()
        for ref in referencias_iterator:
            name = ref[0]
            category = ref[1]
            if category == 'país':
                country.append(name)
            elif category == 'estado':
                state.append(name)
            elif category == 'cidade':
                city.append(name)

        # Get list of individuos from database
        individuos = self.query("SELECT nome FROM individuo WHERE tipo = 'PF'")

        cargos_attempts_amount = len(individuos) * 20
        for i in range(cargos_attempts_amount):
            try:
                candidato = random.choice(individuos)
                ano = random.randint(2000, 2021)
                nomecargo = random.choice(['Presidente', 'DepFederal', 'Senador', 'Governador', 'Prefeito'])
                if nomecargo == 'Presidente':
                    referencia = random.choice(country)
                elif nomecargo == 'DepFederal':
                    referencia = random.choice(country)
                elif nomecargo == 'Senador':
                    referencia = random.choice(country)
                elif nomecargo == 'Governador':
                    referencia = random.choice(state)
                elif nomecargo == 'Prefeito':
                    referencia = random.choice(city)
                self.execute(
                    "INSERT INTO cargo (candidato, ano, nomecargo, referencia) VALUES (%s, %s, %s, %s)",
                    [candidato, ano, nomecargo, referencia]
                )
                print(f"Cargo ({candidato} | {ano} | {nomecargo} | {referencia}) created")
            except Exception as e:
                print(f"Error when creating cargos\n{e}")


    def create_equipes_de_apoio(self):
        # Get list of individuos from database
        individuos = self.query("SELECT nome FROM individuo")
        # Get list of candidatos from database
        candidatos = self.query("SELECT candidato FROM candidatura")

        equipes_attempts_amount = len(individuos) * 5
        for i in range(equipes_attempts_amount):
            try:
                candidato = random.choice(candidatos)
                ano = random.randint(2000, 2021)
                apoiador = random.choice(individuos)
                self.execute(
                    "INSERT INTO equipedeapoio (candidato, ano, apoiador) VALUES (%s, %s, %s)",
                    [candidato, ano, apoiador]
                )
                print(f"Equipe de apoio ({candidato} | {ano} | {apoiador}) created")
            except Exception as e:
                print(f"Error when creating cargos\n{e}")


    def create_doacoes(self):
        # Get list of individuos from database
        individuos = self.query("SELECT nome FROM individuo")
        # Get list of candidatos from database
        candidatos = self.query("SELECT candidato FROM candidatura")

        doacoes_attempts_amount = len(individuos) * 5
        for i in range(doacoes_attempts_amount):
            try:
                candidato = random.choice(candidatos)
                ano = random.randint(2000, 2021)
                apoiador = random.choice(individuos)
                valor = random.randint(10, 1000000)
                self.execute(
                    "INSERT INTO doacao (candidato, ano, apoiador, valor) VALUES (%s, %s, %s, %s)",
                    [candidato, ano, apoiador, valor]
                )
                print(f"Doação ({candidato} | {ano} | {apoiador} | {valor}) created")
            except Exception as e:
                print(f"Error when creating doações\n{e}")


if __name__ == "__main__":
    main()
