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
    cd FlaskAssign
    ```

3. Create a `.env` file in the root directory and add the following environment variables:

    ```plaintext
    DB_SERVER=db
    DB_PORT=1433
    DB_USER=sa
    DB_PASSWORD=YourPassword
    DB_NAME=YourDataBase
    ```

4. Build and start the Docker containers:

    ```bash
    docker-compose up --build
    ```

## Usage

- Access the Flask app at `http://localhost:5000`

## Cleanup

To stop the containers and remove associated resources, use:

```bash
docker-compose down
