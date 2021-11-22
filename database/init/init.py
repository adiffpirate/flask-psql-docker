import psycopg2 as psql
import os

def main():
    populate = Populate()
    populate.create_tables()

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

    def create_tables(self):
        try:
            print("Creating tables")
            queries = open("queries/create_tables.sql").read()
            self.execute(queries)
            self.commit()
        except Exception as e:
            print(f"Error when creating tables\n{e}")
        print("Successfully created tables")

    def create_partidos(self, csv_filepath):
        try:
            print("Creating partidos")
            partidos_csv = open("queries/create_tables.sql").read()
            self.execute(queries)
            self.commit()
        except Exception as e:
            print(f"Error when creating tables\n{e}")
        print("Successfully created tables")


if __name__ == "__main__":
    main()
