#!/bin/sh

# Start MongoDB in the background
docker-entrypoint.sh mongod &

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to start..."
until mongo --eval "print('MongoDB is ready')" > /dev/null 2>&1; do
    sleep 2
done

# Find the latest backup directory
LATEST_BACKUP=$(ls -td /backup/20* 2>/dev/null | head -n 1)

if [ -d "$LATEST_BACKUP/notoday_db" ]; then
    echo "Restoring MongoDB from $LATEST_BACKUP/notoday_db..."
    mongorestore --host localhost --drop --db notoday_db "$LATEST_BACKUP/notoday_db"
    echo "Restore completed!"
elif [ -d "/backup/notoday_db" ]; then
    echo "Restoring MongoDB from /backup/notoday_db..."
    mongorestore --host localhost --drop --db notoday_db "/backup/notoday_db"
    echo "Restore completed!"
else
    echo "No backup found. Skipping restore."
fi

# Keep MongoDB running in foreground
wait