from datetime import datetime
import platform
import socket
import psutil

class SystemTool:

    @staticmethod
    def current_time():

        return datetime.now().strftime(
            "%I:%M:%S %p"
        )

    @staticmethod
    def current_date():

        return datetime.now().strftime(
            "%Y-%m-%d"
        )

    @staticmethod
    def hostname():

        return socket.gethostname()

    @staticmethod
    def os_info():

        return platform.platform()

    @staticmethod
    def cpu_usage():

        return psutil.cpu_percent(interval=1)

    @staticmethod
    def ram_usage():

        return psutil.virtual_memory().percent
    
    @staticmethod
    def battery_status():

        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery information unavailable"

        return f"{battery.percent}%"
    
    @staticmethod
    def disk_usage():

        disk = psutil.disk_usage("/")

        return {
            "total_gb": round(
                disk.total / (1024**3),
                2
            ),
            "used_gb": round(
                disk.used / (1024**3),
                2
            ),
            "free_gb": round(
                disk.free / (1024**3),
                2
            ),
            "usage_percent": disk.percent
        }
    
    @staticmethod
    def ip_address():

        hostname = socket.gethostname()

        return socket.gethostbyname(
            hostname
        )