import psutil
import time
from datetime import datetime
import os

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

# Configuration
log_file = f"./results/system_metrics/system_metrics_log_{current_date}.csv"
interval = 15  # in seconds

# Ensure the directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Write header to log file
with open(log_file, "w") as f:
    f.write("Timestamp, CPU Usage (%), Memory Usage (%), Disk Usage (%), Disk Read (Bytes), Disk Write (Bytes), "
            "Network Sent (Bytes), Network Received (Bytes)\n")

print(f"Logging system metrics to {log_file} every {interval} seconds. Press Ctrl+C to stop.")

# Initialize previous network and disk counters
prev_net_io = psutil.net_io_counters()
prev_disk_io = psutil.disk_io_counters()

try:
    while True:
        # Get timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Get metrics
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()

        # Calculate I/O differences
        disk_read = disk_io.read_bytes - prev_disk_io.read_bytes
        disk_write = disk_io.write_bytes - prev_disk_io.write_bytes
        net_sent = net_io.bytes_sent - prev_net_io.bytes_sent
        net_recv = net_io.bytes_recv - prev_net_io.bytes_recv

        # Update previous counters
        prev_disk_io = disk_io
        prev_net_io = net_io

        # Log entry
        log_entry = (f"{timestamp}, {cpu_usage:.2f}, {memory_usage:.2f}, {disk_usage:.2f}, "
                     f"{disk_read}, {disk_write}, {net_sent}, {net_recv}\n")

        # Append to log file
        with open(log_file, "a") as f:
            f.write(log_entry)

        # Wait before next measurement
        time.sleep(interval)

except KeyboardInterrupt:
    print("Logging stopped.")

