import requests
import json
from datetime import datetime
from urllib.parse import urljoin
try:
    import dev_settings as s
except:
    import settings as s


def api_get(base_url, api, token=None, parameters=None):
    api_endpoint = urljoin(base_url, api)
    headers = {'accept': 'application/json',
               }
    if token:
        headers['Authorization'] = token

    r = requests.get(url=api_endpoint, headers=headers, params=parameters)

    if r.status_code == 200:
        return r.json()
    else:
        print('Status:', r.status_code)
        print('Reason:', r.reason)
        print('Response text:', r.text)
        print('Requested URL:', r.url)
        print('\n\n')
        #raise ValueError('Invalid response received from server.')
        return None

def api_post(base_url, api, token=None, parameters=None):
    api_endpoint = urljoin(base_url, api)
    headers = {'Content-Type': 'application/json',
                }
    if token:
        headers['Authorization'] = token

    post = requests.post(url=api_endpoint, headers=headers, json=parameters)
    return post

def station_list():
    #returns a list of weather stations known by IOT endpoint
    api_stations = api_get(s.endp_base, s.endp_station_list, s.api_token)
    station_li = []
    for station in api_stations:
        station_li.append(station['identifier'])
    return station_li

    return st

def create_station(station):
    #Creates new weather station
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    payload = {'identifier': station,
                'name': station,
                'description': 'Added by WeatherGrabber.py ' + ts,
                'type': 'Unknown'}
    response = api_post(s.endp_base, s.endp_station_add, s.api_token, payload)
    if response.status_code == 201:
        #Log creation & email notification
        return True
    return False
        #Log error & email notification

def get_weather(station):
    endpoint = 'stations/' + station + '/observations/current'
    wx = api_get(s.wx_base, endpoint)
    return wx

def wx_keyvalue(wx, keypath, default=None, rounding=None):
    for key in keypath:
        if isinstance(wx, dict):
            wx = wx.get(key, default)
        else:
            return default
    if wx and rounding is not None:
        try:
            wx = round(float(wx), rounding)
        except ValueError:
            #Not convertable
            pass
    return wx

def parse_weather(station, wx):
    #Parse the wx dict returning bits we care about
    pwx = {}
    pwx['identifier'] = station
    pwx['temperature'] = wx_keyvalue(wx, ['properties','temperature','value'], None, 2)
    pwx['dewpoint'] = wx_keyvalue(wx, ['properties','dewpoint','value'], None, 2)
    pwx['temp_uom'] = wx_keyvalue(wx, ['properties','temperature','unitCode'])
    pwx['wind_speed'] = wx_keyvalue(wx, ['properties','windSpeed','value'], None, 2)
    pwx['wind_gust'] = wx_keyvalue(wx, ['properties','windGust','value'], None, 2)
    pwx['wind_uom'] = wx_keyvalue(wx, ['properties','windSpeed','unitCode'])
    pwx['wind_dir'] = wx_keyvalue(wx, ['properties','windDirection','value'], None, 0)
    pwx['dir_uom'] = wx_keyvalue(wx, ['properties','windDirection','unitCode'])
    pwx['timestamp'] = wx_keyvalue(wx, ['properties','timestamp'])
    #Clean None values out of pwx
    cwx = {k: v for k, v in pwx.items() if v is not None}
    #Remove 'unit:' from UOMs
    for key in cwx:
        if 'uom' in key:
            cwx[key] = cwx[key].replace('unit:','')
    #Replace certain UOMs
    if cwx['wind_uom'] == 'm_s-1':
        cwx['wind_uom'] = 'm/sec'
    if cwx['dir_uom'] == 'degree_(angle)':
        cwx['dir_uom'] = 'degAngle'
    return cwx

if __name__ == "__main__":
    api_stations = station_list()
    #print(api_stations)
    print(s.wx_stations)
    for station in s.wx_stations:
        if station in api_stations:
            valid_station = True
        else:
            #Creation new station
            valid_station = create_station(station)
        if valid_station:
            #Get station weather
            wx = get_weather(station)
            payload = parse_weather(station, wx)
            #Get current record from IOT api
            cur = api_get(s.endp_base, s.endp_current_data + station, s.api_token)
            #Don't post wx if ts matches current saved record ts
            record_exists = False
            if len(cur) > 0:
                cur_ts = cur[0]['timestamp'].replace('Z', '+00:00')
                record_exists = (cur_ts == payload['timestamp'])
            if not record_exists:
                #Post station weather
                post = api_post(s.endp_base, s.endp_data_add, s.api_token, payload)
                print(post.status_code)
            else:
                print(f'{station} has existing record matching timestamp.')
