from dateparser import parse

def parse_natural_language_date(date_str):
    try:
        date_obj = parse(date_str)
        if not date_obj:
            return None
        return date_obj
    except:
        return None