from fast_flights import FlightData, Passengers, Result, get_flights
from typing import Literal
from loguru import logger
from agno.tools import tool
from config.logger import logger_hook


@tool(name="get_flights", show_result=True, tool_hooks=[logger_hook])
def get_google_flights(
    departure: str,
    destination: str,
    date: str,
    trip: Literal["one-way", "round-trip"] = "one-way",
    adults: int = 1,
    children: int = 0,
    cabin_class: Literal["first", "business", "premium-economy", "economy"] = "economy",
) -> Result:
    """
    从Google Flights获取航班信息

    :param departure: 出发机场代码
    :param destination: 目的地机场代码
    :param date: 航班日期，格式为'YYYY-MM-DD'
    :param trip: 旅行类型（one-way, round-trip）
    :param adults: 成人数量（默认1）
    :param children: 儿童数量（默认0）
    :param cabin_class: 舱位等级（first, business, premium-economy, economy）
    :return: 航班结果

    """
    logger.info(
        f"Getting flights from Google Flights for {departure} to {destination} on {date}"
    )

    try:
        result: Result = get_flights(
            flight_data=[
                FlightData(date=date, from_airport=departure, to_airport=destination)
            ],
            trip=trip,
            seat=cabin_class,
            passengers=Passengers(
                adults=adults, children=children, infants_in_seat=0, infants_on_lap=0
            ),
            fetch_mode="fallback",
        )
        logger.info(f"Flights found: {result.flights}")

        return result.flights
    except Exception as e:
        logger.error(f"Error getting flights from Google Flights: {e}")
        return []
