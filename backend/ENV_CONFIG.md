# 环境变量配置说明

## 必需的API密钥配置

### 1. 阿里云DashScope API（用于qwen模型）
```bash
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

**获取方式：**
1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 注册并登录阿里云账号
3. 创建API密钥
4. 将密钥配置到环境变量中

### 2. 百度搜索API（可选，用于网络搜索）
```bash
BAIDU_SEARCH_API_KEY=your_baidu_search_api_key
BAIDU_SEARCH_ID=your_baidu_search_id
```

**获取方式：**
1. 访问 [百度开发者中心](https://developer.baidu.com/)
2. 申请百度搜索API
3. 获取API密钥和搜索ID

### 3. 数据库配置
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/tripcraft_db
```

### 4. 其他API配置
```bash
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
EXA_API_KEY=your_exa_api_key_here
BACKEND_API_URL=http://localhost:8000
LOG_LEVEL=INFO
```

## 配置步骤

1. 复制 `.env.example` 文件为 `.env`
2. 填入您的API密钥
3. 确保数据库连接正常
4. 启动服务

## 注意事项

- DashScope API密钥是必需的，用于调用qwen-plus模型
- 其他API密钥是可选的，如果未配置将使用模拟数据
- 请妥善保管您的API密钥，不要提交到版本控制系统
