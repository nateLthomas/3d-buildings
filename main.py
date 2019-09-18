from bs4 import BeautifulSoup
import requests
import os
import urllib.request
import concurrent.futures
import subprocess
import pandas as pd
import sys
import geopandas as gpd
import download as d1
import download2 as d2
import ogr as ogr
import query as qt


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

make_dir('./download')
make_dir('./download2')
make_dir('./types')

d1.load_data(4)
d2.load_data2(4)
ogr.ogr_make()
qt.raster_points()