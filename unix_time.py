import time
import pandas as pd

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    timestamp = pd.to_datetime(unix, unit='s')
    return timestamp