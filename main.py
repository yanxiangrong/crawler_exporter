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

def run_init_cmds(cmd_list, tag="global"):
    for cmd in cmd_list:
        print(f"[INIT][{tag}] Running: {cmd}", file=sys.stderr)
        try:
            subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            print(f"Init failed [{tag}]: {e}", file=sys.stderr)

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    interval = cfg.get('interval', 300)
    global_init = cfg.get('global_init', [])
    scripts = {}
    script_init_map = {}
    for name, conf in cfg.get('scripts', {}).items():
        scripts[name] = conf['command']
        script_init_map[name] = conf.get('init', [])
    return interval, global_init, scripts, script_init_map

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
    interval, global_init, scripts, script_init_map = load_config()
    # 1. 运行全局初始化
    if global_init:
        run_init_cmds(global_init, tag="global")
    # 2. 逐脚本初始化
    for name, init_cmds in script_init_map.items():
        if init_cmds:
            run_init_cmds(init_cmds, tag=name)
    # 3. 启动Prometheus HTTP
    start_http_server(EXPORTER_PORT)
    # 4. 定时执行采集脚本
    threading.Thread(target=run_scripts, args=(interval, scripts), daemon=True).start()
    # 5. 主线程阻塞
    while True:
        time.sleep(3600)

if __name__ == '__main__':
    main()
