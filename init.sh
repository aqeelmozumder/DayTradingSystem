#!/bin/bash

docker-compose exec config1 sh -c "mongo --port 27017 < /data/db/init-configserver.js"
docker-compose exec shard1_1 sh -c "mongo --port 27017 < /data/init-shard1.js"
docker-compose exec shard2_1 sh -c "mongo --port 27017 < /data/init-shard2.js"
# docker-compose exec shard3_1 sh -c "mongo --port 27017 < /data/init-shard3.js"
sleep 30

docker-compose exec mongos sh -c "mongo --port 27017 < /data/db/init-router.js"