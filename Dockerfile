# 使用官方Python镜像作为基础
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到容器中的/app目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 容器启动时运行的命令
CMD ["python", "test.py"]