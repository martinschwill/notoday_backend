#!/bin/sh

# Find the latest backup directory
LATEST_BACKUP=$(ls -td /backup/* | head -n 1)

if [ -d "$LATEST_BACKUP" ]; then
    echo "Restoring MongoDB from $LATEST_BACKUP..."
    mongorestore --host localhost --drop "$LATEST_BACKUP"
else
    echo "No backup found in /backup. Skipping restore."
fi

# Start MongoDB
exec docker-entrypoint.sh mongod