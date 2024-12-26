import subprocess
import time
from datetime import datetime

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

# Configuration
log_file = f"./results/nvidia-smi/gpu_utilization_log_{current_date}.csv"
interval = 15  # in seconds

# Ensure the directory exists
import os
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Write header to log file
with open(log_file, "w") as f:
    f.write("Timestamp, GPU Utilization (%), GPU Memory Used (MiB), GPU Memory Total (MiB)\n")

print(f"Logging GPU utilization to {log_file} every {interval} seconds. Press Ctrl+C to stop.")

try:
    while True:
        # Get nvidia-smi output
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Error running nvidia-smi. Ensure NVIDIA drivers are installed and the GPU is accessible.")
            break

        # Parse output
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        gpu_info = result.stdout.strip()
        log_entry = f"{timestamp}, {gpu_info}\n"

        # Append to log file
        with open(log_file, "a") as f:
            f.write(log_entry)

        # Wait before the next log
        time.sleep(interval)

except KeyboardInterrupt:
    print("Logging stopped.")

