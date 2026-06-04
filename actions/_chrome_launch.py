"""_chrome_launch.py — Clean Chrome launcher helper."""
import subprocess
import webbrowser

def chrome_launch(url: str) -> bool:
    """Launch Chrome browser pointing to the specified URL."""
    try:
        # Try to launch standard chrome command
        subprocess.Popen(f'start chrome "{url}"', shell=True)
        return True
    except Exception:
        try:
            # Fallback to default system browser
            webbrowser.open(url)
            return True
        except Exception:
            return False
