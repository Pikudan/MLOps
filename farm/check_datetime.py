from datetime import datetime
def is_valid_datetime(date_string, format='%Y-%m-%d'):
    try:
        input_datetime = datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False
