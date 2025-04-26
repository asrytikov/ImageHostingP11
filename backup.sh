#!/bin/bash

BACKUP_DIR=${BACKUP_DIR:='./backups'}
PG_USER=${PG_USER:='app_user'}
DB_NAME=${DB_NAME:='image_db'}
NOW=$(date '+%Y_%m-%d_%H%M%S')
FILE_NAME=backup_$NOW.sql

mkdir -p "$BACKUP_DIR"

echo "Creating backup..."
docker exec -t db pg_dump -U  "$PG_USER" $DB_NAME > "$BACKUP_DIR/$FILE_NAME" && echo "Backup $FILE_NAME created" || echo "Backup $FILE_NAME failed"


