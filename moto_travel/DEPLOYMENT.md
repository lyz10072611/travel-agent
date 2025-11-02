# 摩旅智能助手部署指南

## 环境要求

- Python 3.8+
- PostgreSQL 12+ (支持pgvector扩展)
- Redis 6+
- Docker & Docker Compose (可选)

## 快速部署

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd moto_travel

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
vim .env
```

配置以下关键参数：
- `DATABASE_URL`: PostgreSQL数据库连接字符串
- `REDIS_URL`: Redis连接字符串
- `QWEN_API_KEY`: 通义千问API密钥
- `AMAP_API_KEY`: 高德地图API密钥
- `QWEATHER_API_KEY`: 和风天气API密钥

### 3. 数据库初始化

```bash
# 使用Docker启动数据库服务
docker-compose up -d

# 初始化数据库
python scripts/init_db.py

# 运行数据库迁移
python scripts/run_migrations.py
```

### 4. 启动服务

```bash
# 启动API服务
python run.py

# 或使用uvicorn直接启动
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# 测试API
curl http://localhost:8000/docs
```

## Docker部署

### 1. 构建镜像

```bash
# 构建应用镜像
docker build -t moto-travel-agent .

# 启动所有服务
docker-compose up -d
```

### 2. 查看日志

```bash
# 查看应用日志
docker-compose logs -f app

# 查看数据库日志
docker-compose logs -f postgres
```

## 生产环境部署

### 1. 使用Gunicorn

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 使用Systemd服务

创建服务文件 `/etc/systemd/system/moto-travel.service`:

```ini
[Unit]
Description=Moto Travel Agent
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/moto_travel
Environment=PATH=/path/to/moto_travel/venv/bin
ExecStart=/path/to/moto_travel/venv/bin/gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable moto-travel
sudo systemctl start moto-travel
```

## 监控和日志

### 1. 日志配置

应用使用loguru进行日志记录，日志文件位于 `logs/` 目录。

### 2. 健康检查

```bash
# 应用健康检查
curl http://localhost:8000/health

# 数据库健康检查
curl http://localhost:8000/api/v1/health/database
```

### 3. 性能监控

可以使用Prometheus和Grafana进行性能监控：

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'moto-travel'
    static_configs:
      - targets: ['localhost:8000']
```

## 故障排除

### 1. 常见问题

**数据库连接失败**
```bash
# 检查数据库状态
docker-compose ps postgres

# 检查连接
psql -h localhost -U moto_travel -d moto_travel
```

**Redis连接失败**
```bash
# 检查Redis状态
docker-compose ps redis

# 测试连接
redis-cli ping
```

**API密钥配置错误**
```bash
# 检查环境变量
echo $QWEN_API_KEY
echo $AMAP_API_KEY
echo $QWEATHER_API_KEY
```

### 2. 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

### 3. 性能优化

**数据库优化**
- 创建适当的索引
- 定期清理旧数据
- 使用连接池

**缓存优化**
- 配置Redis缓存
- 设置合适的TTL
- 使用缓存预热

**API优化**
- 启用响应压缩
- 使用CDN
- 实现请求限流

## 安全配置

### 1. 环境变量安全

```bash
# 使用强密码
export SECRET_KEY="your-very-secure-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"

# 限制数据库访问
export DATABASE_URL="postgresql://user:password@localhost:5432/moto_travel?sslmode=require"
```

### 2. 网络安全

```bash
# 配置防火墙
sudo ufw allow 8000/tcp
sudo ufw enable

# 使用HTTPS
# 配置SSL证书
```

### 3. 数据安全

- 定期备份数据库
- 加密敏感数据
- 实施访问控制

## 扩展部署

### 1. 水平扩展

```bash
# 使用负载均衡器
# 配置多个应用实例
# 使用Redis集群
```

### 2. 微服务架构

```bash
# 拆分服务
# 使用消息队列
# 实现服务发现
```

## 维护和更新

### 1. 定期维护

```bash
# 更新依赖
pip install -r requirements.txt --upgrade

# 数据库维护
python scripts/maintenance.py

# 清理日志
python scripts/cleanup_logs.py
```

### 2. 版本更新

```bash
# 备份数据
pg_dump moto_travel > backup.sql

# 更新代码
git pull origin main

# 运行迁移
python scripts/run_migrations.py

# 重启服务
sudo systemctl restart moto-travel
```
