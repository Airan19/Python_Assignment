# Redis Task

This project utilizes Redis as a message queue to implement a producer-consumer model. It consists of three containers: producer, consumer, and Redis.

## Overview

- **Producer**: This container writes employee data in JSON format to a Redis key.

- **Consumer**: Monitors a specific Redis key for any updates. Upon detecting a change, it logs the data into a file associated with that Redis key.

- **Redis Container**: Acts as the message queue, storing the employee data.

## Usage

1. Clone the repository and navigate to the project directory.
2. Run `docker compose up --build` to start the containers.
3. Verify that the producer container is successfully writing data to Redis.
4. Check the consumer container to ensure it is logging any changes in the data.
5. Monitor the logs of both producer and consumer containers for any errors or unexpected behavior.
6. Adjust the code as needed for specific requirements or enhancements.

## File Structure

- `producer.py`: Python script for the producer container, responsible for writing employee data to Redis.
- `consumer.py`: Python script for the consumer container, which monitors Redis for data changes and logs them.
- `docker-compose.yml`: Docker Compose file for orchestrating the containers.

## Dependencies

- Docker: Ensure Docker is installed and running on your system.

## Notes

- Make sure to configure Redis to accept external connections if needed.
- Adjust Redis settings or container configurations as necessary for your environment.

For detailed steps on setting up and running the Redis task, refer to the comments within the code files and Docker Compose configuration.
