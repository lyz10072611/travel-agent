# 摩旅智能助手输出模板

本目录包含了摩旅智能助手的输出模板和提示词模板，为其他应用提供标准化的输出格式。

## 📁 文件结构

```
app/templates/
├── output_templates.py      # 输出模板定义
├── moto_travel_prompt.py    # 摩旅提示词模板
└── README.md               # 本文档
```

## 🎯 主要功能

### 1. 输出模板 (`output_templates.py`)

提供标准化的JSON和Markdown输出格式：

- **数据结构定义**: 使用dataclass定义完整的数据结构
- **JSON模板**: 标准化的JSON输出格式
- **Markdown模板**: 美观的Markdown文档格式
- **格式化器**: 自动格式化输出内容

### 2. 提示词模板 (`moto_travel_prompt.py`)

提供专业的摩旅规划提示词：

- **系统提示词**: 定义Agent的角色和职责
- **专业提示词**: 针对不同功能模块的专门提示
- **完整提示词**: 集成所有功能的完整提示
- **成功标准**: 定义输出质量评估标准

## 🚀 快速开始

### 基本使用

```python
from app.templates.output_templates import OutputFormatter, OutputFormat
from app.templates.moto_travel_prompt import MotoTravelPromptTemplate

# 创建输出格式化器
formatter = OutputFormatter()

# 格式化JSON输出
json_output = formatter.format_output(plan_data, OutputFormat.JSON)

# 格式化Markdown输出
markdown_output = formatter.format_output(plan_data, OutputFormat.MARKDOWN)

# 获取提示词模板
system_prompt = MotoTravelPromptTemplate.get_system_prompt()
complete_prompt = MotoTravelPromptTemplate.get_complete_prompt()
```

### 使用摩旅Agent

```python
from app.agents.moto_travel_agent import MotoTravelAgent

# 创建Agent
agent = MotoTravelAgent()

# 执行规划
result = await agent.execute(
    query="从北京到上海的摩旅规划",
    user_id="user_001",
    output_format="markdown",
    preferences={
        "daily_distance": 400,
        "route_type": "自然风光",
        "budget_range": 5000
    }
)
```

## 📊 输出格式

### JSON格式

```json
{
  "success": true,
  "data": {
    "plan_id": "moto_plan_20240101_120000",
    "user_id": "user_001",
    "title": "从北京到上海的摩旅计划",
    "description": "一次精彩的摩旅体验",
    "created_at": "2024-01-01T12:00:00Z",
    "origin": {
      "name": "北京",
      "address": "北京市朝阳区",
      "coordinates": {"longitude": 116.397, "latitude": 39.909}
    },
    "destination": {
      "name": "上海",
      "address": "上海市黄浦区",
      "coordinates": {"longitude": 121.473, "latitude": 31.230}
    },
    "total_distance_km": 1200.0,
    "total_duration_days": 7,
    "route_type": "自然风光",
    "daily_routes": [...],
    "weather_forecast": [...],
    "restaurants": [...],
    "accommodations": [...],
    "gas_stations": [...],
    "total_budget": 5000.0,
    "daily_budgets": [...],
    "budget_breakdown": {...},
    "safety_recommendations": [...],
    "personalized_recommendations": [...]
  },
  "message": "摩旅规划完成",
  "metadata": {
    "execution_time": 2.5,
    "agent_used": "moto_travel_agent",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Markdown格式

```markdown
# 🏍️ 摩旅智能规划报告

## 📋 执行摘要

### 🎯 旅行目的与愿景
- **主要目标**: 安全、愉快的摩托车旅行体验
- **期望体验**: 探索自然风光，体验当地文化
- **特殊需求**: 无
- **关键偏好**: 自然风光路线，休闲骑行

### 🛣️ 路线概览
- **出发地**: 北京
- **目的地**: 上海
- **总距离**: 1200.0 公里
- **预计天数**: 7 天
- **路线类型**: 自然风光
- **整体风格**: 休闲
- **总预算**: ¥5000

## 🗺️ 详细路线规划

### 每日详细行程

#### 第1天 - 2024-07-01

##### 🚀 路线信息
- **起点**: 北京
- **终点**: 天津
- **距离**: 120.0 公里
- **预计时长**: 2.5 小时

##### 🛑 推荐停靠点
- **加油站**: 途中加油站 (距离: 60km)

##### 🏨 住宿推荐
天津摩旅酒店

## 🌤️ 天气与安全分析

### 天气预报

#### 2024-07-01 - 北京
- **温度**: 25.0°C
- **天气**: 晴天
- **风力**: 10.0km/h 东南风
- **能见度**: 15.0km
- **安全评分**: 85/100 (良好)
- **建议**: 天气条件良好，适合骑行

## 💰 预算分析

### 总预算概览
- **总预算**: ¥5000
- **日均预算**: ¥714.29
- **每公里成本**: ¥4.17

### 详细预算分解
- **燃油费**: ¥800
- **住宿费**: ¥1400
- **餐饮费**: ¥1200
- **其他费用**: ¥1600

---

*本报告由摩旅智能助手生成，祝您旅途愉快！* 🏍️✨
```

## 🎨 提示词模板

### 系统提示词

定义了Agent的核心角色和职责：

- 摩旅规划专家身份
- 专业领域覆盖
- 核心职责定义
- 输出要求规范
- 质量标准设定

### 专业提示词

针对不同功能模块的专门提示：

- **路线规划提示**: 路线分析要点、分段原则、安全考虑
- **天气安全提示**: 天气因素分析、安全建议输出
- **POI推荐提示**: 推荐原则、输出格式要求
- **预算计算提示**: 成本构成分析、输出格式要求
- **个性化提示**: 用户偏好分析、个性化建议输出

### 完整提示词

集成所有功能的完整提示，包含：

- 系统角色定义
- 专业功能提示
- 输出格式要求
- 质量标准
- 成功标准

## 🔧 自定义扩展

### 添加新的输出格式

```python
# 在 OutputFormat 枚举中添加新格式
class OutputFormat(Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"  # 新增格式

# 在 OutputFormatter 中添加格式化方法
def format_html_output(self, data: MotoTravelPlan) -> str:
    # 实现HTML格式化逻辑
    pass
```

### 添加新的数据结构

```python
# 在 output_templates.py 中添加新的数据类
@dataclass
class NewDataStructure:
    field1: str
    field2: int
    field3: List[str]

# 在 MotoTravelPlan 中添加新字段
new_field: List[NewDataStructure] = field(default_factory=list)
```

### 自定义提示词

```python
# 在 moto_travel_prompt.py 中添加新的提示词方法
@staticmethod
def get_custom_prompt() -> str:
    return """
    自定义提示词内容...
    """
```

## 📝 使用示例

查看 `examples/template_usage.py` 文件获取完整的使用示例，包括：

- JSON输出示例
- Markdown输出示例
- Agent使用示例
- 提示词模板示例

## 🤝 贡献指南

1. 遵循现有的代码风格和结构
2. 添加适当的类型注解和文档字符串
3. 更新相关的测试和示例
4. 确保新功能与现有模板兼容

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。
