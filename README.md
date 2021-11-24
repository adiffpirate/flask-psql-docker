Simple docker-compose project that deploys a Flask app with PostgresQL as its database :)

Components:
  - Docker
  - Docker Compose
  - Flask (Python Framework) (back-end/front-end)
  - PostgresQL with PGAdmin (database)

## Deployment

Requiments:
  - Docker (https://docs.docker.com/engine/install/)
  - Docker Compose (https://docs.docker.com/compose/install/)

Thanks to docker-compose we only need to run one command :)
```sh
docker-compose up --build -d
```

### Access

- Application: http://localhost:8080
- PostgresQL:  localhost:5432

### Dev mode

You can run the project on development mode to enable debug, hot-reloading and deploy a PGAdmin page.

```sh
docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up --build -d
```

The PGAdmin will be availabe at http://localhost:7777

### Init script

There's a python script to initialize the database, you can it as a standalone script.

The only requirement is to configure the following environment variables with your database info:
  - DB_USER
  - DB_PASSWORD
  - DB_DATABASE
  - DB_HOST
  - DB_PORT

After that, simply go to the init directory and run `init.py`
```sh
cd database/init
```
```sh
python3 init.py
```

> All queries runned by the script are printed to stderr

> The first line of the main fuction defines the random seed to use.
> It's hardcoded now so we can have some previsibility, but you can change that.
