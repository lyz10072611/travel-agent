FROM python:3.12-slim-bookworm AS builder

# 安装uv
RUN pip install --no-cache-dir uv

# 复制依赖文件
WORKDIR /app
COPY pyproject.toml uv.lock ./

# 将依赖安装到系统Python中
RUN uv pip install --system -e .

# 最终镜像 - 超精简
FROM python:3.12-slim-bookworm

# 安装运行时依赖、Node.js、PNPM、PostgreSQL客户端库和FFmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl \
    libpq-dev postgresql-client ffmpeg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g pnpm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    npm cache clean --force && \
    pip install --no-cache-dir psycopg2-binary gunicorn

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# 复制应用程序代码（仅需要的部分）
WORKDIR /app
COPY app/ app/
COPY agents/ agents/
COPY config/ config/
COPY models/ models/
COPY routers/ routers/
COPY services/ services/
COPY api.py server.py ./

# 创建日志目录并设置适当权限
RUN mkdir -p logs && chmod 777 logs

EXPOSE 8001

# 使用gunicorn和uvicorn工作进程
CMD ["gunicorn", "server:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001", "--timeout", "0", "--keep-alive", "5"]