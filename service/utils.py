def convert_price_to_kopecks(price_rubles: float) -> int:
    return int(price_rubles*100) 


def convert_time_to_seconds(time_minutes: int) -> int:
    return time_minutes * 60
