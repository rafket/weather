#!/bin/python
import os
import dbus
import requests
import json
import time

username = os.environ.get('USER')
useragent = '{}@{}'.format(username, os.uname().nodename)

def getLocation():
    bus = dbus.SystemBus()
    manager = bus.get_object('org.freedesktop.GeoClue2', '/org/freedesktop/GeoClue2/Manager')
    clientPath = dbus.Interface(manager, dbus_interface='org.freedesktop.GeoClue2.Manager').GetClient()
    client = bus.get_object('org.freedesktop.GeoClue2', clientPath)
    dbus.Interface(client, dbus_interface='org.freedesktop.DBus.Properties').Set('org.freedesktop.GeoClue2.Client', 'DesktopId', dbus.types.String(username))
    dbus.Interface(client, dbus_interface='org.freedesktop.GeoClue2.Client').Start()
    time.sleep(3)
    locPath = dbus.Interface(client, dbus_interface='org.freedesktop.DBus.Properties').Get('org.freedesktop.GeoClue2.Client', 'Location')
    loc = bus.get_object('org.freedesktop.GeoClue2', locPath)

    prop = dbus.Interface(loc, dbus_interface='org.freedesktop.DBus.Properties').GetAll('org.freedesktop.GeoClue2.Location')
    Longitude = prop['Longitude']
    Latitude = prop['Latitude']

    dbus.Interface(manager, dbus_interface='org.freedesktop.GeoClue2.Manager').DeleteClient(clientPath)
    return Latitude, Longitude

def getWeather(lat, lon):
    r = requests.get("https://api.weather.gov/points/{},{}".format(lat, lon), headers={'User-Agent': useragent})
    if 'properties' not in r.json():
        return getWeatherFindU(lat, lon)
    forecastURL = r.json()['properties']['forecastHourly']
    r = requests.get(forecastURL+'?units=si', headers={'User-Agent': useragent})
    forecast = r.json()['properties']['periods']

    return "now: {}°C {}, 3hr: {}°C {}".format(forecast[0]['temperature'], forecast[0]['shortForecast'], forecast[3]['temperature'], forecast[3]['shortForecast'])

def getWeatherFindU(lat, lon):
    import pandas as pd

    r = requests.get("http://www.findu.com/cgi-bin/wxnear.cgi?lat={:.2f}&lon={:.2f}".format(lat, lon))
    df = pd.read_html(r.text)[0]
    df = df.rename(columns=df.iloc[0]).drop(0)
    df['invdist'] = 1/df['distance'].astype(float)
    df['temp'] = df['temp'].astype(float)
    df['rain'] = df['rain*'].astype(float)
    df['rain 24h'] = df['rain 24h'].astype(float)
    df['humidity'] = df['humidity'].astype(float)

    temp = sum((df['temp'] * df['invdist'] / sum(df['invdist'])).dropna())
    temp = (temp - 32) * 5/9
    humidity = sum((df['humidity'] * df['invdist'] / sum(df['invdist'])).dropna())
    rain = sum((df['rain'] * df['invdist'] / sum(df['invdist'])).dropna())
    rain = rain * 2.54
    rain24h = sum((df['rain 24h'] * df['invdist'] / sum(df['invdist'])).dropna())
    rain24h = rain24h * 2.54

    return "{:.1f}°C, humidity: {:.0f}%, rain 1hr: {:.1f}cm, rain 24hr: {:.1f}cm".format(temp, humidity, rain, rain24h)

print(getWeather(*getLocation()))
