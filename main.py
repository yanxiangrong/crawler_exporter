import subprocess
import sys
import threading
import time

import yaml
from prometheus_client import start_http_server, Gauge

CONFIG_PATH = 'config.yaml'
EXPORTER_PORT = 9115

# 存放已注册的 Gauge
gauges = {}
lock = threading.Lock()

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    interval = cfg.get('interval', 300)
    scripts = {}
    for name, conf in cfg.get('scripts', {}).items():
        scripts[name] = conf['command']
    return interval, scripts

def run_scripts(interval, scripts):
    while True:
        start_time = time.time()
        for name, cmd in scripts.items():
            try:
                result = subprocess.check_output(cmd, encoding='utf-8')
                for line in result.strip().split('\n'):
                    key_value = line.strip().split()
                    if len(key_value) == 2:
                        metric, value = key_value
                        with lock:
                            if metric not in gauges:
                                gauges[metric] = Gauge(metric, f'{metric} collected by scripts', ['source'])
                            gauges[metric].labels(source=name).set(float(value))
            except Exception as e:
                print(f"Error running {cmd}: {e}", file=sys.stderr)
        elapsed = time.time() - start_time
        sleep_time = interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

def main():
    interval, scripts = load_config()
    # 先启动Prometheus HTTP
    start_http_server(EXPORTER_PORT)
    # 后台定时采集
    threading.Thread(target=run_scripts, args=(interval, scripts), daemon=True).start()
    # 主线程阻塞，保证进程不退出
    while True:
        time.sleep(3600)

if __name__ == '__main__':
    main()
