from datetime import date, timedelta

def date_range(start_date_str: str, end_date_str: str) -> list[str]:
    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)

    date_str_list = [start_date_str]

    if start_date <= end_date:
        current_date = start_date + timedelta(days=1)
        while current_date <= end_date:
            date_str_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
    else:
        current_date = start_date - timedelta(days=1)
        while current_date >= end_date:
            date_str_list.append(current_date.strftime("%Y-%m-%d"))
            current_date -= timedelta(days=1)

    return date_str_list
