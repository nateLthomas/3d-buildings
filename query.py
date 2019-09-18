import xarray as xr
import os
import json
from shapely.geometry import mapping, shape
from rtree import index
import pandas as pd
import sys
import geopandas as gpd

def raster_points():
    

    ds = xr.open_rasterio("step1.vrt")
    print(ds)
    ds2 = xr.open_rasterio("step2.vrt")
    print(ds)
    # Insert your lat/lon/band below to extract corresponding pixel value
    #ds.sel(band=2, lat=19.9, lon=39.5, method='nearest').values
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