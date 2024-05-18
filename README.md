# create-web-app

Scaffholding to create a web application using FastAPI and VueJS.

[video-demonstration.webm](https://github.com/yannmazita/create-web-app/assets/83191036/b148226c-53aa-487c-bf34-32d55edaf0ee)


## Running


<details>
    <summary>Basic commands</summary>

The frontend, the backend and the database live in Docker containers. Utility scripts can be found in the `scripts` directory.

To start the development environment, run from the project root:

```commandline
bash ./scripts/run-dev.sh [--options]
```

To start the production environment, run from the project root:

```commandline
bash ./scripts/run-prod.sh [--options]
```

You can specify Docker options like `--build`.
Services can also be started individually with :

```commandline
docker compose up [--options] <docker-service>
```
</details>

The frontend is served to `localhost:5173` in dev and `localhost:80` in prod.
The backend is served to `localhost:8000` in both environments, currently.


However backend services depend on database services, starting the former will start up the latter.


## Infrastructure

<details>
    <summary>How do the docker services look like?</summary>

Two environments (docker profiles) are currently set up, `dev` and `prod`.

Services are setup following this naming scheme :
- `postgres-[profile]`
- `backend-[profile]`
- `frontend-[profile]`

For example, to build and spin up the frontend service with `dev` profile in detached mode :

```commandline
docker compose up -d --build frontend-dev
```

Attention: when directly spinning up backend services you have to copy `pyproject.toml` and `poetry.lock` to the `app` directory.
</details>


## Features
 - Separate development and production services
 - Seperate development and production networks
 - Quick and easy spin up
 - PostgreSQL database
 - FastAPI backend
 - Asynchronous database interface using `asyncio` and `asyncpg`
 - Administration dashboard
 - Responsive Vue3 frontend
 - Type safety with Typescript and Python type hints.

<details>
    <summary>More detail</summary>

- The database lives in a `Postgresql` container.
- `Python` backend using `FastAPI` and several other utilities like `SQLModel`, `SQLAlchemy` and `Pydantic`. The backend is served using `uvicorn`.
- `Vue3/Typescript` frontend using `vite`. In the development environment the frontend is served using vite, in production `NGINX` is used.
</details>

## To do
- Update README with pictures
- Backend: Enhance OpenAPI documentation
- Backend: Use KeyDB/Valkey/DynamoDB to store websocket connections
- DB: Manage migrations with Alembic
- Frontend: Enhance error/loading handling when accessing backend
