import os, sys
from osgeo import ogr
from math import ceil, cos, pi
# the code is from this reference: http://varunpant.com/posts/how-to-create-fishnets-or-geospatial-grids

def make_fishnet(outputGridfn,xmin,xmax,ymin,ymax,gridHeight,gridWidth):

    # convert sys.argv to float
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    gridWidth = float(gridWidth)
    gridHeight = float(gridHeight)

    # Coordinate offsets in radians
    R=6378137 # Earth’s radius, sphere
    dn = gridWidth #the width of each grid unit in meters
    de = gridHeight #the height of each grid unit in meters
    
    dLat = dn/R
    dLon = de/(R*cos(pi*ymin/180))
    
    # OffsetPosition, decimal degrees
    gridWidth = dLat * 180/pi # the corresponding latitude for each grid unit's width
    gridHeight = dLon * 180/pi # the corresponding latitude for each grid unit's height

    # get rows
    rows = ceil((ymax-ymin)/gridHeight)
    # get columns
    cols = ceil((xmax-xmin)/gridWidth)

    # start grid cell envelope
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight

    # create output file
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(outputGridfn):
        os.remove(outputGridfn)
    outDataSource = outDriver.CreateDataSource(outputGridfn)
    outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon )
    featureDefn = outLayer.GetLayerDefn()

    # create grid cells
    countcols = 0
    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        countrows = 0

        while countrows < rows:
            countrows += 1
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(poly)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy

            # new envelope for next poly
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight

        # new envelope for next poly
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth

    # Close DataSources
    outDataSource.Destroy()

if __name__ == "__main__":

    if len( sys.argv ) != 8:
        print ("[ ERROR ]")
        sys.exit( 1 )

    main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7] )
