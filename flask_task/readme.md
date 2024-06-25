# Project Name

Flask-API-App

## Prerequisites

- Docker
- Docker Compose

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Airan19/FlaskAssign
    ```

2. Navigate to the project directory:

    ```bash
    cd /FlaskAssign/flask_task
    ```

3. Update the `./env_varables` file in the root directory with the following environment variables:

    ```plaintext
    DB_SERVER=mssql-db
    DB_PORT=1433
    DB_USER=sa
    DB_PASSWORD=YourPassword
    DB_NAME=YourDataBaseName
    DB_MASTER=master
    SA_PASSWORD=YourPassword (same as DB_PASSWORD)
    ```

4. Build and start the Docker containers:

    ```bash
    docker compose up --build
    ```

## Usage

- Access the Flask app at `http://localhost:5000`

## Cleanup

To stop the containers and remove associated resources, use:

```bash
ctrl + c
docker compose down
```
or open a new terminal and navigate to the project directory, then use:

```bash
docker compose down
```
