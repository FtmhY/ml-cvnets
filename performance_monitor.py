import threading
import time
import psutil
import csv
from datetime import datetime
from pathlib import Path
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo, nvmlShutdown

class PerformanceMonitor:
    def __init__(self, interval=15, log_dir="/home/ubuntu/ml-cvnets/results/PerformanceLogs/"):
        self.interval = interval
        self.running = False
        self.metrics = []
        self.epoch = None  # Stores the current epoch
        self.iteration = None  # Stores the current iteration

        # Generate log file name based on the current date
        date_str = datetime.now().strftime("%Y%m%d")
        self.log_file = Path(log_dir) / f"perf_monitor_log_{date_str}.csv"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the CSV file with headers
        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "epoch",
                "iteration",
                "cpu_percent",
                "memory_percent",
                "gpu_utilization",
                "gpu_memory_used_MB",
                "disk_read_MB",
                "disk_write_MB",
                "net_sent_MB",
                "net_recv_MB"
            ])

    def update_training_info(self, epoch, iteration):
        """
        Update the current epoch and iteration for logging.
        """
        self.epoch = epoch
        self.iteration = iteration

    def collect_metrics(self):
        # Initialize NVML for GPU monitoring
        nvmlInit()
        gpu_handle = nvmlDeviceGetHandleByIndex(0)

        while self.running:
            # CPU and memory stats
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()

            # GPU utilization and memory
            utilization = nvmlDeviceGetUtilizationRates(gpu_handle)
            gpu_memory = nvmlDeviceGetMemoryInfo(gpu_handle)

            # Disk I/O
            disk_io = psutil.disk_io_counters()

            # Network I/O
            net_io = psutil.net_io_counters()

            # Collect metrics
            metric = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "epoch": self.epoch if self.epoch is not None else "N/A",
                "iteration": self.iteration if self.iteration is not None else "N/A",
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "gpu_utilization": utilization.gpu,
                "gpu_memory_used_MB": gpu_memory.used / 1024**2,
                "disk_read_MB": disk_io.read_bytes / 1024**2,
                "disk_write_MB": disk_io.write_bytes / 1024**2,
                "net_sent_MB": net_io.bytes_sent / 1024**2,
                "net_recv_MB": net_io.bytes_recv / 1024**2,
            }
            self.metrics.append(metric)

            # Write metrics to the CSV file
            with open(self.log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(metric.values())

            # Wait for the specified interval before collecting metrics again
            time.sleep(self.interval)

        nvmlShutdown()

    def start(self):
        """
        Start the performance monitoring thread.
        """
        self.running = True
        self.thread = threading.Thread(target=self.collect_metrics)
        self.thread.start()

    def stop(self):
        """
        Stop the performance monitoring thread.
        """
        self.running = False
        self.thread.join()

    def get_metrics(self):
        """
        Retrieve the collected metrics.
        """
        return self.metrics


