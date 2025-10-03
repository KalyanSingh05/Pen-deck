# Pen-Deck API Reference

## Web UI API Endpoints

### Configuration Management

#### GET /api/config
Get current configuration
```json
{
  "wifi_networks": [...],
  "ai_assistant": {...},
  "tools": {...},
  "display": {...},
  "system": {...}
}
```

#### POST /api/config
Update configuration
```json
{
  "wifi_networks": [
    {
      "ssid": "NetworkName",
      "password": "password",
      "priority": 1
    }
  ],
  "ai_assistant": {
    "api_key": "your-api-key",
    "model": "gpt-3.5-turbo",
    "max_tokens": 500
  }
}
```

### WiFi Management

#### GET /api/wifi/scan
Scan for available networks
```json
[
  {
    "ssid": "NetworkName",
    "signal": -45,
    "encrypted": true
  }
]
```

#### POST /api/wifi/connect
Connect to network
```json
{
  "ssid": "NetworkName",
  "password": "password"
}
```

### Tool Management

#### GET /api/tools
Get available tools and commands
```json
{
  "nmap": {
    "quick_scan": "nmap -T4 -F {target}",
    "aggressive_scan": "nmap -A -T4 {target}"
  }
}
```

#### POST /api/tools
Update tool commands
```json
{
  "nmap": {
    "custom_scan": "nmap -sS -O {target}"
  }
}
```

### Results Management

#### GET /api/results
Get recent results
```json
[
  {
    "filename": "nmap_192.168.1.1_20231201_143022.txt",
    "size": 2048,
    "modified": 1701434622
  }
]
```

#### GET /api/results/{filename}
Get result content
```json
{
  "content": "Tool execution results..."
}
```

### System Information

#### GET /api/system/info
Get system information
```json
{
  "platform": "Linux-5.15.0-rpi",
  "cpu_percent": 15.2,
  "memory": {
    "total": 536870912,
    "available": 402653184
  },
  "disk": {
    "total": 31914983424,
    "free": 25431654400
  }
}
```

#### POST /api/system/shutdown
Shutdown system
```json
{
  "success": true,
  "message": "Shutting down in 2 seconds"
}
```

## Python API Classes

### ConfigManager
```python
from src.config_manager import ConfigManager

config = ConfigManager()
config.get('ai_assistant.api_key')
config.set('ai_assistant.model', 'gpt-4')
config.add_wifi_network('SSID', 'password')
```

### ToolManager
```python
from src.tools.tool_manager import ToolManager

tools = ToolManager(config_manager)
result = tools.run_tool_command('nmap', 'quick_scan', '192.168.1.1')
recent = tools.get_recent_results()
```

### NetworkManager
```python
from src.network_manager import NetworkManager

network = NetworkManager(config_manager)
networks = network.scan_networks()
status = network.get_status()
network.connect_to_network('SSID', 'password')
```

### AIAssistant
```python
from src.ai_assistant import AIAssistant

ai = AIAssistant(config_manager)
response = ai.get_response('How do I use nmap?')
help_text = ai.get_tool_help('nmap')
```

### DisplayManager
```python
from src.display_manager import DisplayManager

display = DisplayManager()
display.initialize()
display.show_menu('Title', ['Item 1', 'Item 2'], 0)
display.show_text_screen('Results', content)
```

## Error Handling

All API endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include details:
```json
{
  "success": false,
  "error": "Error description"
}
```

## Authentication

Currently, the API does not require authentication as it's designed for local network use. For production deployments, consider adding:
- API key authentication
- IP address restrictions
- HTTPS encryption