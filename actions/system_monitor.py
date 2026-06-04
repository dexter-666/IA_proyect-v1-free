"""system_monitor.py — Clean system hardware metrics fetcher."""
import psutil

def system_monitor(parameters: dict = None, player=None) -> str:
    """Fetch active CPU, RAM, and Battery percentages."""
    try:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        
        battery_msg = "Battery: N/A"
        try:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "plugged in" if battery.power_plugged else "unplugged"
                battery_msg = f"Battery: {battery.percent}% ({plugged})"
        except Exception:
            pass
            
        report = f"CPU: {cpu}% | RAM: {ram}% | {battery_msg}"
        if player:
            player.write_log(f"💻 System Metrics: {report}")
        return report
    except Exception as e:
        return f"Failed to retrieve hardware metrics: {e}"
