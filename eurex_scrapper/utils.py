"""
All the utility code goes here
"""
from os import name
from typing import Dict, Any
import yaml
from datetime import datetime

def read_config() -> Dict[Any,Any]:
    
    with open('eurex_scrapper/config.yaml') as config:
        conf_dict = yaml.safe_load(config)
    
    return conf_dict

def lower_bound_date_check(date_string:str) -> bool:
    """
    This method checks if the date string is today or not
    """
    conf = read_config()
    cutoff = datetime.today().date() if str(str.lower(conf['cutoff_date'])) == 'today' else datetime.strptime(conf['cutoff_date'], '%d-%m-%Y').date()

    try:
        parts = date_string.strip().replace('Posted on:','').strip()
        date_object = datetime.strptime(parts, '%d %B %Y').date()
    
    except Exception as e:
        print(f"Error parsing date string: {date_string} - {e}")
        return False
    
    return date_object >= cutoff

if __name__ == '__main__':
    print(lower_bound_date_check('12 April 2026'))