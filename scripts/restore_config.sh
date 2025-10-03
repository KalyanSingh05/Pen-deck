#!/bin/bash

# Restore Pen-Deck configuration from backup
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file>"
    echo "Available backups:"
    ls -la /home/pi/pen-deck-backups/pen-deck-backup-*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring Pen-Deck from backup: $BACKUP_FILE"

# Stop Pen-Deck service if running
sudo systemctl stop pen-deck.service 2>/dev/null

# Create backup of current config
if [ -f "/home/pi/pen-deck/config.json" ]; then
    cp /home/pi/pen-deck/config.json /home/pi/pen-deck/config.json.pre-restore
fi

# Extract backup
cd /home/pi
tar -xzf "$BACKUP_FILE"

echo "Restore complete!"
echo "Previous config saved as config.json.pre-restore"
echo "Restart Pen-Deck to apply changes."