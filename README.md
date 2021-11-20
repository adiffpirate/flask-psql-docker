Simple deploy of an application with database via docker-compose.

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

Application: http://localhost:8080
PQAdmin:     http://localhost:7777
PostgresQL:  localhost:5432
