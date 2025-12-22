# 酒店住宿Agent文档

## 📋 功能概述

酒店住宿Agent提供完整的酒店服务，包括：
- 🔍 多数据源酒店搜索（美团、携程、同程、去哪、飞猪）
- 🎯 智能筛选和推荐（适合摩旅）
- 📱 手机号+验证码登录认证
- 🏨 酒店预订和退订
- 🤖 ReAct模式智能查询

## 🏗️ 架构设计

### Agent结构
```
app/agents/hotel/
├── __init__.py
├── agent.py              # 主Agent类
└── tools/
    ├── __init__.py
    ├── meituan_tool.py   # 美团工具
    ├── ctrip_tool.py     # 携程工具
    ├── tongcheng_tool.py # 同程工具
    ├── qunar_tool.py     # 去哪儿工具
    ├── fliggy_tool.py    # 飞猪工具
    ├── hotel_analyzer.py # 酒店分析器
    └── hotel_filter.py   # 酒店筛选器
```

### 数据源支持
- ✅ 美团（已实现基础功能）
- ⏳ 携程（待实现）
- ⏳ 同程（待实现）
- ⏳ 去哪儿（待实现）
- ⏳ 飞猪（待实现）

## 🔐 用户认证

### 手机号+验证码登录流程

1. **发送验证码**
```http
POST /auth/send_code
{
  "phone": "13800138000"
}
```

2. **登录**
```http
POST /auth/login
{
  "phone": "13800138000",
  "code": "123456"
}
```

3. **获取Token**
登录成功后返回token，后续请求需要携带token。

## 🏨 API接口

### 1. 搜索酒店

```http
POST /hotel/search
{
  "city": "北京",
  "check_in_date": "2024-01-15",
  "check_out_date": "2024-01-17",
  "sources": ["meituan", "ctrip"],  // 可选，默认全选
  "filters": {
    "price_min": 100,
    "price_max": 500,
    "rating_min": 4.0,
    "room_type": "大床"
  },
  "preferences": {
    "budget_max": 500,
    "prefer_parking": true
  },
  "user_token": "xxx"  // 可选
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "hotels": [
      {
        "hotel_id": "123",
        "name": "XX酒店",
        "price": 300,
        "rating": 4.5,
        "parking_available": true,
        "moto_score": 85,
        "suitable_for_moto": true,
        "reasons": ["有停车位", "位置便利", "价格合适"]
      }
    ],
    "total": 50,
    "suitable_count": 35,
    "sources_used": ["meituan", "ctrip"]
  }
}
```

### 2. 获取酒店详情

```http
POST /hotel/details
{
  "hotel_id": "123",
  "source": "meituan",
  "check_in_date": "2024-01-15",
  "check_out_date": "2024-01-17",
  "user_token": "xxx"
}
```

### 3. 预订酒店

```http
POST /hotel/book
{
  "hotel_id": "123",
  "source": "meituan",
  "room_type_id": "456",
  "check_in_date": "2024-01-15",
  "check_out_date": "2024-01-17",
  "guest_name": "张三",
  "guest_phone": "13800138000",
  "num_rooms": 1,
  "user_token": "xxx"  // 必需
}
```

### 4. 取消预订

```http
POST /hotel/cancel
{
  "order_id": "789",
  "source": "meituan",
  "user_token": "xxx"  // 必需
}
```

### 5. ReAct模式查询

```http
POST /hotel/react_query
{
  "query": "我想在北京找一家价格300左右，有停车位的酒店",
  "user_token": "xxx",
  "max_iterations": 5
}
```

**ReAct流程：**
1. **思考（Think）**：分析查询，决定需要什么信息
2. **行动（Act）**：执行搜索或询问用户
3. **观察（Observe）**：获取结果
4. **循环**：基于观察结果继续思考，直到得到答案

**响应示例：**
```json
{
  "success": true,
  "data": {
    "answer": "找到15个符合条件的酒店，其中12个适合摩旅",
    "thoughts": [
      {
        "action": "ask_user",
        "params": {"question": "请问您的预算范围是多少？"},
        "reasoning": "需要了解用户预算"
      },
      {
        "action": "search_hotels",
        "params": {...},
        "reasoning": "搜索符合条件的酒店"
      }
    ],
    "actions": [...],
    "observations": [...]
  }
}
```

## 🏍️ 摩旅特色功能

### 酒店适合度评分

Agent会为每个酒店计算摩旅适合度评分（moto_score），考虑因素：
- ✅ 停车位（+20分）
- ✅ 位置便利性（+15分）
- ✅ 价格合理性（+10分）
- ✅ 评分（+15分）
- ✅ 设施完善度（+5分）

### 筛选条件

支持以下筛选：
- 价格范围
- 评分最低值
- 房型（双床、大床、单人床、青旅、连锁、民宿）
- 距离
- 设施（WiFi、餐厅等）

## 🔧 配置

在`.env`文件中添加：

```bash
# 美团
MEITUAN_API_KEY=your_key
MEITUAN_APP_SECRET=your_secret
MEITUAN_BASE_URL=https://openapi.meituan.com

# 携程
CTRIP_API_KEY=your_key
CTRIP_BASE_URL=https://openapi.ctrip.com

# 同程
TONGCHENG_API_KEY=your_key
TONGCHENG_BASE_URL=https://openapi.ly.com

# 去哪儿
QUNAR_API_KEY=your_key
QUNAR_BASE_URL=https://openapi.qunar.com

# 飞猪
FLIGGY_API_KEY=your_key
FLIGGY_BASE_URL=https://openapi.fliggy.com

# Redis（用于验证码存储）
REDIS_URL=redis://localhost:6379/0
```

## 📝 使用示例

### Python示例

```python
from app.agents.hotel import HotelAgent
from app.services.auth_service import AuthService

# 1. 用户登录
auth_service = AuthService()
login_result = await auth_service.login_with_phone("13800138000", "123456")
token = login_result["data"]["token"]

# 2. 搜索酒店
hotel_agent = HotelAgent()
result = await hotel_agent.send_request(
    to_agent="hotel",
    action="search_hotels",
    payload={
        "city": "北京",
        "check_in_date": "2024-01-15",
        "check_out_date": "2024-01-17",
        "sources": ["meituan", "ctrip"],
        "filters": {
            "price_min": 200,
            "price_max": 500
        },
        "preferences": {
            "budget_max": 500,
            "prefer_parking": True
        },
        "user_token": token
    }
)

# 3. ReAct查询
react_result = await hotel_agent.send_request(
    to_agent="hotel",
    action="react_query",
    payload={
        "query": "我想找一家有停车位，价格300左右的酒店",
        "user_token": token
    }
)
```

## 🚀 后续优化

1. **完善其他数据源API**：实现携程、同程、去哪、飞猪的真实API调用
2. **增强ReAct模式**：使用LLM进行更智能的思考和决策
3. **缓存优化**：缓存搜索结果，减少API调用
4. **推荐算法**：基于用户历史偏好进行个性化推荐
5. **短信服务集成**：集成真实的短信服务发送验证码

---

**版本**: 1.0.0
**最后更新**: 2024-01-01

