FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制代码和依赖文件
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口（如9115）
EXPOSE 9115

# 启动脚本
CMD ["python", "exporter.py"]
