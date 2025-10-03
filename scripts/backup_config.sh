#!/bin/bash

# Backup Pen-Deck configuration and results
BACKUP_DIR="/home/pi/pen-deck-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="pen-deck-backup-${TIMESTAMP}"

echo "Creating Pen-Deck backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup archive
cd /home/pi
tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" \
    pen-deck/config.json \
    pen-deck/results/ \
    pen-deck/logs/ \
    --exclude="pen-deck/pen-deck-env" \
    --exclude="pen-deck/__pycache__" \
    --exclude="pen-deck/src/__pycache__" \
    --exclude="pen-deck/temp"

echo "Backup created: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"

# Keep only last 5 backups
cd "$BACKUP_DIR"
ls -t pen-deck-backup-*.tar.gz | tail -n +6 | xargs -r rm

echo "Backup complete!"