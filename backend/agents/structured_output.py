from typing import TypeVar, Type, Any
from pydantic import BaseModel
from agno.agent import Agent
from loguru import logger
from config.llm import model
import json
import re
from pydantic import ValidationError

T = TypeVar("T", bound=BaseModel)


def clean_json_string(json_str: str) -> str:
    """
    通过移除markdown代码块和任何额外空白来清理JSON字符串。

    参数:
        json_str (str): 要清理的JSON字符串

    返回:
        str: 清理后的JSON字符串
    """
    # 移除markdown代码块
    json_str = re.sub(r"```(?:json)?\n?(.*?)```", r"\1", json_str, flags=re.DOTALL)

    # 如果没有找到代码块，使用原始字符串
    if not json_str.strip():
        json_str = json_str

    # 移除任何前导/尾随空白
    json_str = json_str.strip()

    return json_str


async def convert_to_model(input_text: str, target_model: Type[T]) -> str:
    """
    使用Agno代理将输入文本转换为指定的Pydantic模型。

    参数:
        input_text (str): 要转换的输入文本
        target_model (Type[T]): 目标Pydantic模型类

    返回:
        str: 匹配模型模式的JSON字符串
    """

    logger.info(
        f"将输入文本转换为模型: {target_model.__name__} : {input_text}"
    )

    structured_output_agent = Agent(
        model=model,
        description=(
            "您是专家，擅长从非结构化、自由形式的用户输入中提取结构化旅行规划信息。"
            "给定详细的用户消息、旅行描述或对话，您的目标是准确填充预定义的旅行模式。"
        ),
        instructions=[
            "您的任务是将输入文本转换为与模型模式完全匹配的有效JSON。",
            "您必须仅返回与模式完全匹配的JSON对象 - 没有其他输出。",
            "格式化文本字段时，您必须：",
            "- 在整个过程中使用最小、一致的格式",
            "- 应用适当的列表格式",
            "- 一致地格式化日期、时间和结构化数据",
            "- 简洁清晰地构建文本",
        ],
        markdown=True,
        expected_output="""
            与提供的模式匹配的有效JSON对象。
            文本字段应该干净且格式一致。
            不要包含任何解释或附加文本 - 仅返回JSON对象。
            不使用```json或```
        """,
    )

    schema = target_model.model_json_schema()
    schema_str = json.dumps(schema, indent=2)

    # 使用模型模式和清晰指令创建提示
    prompt = f"""
    您的任务是将输入文本转换为与提供的模式完全匹配的有效JSON对象。
    不要包含任何解释或附加文本 - 仅返回JSON对象。

    模型模式:
    {schema_str}

    规则:
    - 输出必须是有效的JSON
    - 必须包含所有必填字段
    - 字段类型必须与模式完全匹配
    - 不允许额外字段
    - 验证所有约束（最小/最大值、正则表达式模式等）

    文本格式要求:
    - 在所有字符串字段中使用一致、干净的文本格式
    - 对于列表项，使用项目符号（•）而不是星号（*）
    - 最小化文本字段中的缩进和空白
    - 谨慎且一致地使用换行符
    - 避免在文本中使用格式字符，如星号（*）
    - 不要在文本内容中包含不必要的前缀或标签
    - 一致地格式化时间、日期、持续时间和价格
    - 确保所有字段都包含适合其用途的数据

    要转换的输入文本:
    {input_text}
    """

    # 从代理获取结构化响应
    try:
        response = await structured_output_agent.arun(prompt)
        json_string = clean_json_string(response.content)
        logger.info(f"结构化输出代理响应: {json_string}")

        # 解析JSON字符串
        try:
            json.loads(json_string)
            return json_string

        except json.JSONDecodeError as json_err:
            logger.error(f"JSON解析错误: {str(json_err)}")
            raise ValueError(f"无效的JSON响应: {str(json_err)}")

    except Exception as e:
        logger.error(f"解析响应到{target_model.__name__}失败: {str(e)}")
        raise ValueError(
            f"解析响应到{target_model.__name__}失败: {str(e)}"
        )
