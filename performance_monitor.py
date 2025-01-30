
import subprocess
import time
import csv
import psutil
from datetime import datetime
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, interval=15, log_dir="/home/ubuntu/ml-cvnets-FtmhY/ml-cvnets/results/PerformanceLogs/"):
        self.interval = interval
        self.running = False
        self.epoch = None
        self.iteration = None

        # Log file paths
        date_str = datetime.now().strftime('%Y%m%d')
        self.gpu_log_file = Path(log_dir) / f"perf_monitor_gpu_{date_str}.csv"
        self.sys_log_file = Path(log_dir) / f"perf_monitor_sys_{date_str}.csv"

        # Ensure the log directory exists
        self.gpu_log_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize GPU log file
        if not self.gpu_log_file.exists():
            with open(self.gpu_log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "epoch", "iteration", "gpu_id", "gpu_utilization", "gpu_memory_used_MB"])

        # Initialize system log file
        if not self.sys_log_file.exists():
            with open(self.sys_log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "epoch", "iteration", "cpu_percent", "memory_percent"])

    def update_training_info(self, epoch, iteration):
        """Update the current epoch and iteration for logging."""
        self.epoch = epoch
        self.iteration = iteration
        print(f"Updated epoch: {self.epoch}, iteration: {self.iteration}")  # Debugging
        
    def collect_metrics(self):
        while self.running:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # GPU Monitoring using nvidia-smi
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used",
                     "--format=csv,noheader,nounits"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                gpu_stats = result.stdout.strip().split("\n")

                with open(self.gpu_log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    for line in gpu_stats:
                        gpu_id, utilization, memory_used = line.split(", ")
                        writer.writerow([
                            timestamp,
                            self.epoch if self.epoch is not None else "N/A",
                            self.iteration if self.iteration is not None else "N/A", 
                            gpu_id, 
                            utilization, 
                            memory_used
                        ])

            except subprocess.CalledProcessError as e:
                print(f"Error running nvidia-smi: {e}")

            # CPU & Memory Monitoring
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()

            with open(self.sys_log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    self.epoch if self.epoch is not None else "N/A",
                    self.iteration if self.iteration is not None else "N/A",
                    cpu_percent,
                    memory_info.percent
                ])

            time.sleep(self.interval)

    def start(self):
        """Start performance monitoring."""
        self.running = True
        self.collect_metrics()  # Run in the same thread for simplicity

    def stop(self):
        """Stop performance monitoring."""
        self.running = False

