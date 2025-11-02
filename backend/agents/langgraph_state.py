"""
LangGraph状态管理
定义旅行规划工作流的状态结构
"""

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class TravelRequest(BaseModel):
    """旅行请求模型"""
    name: str = ""
    destination: str = ""
    starting_location: str = ""
    travel_dates_start: str = ""
    travel_dates_end: str = ""
    date_input_type: str = "picker"
    duration: int = 0
    traveling_with: str = ""
    adults: int = 1
    children: int = 0
    age_groups: List[str] = []
    budget: int = 75000
    budget_currency: str = "CNY"
    travel_style: str = ""
    budget_flexible: bool = False
    vibes: List[str] = []
    priorities: List[str] = []
    interests: str = ""
    rooms: int = 1
    pace: List[int] = [3]
    been_there_before: str = ""
    loved_places: str = ""
    additional_info: str = ""


class AgentResult(BaseModel):
    """代理结果模型"""
    agent_name: str
    content: str
    status: str = "completed"  # completed, failed, pending
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = datetime.now()


class TravelPlanState(TypedDict):
    """旅行规划工作流状态"""
    # 输入数据
    travel_request: TravelRequest
    trip_plan_id: str
    
    # 工作流控制
    current_step: str
    completed_steps: List[str]
    failed_steps: List[str]
    
    # 代理结果
    destination_result: Optional[AgentResult]
    flight_result: Optional[AgentResult]
    hotel_result: Optional[AgentResult]
    dining_result: Optional[AgentResult]
    itinerary_result: Optional[AgentResult]
    budget_result: Optional[AgentResult]
    
    # 最终结果
    final_plan: Optional[str]
    plan_status: str  # processing, completed, failed
    error_message: Optional[str]
    
    # 元数据
    start_time: datetime
    end_time: Optional[datetime]
    total_execution_time: Optional[float]


class WorkflowConfig(BaseModel):
    """工作流配置"""
    max_retries: int = 3
    timeout_seconds: int = 300
    parallel_execution: bool = True
    enable_monitoring: bool = True
    log_level: str = "INFO"
