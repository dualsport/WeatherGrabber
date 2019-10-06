#Settings file for WeatherGrabber
import os

#Create list of urls to collect weather from
wx_base = 'https://api.weather.gov'

wx_stations = os.environ.get('WX_STATIONS')

#Endpoint for posting weather data
endp_base = os.environ.get('IOT_ENDP_BASE_URL')
endp_data_add = 'weatherdata/add/'
endp_current_data = 'weatherdata/current/'
endp_station_list = 'weatherstation/list/'
endp_station_add = 'weatherstation/add/'

#API token
api_token = os.environ.get('IOT_ENDP_TOKEN')


