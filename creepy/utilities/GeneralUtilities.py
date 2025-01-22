#!/usr/bin/python
# -*- coding: utf-8 -*-
from os.path import expanduser
import webbrowser
from math import radians, cos, sin, asin, sqrt
from typing import Union

def getUserHome() -> str:
    """Returns the path to the user's home directory."""
    return expanduser("~")

def reportProblem() -> None:
    """Opens the web browser to report a problem on the GitHub issues page."""
    webbrowser.open_new_tab('https://github.com/ilektrojohn/creepy/issues')

def calcDistance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth 
    (specified in decimal degrees).
    
    Args:
        lat1 (float): Latitude of the first point.
        lng1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lng2 (float): Longitude of the second point.
    
    Returns:
        float: Distance between the two points in meters.
    """
    # Convert decimal degrees to radians 
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # Haversine formula 
    delta_lng = lng2 - lng1 
    delta_lat = lat2 - lat1 
    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lng / 2) ** 2
    c = 2 * asin(sqrt(a)) 

    # 6378100 m is the mean radius of the Earth
    meters = 6378100 * c
    return meters     

def html_escape(text: str) -> str:
    """
    Escapes HTML special characters in a given text.
    
    Args:
        text (str): The text to escape.
    
    Returns:
        str: The escaped text.
    """
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)