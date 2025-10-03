"""
System Information utility for Pen-Deck
Collects hardware, network, and system stats
"""

import psutil
import platform
import subprocess
import logging
from datetime import datetime, timedelta
import socket

class SystemInfo:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_hardware_info(self):
        """Get hardware information"""
        try:
            info = {
                'Platform': platform.system(),
                'Machine': platform.machine(),
                'Processor': platform.processor()[:20],  # Truncate long processor names
                'CPU Cores': psutil.cpu_count(),
                'CPU Usage': f"{psutil.cpu_percent(interval=1)}%",
                'RAM Total': self._format_bytes(psutil.virtual_memory().total),
                'RAM Used': f"{psutil.virtual_memory().percent}%"
            }
            return info
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {e}")
            return {'Error': str(e)}
            
    def get_network_info(self):
        """Get network information"""
        try:
            info = {}
            
            # Get hostname
            info['Hostname'] = socket.gethostname()
            
            # Get network interfaces
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, interface_addresses in addrs.items():
                # Focus on wlan0 and eth0
                if interface_name in ['wlan0', 'eth0', 'lo']:
                    for address in interface_addresses:
                        if address.family == socket.AF_INET:
                            info[f'{interface_name} IP'] = address.address
                            
                            # Check if interface is up
                            if interface_name in stats:
                                status = 'UP' if stats[interface_name].isup else 'DOWN'
                                info[f'{interface_name} Status'] = status
            
            # Get network I/O stats
            net_io = psutil.net_io_counters()
            info['Bytes Sent'] = self._format_bytes(net_io.bytes_sent)
            info['Bytes Recv'] = self._format_bytes(net_io.bytes_recv)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            return {'Error': str(e)}
            
    def get_disk_info(self):
        """Get disk usage information"""
        try:
            info = {}
            
            # Get disk usage for root partition
            disk = psutil.disk_usage('/')
            info['Total'] = self._format_bytes(disk.total)
            info['Used'] = self._format_bytes(disk.used)
            info['Free'] = self._format_bytes(disk.free)
            info['Usage'] = f"{disk.percent}%"
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting disk info: {e}")
            return {'Error': str(e)}
            
    def get_process_info(self, limit=10):
        """Get top processes by CPU usage"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'][:15],  # Truncate long names
                        'cpu': f"{pinfo['cpu_percent']:.1f}%",
                        'mem': f"{pinfo['memory_percent']:.1f}%"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and get top processes
            processes.sort(key=lambda x: float(x['cpu'].strip('%')), reverse=True)
            
            return processes[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return []
            
    def get_temperature(self):
        """Get CPU temperature (Raspberry Pi specific)"""
        try:
            # Try to read from thermal zone (works on most Linux systems)
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return f"{temp:.1f}°C"
        except:
            try:
                # Try vcgencmd (Raspberry Pi specific)
                result = subprocess.run(
                    ['vcgencmd', 'measure_temp'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    temp = result.stdout.strip().replace("temp=", "")
                    return temp
            except:
                pass
        
        return "N/A"
        
    def get_uptime(self):
        """Get system uptime"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m {seconds}s"
                
        except Exception as e:
            self.logger.error(f"Error getting uptime: {e}")
            return "N/A"
            
    def get_wifi_status(self):
        """Get WiFi connection status"""
        try:
            # Get current SSID
            result = subprocess.run(
                ['iwgetid', '-r'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout.strip():
                ssid = result.stdout.strip()
                
                # Get signal strength
                result2 = subprocess.run(
                    ['iwconfig', 'wlan0'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                signal = "N/A"
                if result2.returncode == 0:
                    for line in result2.stdout.split('\n'):
                        if 'Signal level' in line:
                            parts = line.split('Signal level=')
                            if len(parts) > 1:
                                signal = parts[1].split()[0]
                                break
                
                return {
                    'SSID': ssid,
                    'Signal': signal,
                    'Status': 'Connected'
                }
            else:
                return {
                    'Status': 'Disconnected'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting WiFi status: {e}")
            return {'Status': 'Unknown'}
            
    def get_full_status(self):
        """Get comprehensive system status"""
        try:
            status = {
                'Hardware': self.get_hardware_info(),
                'Network': self.get_network_info(),
                'Disk': self.get_disk_info(),
                'WiFi': self.get_wifi_status(),
                'Temperature': self.get_temperature(),
                'Uptime': self.get_uptime()
            }
            return status
        except Exception as e:
            self.logger.error(f"Error getting full status: {e}")
            return {'Error': str(e)}
            
    def _format_bytes(self, bytes_value):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"
        
    def get_battery_status(self):
        """Get battery status if available"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'Percent': f"{battery.percent}%",
                    'Plugged': 'Yes' if battery.power_plugged else 'No',
                    'Time Left': str(timedelta(seconds=battery.secsleft)) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'N/A'
                }
            return None
        except Exception as e:
            return None
