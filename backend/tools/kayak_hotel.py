from config.logger import logger_hook
from typing import Optional
from agno.tools import tool
from models.hotel import HotelSearchRequest
from loguru import logger

@tool(
    name="kayak_hotel_url_generator",
    show_result=True,
    tool_hooks=[logger_hook]
)
def kayak_hotel_url_generator(
    destination: str, check_in: str, check_out: str, adults: int = 1, children: int = 0, rooms: int = 1, sort: str = "recommended"
) -> str:
    """
    为指定目的地在入住和退房日期之间的酒店生成Kayak URL。

    :param destination: 目的地城市或区域（例如"Berlin"、"City Center, Singapore"、"Red Fort, Delhi"）
    :param check_in: 入住日期，格式为'YYYY-MM-DD'
    :param check_out: 退房日期，格式为'YYYY-MM-DD'
    :param adults: 成人数量（默认1）
    :param children: 儿童数量（默认0）
    :param rooms: 房间数量（默认1）
    :param sort: 排序顺序（recommended, distance, price, rating）
    :return: 酒店搜索的Kayak URL
    """
    request = HotelSearchRequest(
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        rooms=rooms,
        sort=sort)

    logger.info(f"Request: {request}")

    logger.info(f"正在为{check_in}到{check_out}的{destination}生成Kayak URL")
    URL = f"https://www.kayak.com/hotels/{destination}/{check_in}/{check_out}"
    URL += f"/{adults}adults"
    if children > 0:
        URL += f"/{children}children"

    if rooms > 1:
        URL += f"/{rooms}rooms"


    URL += "?currency=USD"
    if sort.lower() == "price":
        URL += "&sort=price_a"
    elif sort.lower() == "rating":
        URL += "&sort=userrating_b"
    elif sort.lower() == "distance":
        URL += "&sort=distance_a"
    logger.info(f"URL: {URL}")
    return URL
