# 项目简介

本项目基于 Python，支持多种脚本的自动化执行和依赖管理，并可通过 Docker 容器化部署。

## 目录结构

- `requirements.txt`：Python 依赖包列表
- `config.yaml`：脚本执行配置
- `.github/workflows/docker-image.yml`：GitHub Actions 自动构建与推送 Docker 镜像

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置说明

* `config.yaml` 中可配置全局初始化命令和各脚本的启动方式及依赖安装命令。

### 3. 运行脚本

根据 `config.yaml` 配置，分别执行对应的初始化命令和脚本启动命令。

### 4. Docker 构建与推送

推送到 `main` 分支或手动触发 GitHub Actions，即可自动构建并推送镜像到 GitHub Container Registry。

## 依赖

* Python 3.x
* PyYAML
* prometheus_client

## 许可证

MIT License
