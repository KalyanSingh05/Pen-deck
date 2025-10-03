# Pen-Deck Makefile

.PHONY: install test clean backup restore setup-permissions start stop status logs

# Installation
install:
	@echo "Installing Pen-Deck..."
	./install.sh

# Testing
test:
	@echo "Running unit tests..."
	python3 tests/run_tests.py

# Clean up
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf temp/*
	rm -f *.log

# Backup configuration and results
backup:
	@echo "Creating backup..."
	./scripts/backup_config.sh

# Restore from backup
restore:
	@echo "Available backups:"
	@ls -la /home/pi/pen-deck-backups/pen-deck-backup-*.tar.gz 2>/dev/null || echo "No backups found"
	@echo "Usage: make restore BACKUP=<backup-file>"
ifdef BACKUP
	./scripts/restore_config.sh $(BACKUP)
endif

# Setup permissions
setup-permissions:
	@echo "Setting up permissions..."
	./scripts/setup_permissions.sh

# Service management
start:
	sudo systemctl start pen-deck.service

stop:
	sudo systemctl stop pen-deck.service

restart:
	sudo systemctl restart pen-deck.service

status:
	sudo systemctl status pen-deck.service

enable:
	sudo systemctl enable pen-deck.service

disable:
	sudo systemctl disable pen-deck.service

# View logs
logs:
	sudo journalctl -u pen-deck.service -f

logs-app:
	tail -f logs/pen-deck.log

logs-errors:
	tail -f logs/pen-deck-errors.log

# Development
dev:
	@echo "Starting Pen-Deck in development mode..."
	source pen-deck-env/bin/activate && python main.py

# Update system
update:
	sudo apt update && sudo apt upgrade -y
	source pen-deck-env/bin/activate && pip install --upgrade -r requirements.txt

# Check system health
health:
	@echo "=== System Health Check ==="
	@echo "Service Status:"
	@sudo systemctl is-active pen-deck.service || echo "Service not running"
	@echo ""
	@echo "Disk Usage:"
	@df -h /
	@echo ""
	@echo "Memory Usage:"
	@free -h
	@echo ""
	@echo "Temperature:"
	@vcgencmd measure_temp 2>/dev/null || echo "Temperature monitoring not available"
	@echo ""
	@echo "Network Status:"
	@ip addr show wlan0 | grep "inet " || echo "WiFi not connected"

# Help
help:
	@echo "Pen-Deck Makefile Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install           - Install Pen-Deck and dependencies"
	@echo "  setup-permissions - Setup tool permissions"
	@echo ""
	@echo "Service Management:"
	@echo "  start            - Start Pen-Deck service"
	@echo "  stop             - Stop Pen-Deck service"
	@echo "  restart          - Restart Pen-Deck service"
	@echo "  status           - Show service status"
	@echo "  enable           - Enable auto-start on boot"
	@echo "  disable          - Disable auto-start on boot"
	@echo ""
	@echo "Development:"
	@echo "  dev              - Run in development mode"
	@echo "  test             - Run unit tests"
	@echo "  clean            - Clean temporary files"
	@echo ""
	@echo "Maintenance:"
	@echo "  backup           - Create configuration backup"
	@echo "  restore          - Restore from backup"
	@echo "  update           - Update system and dependencies"
	@echo "  health           - Check system health"
	@echo ""
	@echo "Monitoring:"
	@echo "  logs             - View service logs (live)"
	@echo "  logs-app         - View application logs (live)"
	@echo "  logs-errors      - View error logs (live)"