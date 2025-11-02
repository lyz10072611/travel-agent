from config.logger import logger_hook
from typing import Optional
from agno.tools import tool
from models.flight import FlightSearchRequest
from loguru import logger

@tool(
    name="kayak_flight_url_generator",
    show_result=True,
    tool_hooks=[logger_hook]
)
def kayak_flight_url_generator(
    departure: str, destination: str, date: str, return_date: Optional[str] = None, adults: int = 1, children: int = 0, cabin_class: Optional[str] = None, sort: str = "best"
) -> str:
    """
    为指定日期的出发地和目的地之间的航班生成Kayak URL。

    :param departure: 出发机场的IATA代码（例如，索菲亚的'SOF'）
    :param destination: 目的地机场的IATA代码（例如，柏林的'BER'）
    :param date: 航班日期，格式为'YYYY-MM-DD'
    :return_date: 仅用于往返机票。返程航班日期，格式为'YYYY-MM-DD'
    :param adults: 成人数量（默认1）
    :param children: 儿童数量（默认0）
    :param cabin_class: 舱位等级（first, business, premium, economy）
    :param sort: 排序顺序（best, cheapest）
    :return: 航班搜索的Kayak URL
    """
    request = FlightSearchRequest(
        departure=departure,
        destination=destination,
        date=date,
        return_date=return_date,
        adults=adults,
        children=children,
        cabin_class=cabin_class,
        sort=sort)

    logger.info(f"Request: {request}")

    logger.info(f"正在为{date}从{departure}到{destination}生成Kayak URL")
    URL = f"https://www.kayak.com/flights/{departure}-{destination}/{date}"
    if return_date:
        URL += f"/{return_date}"
    if cabin_class and cabin_class.lower() != "economy":
        URL += f"/{cabin_class.lower()}"
    URL += f"/{adults}adults"
    if children > 0:
        URL += f"/children"
        for _ in range(children):
            URL += "-11"


    URL += "?currency=USD"
    if sort.lower() == "cheapest":
        URL += "&sort=price_a"
    elif sort.lower() == "best":
        URL += "&sort=bestflight_a"
    logger.info(f"URL: {URL}")
    return URL
