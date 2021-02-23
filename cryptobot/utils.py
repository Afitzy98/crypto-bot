from datetime import datetime, timedelta


def get_current_ts_dt():
    return datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)


def get_previous_ts_dt():
    return datetime.now().replace(
        microsecond=0, second=0, minute=0, hour=0
    ) - timedelta(days=1)


def get_nearest_hour_dt():
    return datetime.now().replace(microsecond=0, second=0, minute=0)
