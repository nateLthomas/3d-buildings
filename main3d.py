from bs4 import BeautifulSoup
import requests
import os
import urllib.request
import concurrent.futures
import subprocess
import pandas as pd
import sys
import geopandas as gpd

workers = 4

def get_urls(path):
    r  = requests.get(path)
    data = r.text
    soup = BeautifulSoup(data)
    URLS = []
    for link in soup.find_all('a'):
        #print(link.get('href'))
        URLS.append(path+link.get('href'))
    return URLS

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

make_dir('./download')
make_dir('./download2')
make_dir('./types')

URLS = []



#long_url_1 = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/UGS_Wasatch/UGS_Wasatch_hh/Del_5/"
long_url_2 = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/UGS_Wasatch/UGS_Wasatch_hh/Del_4/"
#long_url_3 = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/UGS_Wasatch/UGS_Wasatch_hh/Del_3/" 
#long_url_4 = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/UGS_Wasatch/UGS_Wasatch_hh/Del1_2/"

#one = get_urls(long_url_1)
#URLS = URLS + one
two = get_urls(long_url_2)
URLS = URLS + two
#three = get_urls(long_url_3)
#URLS = URLS + three
#four = get_urls(long_url_4)
#URLS = URLS + four
print(URLS)
print(len(URLS))

def load_url(url, timeout):
    base=os.path.basename(url)
    out = os.path.splitext(base)
    outtxt = out[0] + out[1]
    if os.path.exists('download/'+outtxt) == True:
        return "already complete"
    else:
        url = url
        print(url)
        urllib.request.urlretrieve(url, 'download/'+outtxt)
        return url

with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
    
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('one finished')

os.system('gdalbuildvrt step1.vrt download/*img')
os.system('gdalwarp step1.vrt final.vrt -t_srs EPSG:3857')
os.system('gdaltindex types/index.shp download/*.img')
os.system(""" ogr2ogr types/output.shp types/index.shp -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM \'index\' " """)
os.system('ogr2ogr -clipdst types/output.shp outgood.shp Buildings_shp/Buildings/Buildings.shp')
#os.system('gdaldem hillshade step1.vrt terrain1.tif -of GTiff -b 1 -z 1.0 -s 1.0 -az 315.0 -alt 45.0')
os.system('ogrinfo outgood.shp -sql "ALTER TABLE outgood ADD COLUMN mainid INTEGER"')
os.system('ogrinfo outgood.shp -dialect SQLite -sql "UPDATE outgood set mainid = rowid+1"')
os.system('ogr2ogr -f GeoJSON out1.geojson outgood.shp')
#ogr2ogr -f GeoJSON -t_srs crs:84 out1.geojson types/outgood.shp

URLS = []
long_url_2 = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/UGS_Wasatch/UGS_Wasatch_be/Del_4/"
two = get_urls(long_url_2)
URLS = URLS + two
#three = get_urls(long_url_3)
#URLS = URLS + three
#four = get_urls(long_url_4)
#URLS = URLS + four
print(URLS)
print(len(URLS))

def load_url2(url, timeout):
    base=os.path.basename(url)
    out = os.path.splitext(base)
    outtxt = out[0] + out[1]
    if os.path.exists('download2/'+outtxt) == True:
        return "already complete"
    else:
        url = url
        print(url)
        urllib.request.urlretrieve(url, 'download2/'+outtxt)
        return url

with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
    
    future_to_url = {executor.submit(load_url2, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('one finished')

os.system('gdalbuildvrt step2.vrt download2/*img')
os.system('gdaltindex types/index2.shp download2/*.img')

import xarray as xr

ds = xr.open_rasterio("step1.vrt")
print(ds)

ds2 = xr.open_rasterio("step2.vrt")
print(ds)

# Insert your lat/lon/band below to extract corresponding pixel value
#ds.sel(band=2, lat=19.9, lon=39.5, method='nearest').values

import json
from shapely.geometry import mapping, shape
from rtree import index

idx = index.Index()

with open('out1.geojson') as json_data:
    d = json.load(json_data)

p = []
for a in d['features']:
    temp_coord = []
    polygon = shape(a['geometry'])
    coords = polygon.representative_point()
    #print(coords)
    longs = coords.x
    lats = coords.y
    val = ds.sel(band=1, y=lats, x=longs, method='nearest').values
    val2 = ds2.sel(band=1, y=lats, x=longs, method='nearest').values
    temp_coord.append(a['properties']['mainid'])
    #print(val - val2)
    temp_coord.append(val)
    temp_coord.append(val2)
    temp_coord.append(val-val2)

    #print(temp_coord)
# get the x and y coordinate of the centroid
    #print()
    p.append(temp_coord)
    #print(val)
    #p.append(polygon.bounds)
    #print(polygon.bounds)
    #idx.insert(wo, polygon.bounds)
    #wo += 1

df = pd.DataFrame(p, columns=['id', 'buildheight', 'groundheight', 'height'])

df.to_csv('output.csv')
'''
#way way to slow
#.system('ogr2ogr -sql "select outgood.*, output.* from outgood left join \'output.csv\'.output on outgood.mainid = output.id" shape_join.shp outgood.shp')

#ogr2ogr -sql "select europe_shapes.*, attributes.* from europe_shapes left join 'attributes.csv'.attributes on europe_shapes.ID = status.ID" shape_join.shp D:\testfolder\europe_shapes.shp

#for me in df:
    #print(idx.intersection(me).bounds)
    #hits = idx.intersection(me, objects=True)
    #for i in hits:
        #print(i.bounds)
#print(idx.bounds)
'''
# so much quicker
dfcsv = pd.read_csv('output.csv')

fname = "./out1.geojson"

df = gpd.read_file(fname)

mer = pd.merge(df, dfcsv, left_on='mainid', right_on='id')

mer = mer[mer['height'] > 0]  
try: 
    os.remove('test.geojson')
except OSError:
    pass
mer.to_file('test.geojson', driver="GeoJSON")
