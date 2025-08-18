from datetime import date, timedelta

def date_range(start_date_str: str, end_date_str: str) -> list[str]:
    """ Generates a list of dates (as strings in YYYY-MM-DD format) within a given range.
        
    Args:
        start_date_str: The start date of the range, as a string in ISO format (YYYY-MM-DD).
        end_date_str: The end date of the range, as a string in ISO format (YYYY-MM-DD).

    Returns:
        A list of strings, where each string represents a date in YYYY-MM-DD format within the inclusive range from start_date_str to end_date_str.
        If start_date_str is later than end_date_str, the list will be in descending order.
    """
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
