from pydantic import BaseModel, Field
from typing import List
from models.hotel import HotelResult


class TravelDates(BaseModel):
    start: str = ""
    end: str = ""


class TravelPlanRequest(BaseModel):
    name: str = ""
    destination: str = ""
    starting_location: str = ""
    travel_dates: TravelDates = TravelDates()
    date_input_type: str = "picker"
    duration: int = 0
    traveling_with: str = ""
    adults: int = 1
    children: int = 0
    age_groups: List[str] = []
    budget: int = 75000
    budget_currency: str = "INR"
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


class TravelPlanAgentRequest(BaseModel):
    trip_plan_id: str
    travel_plan: TravelPlanRequest


class TravelPlanResponse(BaseModel):
    success: bool
    message: str
    trip_plan_id: str


class DayByDayPlan(BaseModel):
    day: int = Field(
        default=0, description="行程中的天数，从0开始"
    )
    date: str = Field(
        default="", description="这一天的日期，格式为YYYY-MM-DD"
    )
    morning: str = Field(
        default="", description="上午活动和计划的描述"
    )
    afternoon: str = Field(
        default="", description="下午活动和计划的描述"
    )
    evening: str = Field(
        default="", description="晚上活动和计划的描述"
    )
    notes: str = Field(
        default="",
        description="当天的额外提示、提醒或重要信息",
    )


class Attraction(BaseModel):
    name: str = Field(default="", description="景点名称")
    description: str = Field(
        default="", description="景点的详细描述"
    )


class FlightResult(BaseModel):
    duration: str = Field(default="", description="航班持续时间")
    price: str = Field(
        default="", description="航班价格（当地货币）"
    )
    departure_time: str = Field(default="", description="航班出发时间")
    arrival_time: str = Field(default="", description="航班到达时间")
    airline: str = Field(default="", description="航空公司")
    flight_number: str = Field(default="", description="航班号")
    url: str = Field(default="", description="航班网站或预订URL")
    stops: int = Field(default=0, description="航班中转次数")


class RestaurantResult(BaseModel):
    name: str = Field(default="", description="餐厅名称")
    description: str = Field(default="", description="餐厅描述")
    location: str = Field(default="", description="餐厅位置")
    url: str = Field(
        default="", description="餐厅网站或预订URL"
    )


class TravelPlanTeamResponse(BaseModel):
    day_by_day_plan: List[DayByDayPlan] = Field(
        description="旅行的逐日计划列表"
    )
    hotels: List[HotelResult] = Field(description="旅行的酒店列表")
    attractions: List[Attraction] = Field(
        description="旅行的推荐景点列表"
    )
    flights: List[FlightResult] = Field(description="旅行的航班列表")
    restaurants: List[RestaurantResult] = Field(
        description="旅行的推荐餐厅列表"
    )
    budget_insights: List[str] = Field(
        description="旅行的预算洞察列表"
    )
    tips: List[str] = Field(
        description="旅行的提示或推荐列表"
    )
