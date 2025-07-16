from enum import Enum

TIME_UNIT_DICT = {
    'minute' : 'T',
    'hour' : 'H',
    'day' : 'D',
    'week': 'W',
    'month': 'M'
}



class TimeStructure(Enum):
    T = "minute"
    H = "hour"
    D = "day"
    W = "week"
    M = "month"
    