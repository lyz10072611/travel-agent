# 项目结构说明

## 📁 目录结构

```
moto_travel/
├── app/                          # 应用主目录
│   ├── agents/                   # Agent模块（新架构）
│   │   ├── base/                 # Agent基础模块
│   │   │   ├── agent.py          # Agent基类
│   │   │   ├── a2a_protocol.py  # A2A协议
│   │   │   └── message.py        # 消息定义
│   │   ├── route_planning/       # 路径规划Agent
│   │   ├── weather/              # 天气查询Agent
│   │   ├── poi/                  # POI查询Agent
│   │   └── hotel/                # 酒店Agent
│   ├── api/                      # API路由
│   │   ├── routes.py             # 路由定义
│   │   ├── main.py               # FastAPI应用
│   │   └── websocket.py          # WebSocket支持
│   ├── models/                   # 数据模型
│   ├── services/                 # 业务服务
│   │   ├── auth_service.py       # 认证服务
│   │   └── user_service.py       # 用户服务
│   ├── templates/                # 模板文件
│   ├── utils/                    # 工具函数
│   ├── config.py                 # 配置管理
│   └── database.py               # 数据库连接
│
├── tools/                        # 通用工具（保留）
│   ├── base_tool.py              # 工具基类（所有Agent工具依赖）
│   ├── cache_tools.py            # 缓存工具
│   ├── data_tools.py             # 数据处理工具
│   ├── memory_tools.py           # 内存管理工具
│   ├── budget_tools.py           # 预算工具（可选）
│   └── search_tools.py           # 搜索工具（可选）
│
├── docs/                         # 文档目录
│   ├── README.md                 # 文档索引
│   ├── ARCHITECTURE_DESIGN.md    # 架构设计
│   ├── REFACTORING_HISTORY.md    # 重构历史
│   └── CLEANUP_HISTORY.md        # 清理历史
│
├── tests/                        # 测试文件
│   ├── test_agents.py            # Agent测试
│   └── test_tools.py             # 工具测试
│
├── examples/                     # 示例代码
│   ├── basic_usage.py            # 基础使用示例
│   ├── enhanced_usage.py          # 增强使用示例
│   └── template_usage.py         # 模板使用示例
│
├── scripts/                      # 脚本文件
│   ├── init_db.py                # 数据库初始化
│   ├── run_migrations.py         # 运行迁移
│   └── test_agents.py            # 测试脚本
│
├── database/                     # 数据库文件
│   └── init.sql                  # 初始化SQL
│
├── alembic/                      # 数据库迁移
│   └── versions/                 # 迁移版本
│
├── README.md                     # 项目说明
├── requirements.txt              # Python依赖
├── docker-compose.yml            # Docker编排
├── Dockerfile                     # Docker镜像
├── env.example                   # 环境变量示例
│
└── 文档文件（根目录）
    ├── UPGRADE_ROADMAP.md        # 升级路线图
    ├── UPGRADE_PRIORITY_MATRIX.md # 优先级矩阵
    ├── HOTEL_AGENT_DOC.md        # 酒店Agent文档
    ├── USAGE_EXAMPLES.md         # 使用示例
    ├── DEPLOYMENT.md             # 部署指南
    └── PROJECT_ISSUES.md         # 项目问题
```

## 🎯 设计原则

### 1. 模块化
- 每个Agent独立目录，包含自己的tools和逻辑
- 通用工具放在`tools/`目录
- Agent专用工具放在`app/agents/{agent_name}/tools/`

### 2. 自包含
- 每个Agent模块包含完整的业务逻辑
- 减少模块间依赖
- 便于独立测试和部署

### 3. A2A协议
- Agent间通过标准A2A协议通信
- 支持请求-响应模式
- 支持异步通信

### 4. 可扩展
- 易于添加新的Agent
- 易于添加新的工具
- 易于集成新的数据源

## 📝 文件说明

### Agent模块
- **base/**: Agent基类和A2A协议实现
- **route_planning/**: 路径规划Agent（高德+百度）
- **weather/**: 天气查询Agent
- **poi/**: POI查询Agent（含禁摩政策检查）
- **hotel/**: 酒店Agent（多数据源+ReAct）

### 通用工具
- **base_tool.py**: 工具基类，所有Agent工具都继承自此类
- **cache_tools.py**: Redis缓存工具
- **data_tools.py**: 数据处理工具（GeoUtils等）
- **memory_tools.py**: 内存管理和向量搜索
- **budget_tools.py**: 预算计算工具（可选）
- **search_tools.py**: 网页搜索工具（可选）

### 已迁移的工具（已删除）
- ~~map_tools.py~~ → `app/agents/route_planning/tools/amap_tool.py`
- ~~weather_tools.py~~ → `app/agents/weather/tools/weather_tool.py`
- ~~poi_tools.py~~ → `app/agents/poi/tools/poi_tool.py`
- ~~hotel_tools.py~~ → `app/agents/hotel/tools/meituan_tool.py` 等

## 🔄 迁移指南

### 从旧工具迁移到新Agent工具

**旧方式**:
```python
from tools.map_tools import AmapTool
tool = AmapTool()
```

**新方式**:
```python
from app.agents.route_planning.tools.amap_tool import AmapTool
tool = AmapTool()
```

或者通过Agent使用:
```python
from app.agents.route_planning import RoutePlanningAgent
agent = RoutePlanningAgent()
result = await agent.execute(...)
```

## ✅ 清理状态

- ✅ 已删除旧架构Agent文件（13个）
- ✅ 已删除已迁移的工具文件（3个）
- ✅ 已合并冗余文档
- ✅ 已更新tools/__init__.py
- ⏳ 待更新测试文件
- ⏳ 待更新示例文件

---

**最后更新**: 2024-01-01

