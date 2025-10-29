def log(message):
    """Simple console logger with timestamp."""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
