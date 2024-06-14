<!-- Run the Redis Container -->
```bash
docker run --name redis-container -d redis
# (Optional expose ports)
docker run --name redis-container -d -p 6379:6379 redis
```

<!-- Access the Redis Container -->
To access the Redis instance from within the container, you can use the docker exec command:

```bash
docker exec -it redis-container redis-cli
``` 
