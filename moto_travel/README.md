# 摩旅智能助手 (Moto Travel Agent)

一个基于AI的摩托车旅行规划助手，提供智能路线规划、天气预警、POI推荐、预算计算等功能。

## 功能特性

### 🏍️ 核心功能
- **智能路线规划**: 基于高德地图的摩托车专用路线规划
- **天气预警**: 实时天气查询和灾害预警
- **POI服务**: 餐饮、住宿、修车、加油站等本地服务推荐
- **安全信息**: 政策查询、路况信息、野生动物预警
- **景点推荐**: 基于偏好的目的地和景点推荐
- **预算计算**: 智能预算规划和成本估算
- **个性化定制**: 基于用户偏好的个性化行程规划

### 🛠️ 技术架构
- **AI模型**: Qwen-Plus 作为核心推理模型
- **Agent框架**: LangChain + LangGraph 实现多Agent协作
- **数据库**: PostgreSQL + pgvector 实现数据持久化和向量检索
- **缓存**: Redis 实现高性能缓存
- **任务队列**: Celery 处理异步任务

## 项目结构

```
moto_travel/
├── app/                    # 应用主目录
│   ├── agents/            # Agent实现
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   ├── api/               # API接口
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── database/              # 数据库相关
├── tests/                 # 测试文件
├── docs/                  # 文档
└── scripts/               # 脚本文件
```

## 快速开始

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置
复制 `.env.example` 到 `.env` 并配置相关API密钥：

```bash
cp .env.example .env
```

### 3. 数据库初始化
```bash
# 启动PostgreSQL和Redis
docker-compose up -d

# 运行数据库迁移
alembic upgrade head
```

### 4. 启动服务
```bash
# 启动API服务
python -m app.main

# 启动Celery Worker
celery -A app.celery worker --loglevel=info
```

## API文档

启动服务后访问 `http://localhost:8000/docs` 查看完整的API文档。

## 开发指南

### Agent开发
每个Agent都是独立的服务，通过统一的接口进行通信。参考 `app/agents/` 目录下的示例。

### 数据库模型
使用SQLAlchemy定义数据模型，支持PostgreSQL和pgvector扩展。

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agents.py
```

## 许可证

MIT License
