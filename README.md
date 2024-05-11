# create-web-app

Scaffholding to create a web application using FastAPI and VueJS.

## Running
The frontend, the backend and the database live in Docker containers. Utility scripts can be found in the `scripts` directory.

To start the development environment, run from the project root:

```commandline
bash ./scripts/run-dev.sh [--options]
```

To start the production environment, run from the project root:

```commandline
bash ./scripts/run-prod.sh [--options]
```

The frontend is served to `localhost:5173` in dev and `localhost:80` in prod.
The backend is served to `localhost:8000` in both environments, currently.

You can specify Docker options like `--build`.
Services can also be started individually with :

```commandline
docker compose run -d [--options] [docker-service]
```

However backend services depend on database services, starting the former will start up the latter.

## Details

- The database lives in a `Postgresql` container.
- `Python` backend using `FastAPI` and several other utilities like `SQLModel`, `SQLAlchemy` and `Pydantic`. The backend is served using `uvicorn`.
- `VueJS/Typescript` frontend using `vite`. In the development environment the frontend is served using vite, in production `NGINX` is used.



## To do
- Update README with pictures
- Backend: Enhance OpenAPI documentation
- Backend: Use KeyDB/Valkey/DynamoDB to store websocket connections
- Frontend: Enhance error/loading handling when accessing backend
