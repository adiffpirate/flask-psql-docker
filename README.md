Simple docker-compose project that deploys a Flask app with PostgresQL as its database :)

Components:
  - Docker
  - Docker Compose
  - Flask (Python Framework) (back-end/front-end)
  - PostgresQL with PGAdmin (database)

## Deployment

Thanks to docker-compose we only need to run one command :)
```sh
docker-compose up --build -d
```

### Access

- Application: http://localhost:8080
- PQAdmin:     http://localhost:7777
- PostgresQL:  localhost:5432
