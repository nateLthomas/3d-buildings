import os

def ogr_make():
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

    os.system('gdalbuildvrt step2.vrt download2/*img')
    os.system('gdaltindex types/index2.shp download2/*.img')