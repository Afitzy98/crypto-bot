from datetime import datetime, timedelta


def get_current_ts_dt():
    now = datetime.now()
    hr = now.hour - (now.hour % 4)
    return now.replace(microsecond=0, second=0, minute=0, hour=hr)


def get_previous_ts_dt():
    now = datetime.now()
    hr = now.hour - (now.hour % 4)
    return datetime.now().replace(
        microsecond=0, second=0, minute=0, hour=hr
    ) - timedelta(hours=4)


def get_nearest_hour_dt():
    return datetime.now().replace(microsecond=0, second=0, minute=0)
