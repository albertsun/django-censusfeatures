from models import CensusBlock, CensusTract, CensusCounty, DataBlock
from utils import gmerc

from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.gis.geos import GEOSGeometry

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from django.core import serializers
from django.views.decorators.cache import cache_page

import json
import time

# def blocks_by_bounds(request):
#     """
#     /geom/CensusBlocksBox/?bbox=42.864637,-88.891514,42.94645,-79.43732
#     """
#     return features_bounds(request, DataBlock)

# def tracts_by_bounds(request):
#     return features_bounds(request, CensusTract)

# def features_bounds(request, GeomClass):
#     """
#     /geom/<FeatureType>sBox/?bbox=42.864637,-88.891514,42.94645,-79.43732
#     """
#     bbox = request.GET.get('bbox', '')
#     jsonpcallback = request.GET.get('callback','')
#     if bbox == '':
#         raise Http404


#     # has lat lngs in this order: SWNE
#     bbox = bbox.split(',')

#     # TODO: to ease scaling, will probably have to round these off and memcached the result
#     bbox_wkt = "POLYGON(("
#     bbox_wkt += bbox[1]+" "+bbox[0]+","
#     bbox_wkt += bbox[1]+" "+bbox[2]+","
#     bbox_wkt += bbox[3]+" "+bbox[2]+","
#     bbox_wkt += bbox[3]+" "+bbox[0]+","
#     bbox_wkt += bbox[1]+" "+bbox[0]
#     bbox_wkt += "))"
#     box_geom = GEOSGeometry(bbox_wkt, srid=4326)

#     cbs = GeomClass.objects.filter(the_geom__intersects = box_geom)
#     return _output_geo_queryset(cbs, jsonpcallback)


@cache_page(60*60*24*7)
def serve_block_tiles(request, z, x, y):
    """
    /geom/CensusBlockTile/<z>/<x>/<y>.json

    For example:
    /geom/CensusBlockTile/16/19302/24633.json
    """
    z,x,y = [int(z), int(x), int(y)]

    assert isinstance(z, int), TypeError("zoom must be an int from 0 to 30")
    assert isinstance(x, int), TypeError("x must be an int")
    assert isinstance(y, int), TypeError("y must be an int")

    if (z < 13):
        return HttpResponse(json.dumps([]), mimetype="application/json")
    else:
        return serve_tile(request, z, x, y, DataBlock)

def serve_tile(request, z, x, y, GeomClass):
    """
    /geom/<FeatureType>Tile/<z>/<x>/<y>.json
    """
    jsonpcallback = request.GET.get('callback','')


    # Translate tile coordinates into lat-lng bounds
    x1 = x * 256
    x2 = x1 + 255
    y1 = y * 256
    y2 = y1 + 255
    n, w = gmerc.px2ll(x1, y1, z)
    s, e = gmerc.px2ll(x2, y2, z)
    s,w,n,e = [str(s), str(w), str(n), str(e)]
    bbox_wkt = "".join(["POLYGON((",
                        w+" "+s+",",
                        w+" "+n+",",
                        e+" "+n+",",
                        e+" "+s+",",
                        w+" "+s,
                        "))"])
    
    box_geom = GEOSGeometry(bbox_wkt, srid=4326)

    cbs = GeomClass.objects.filter(the_geom__intersects = box_geom)
    return _output_geo_queryset(cbs, jsonpcallback)



def _output_geo_queryset(qs, jsonpcallback=""):
    """
    Helper function that takes a query set and returns the geometries and info as json.
    Uses a JSONP callback if one is specified
    """

    #Bleh. this bit is pretty ugly
    try:
        geoms = { "type": "FeatureCollection",
                  "features": [{ 'id': c.geoid10, 'type': 'Feature', 'geometry': json.loads(c.the_geom.json), 'properties': serializers.serialize('python', [c])[0]['fields'] } for c in qs]
                  }
        if (len(geoms['features']) == 0):
            return HttpResponse(json.dumps([]), mimetype="application/json")
        assert('totpop' in geoms['features'][0]['properties']), AttributeError("Doesn't have population info")
    except AttributeError:
        geoms = { "type": "FeatureCollection",
                  "features": [{ 'id': c.geoid10, 'geometry': json.loads(c.the_geom.json), 'properties': None } for c in qs]
                  }
        
    if (jsonpcallback != ''):
        out = jsonpcallback + '(' + json.dumps(geoms) + ')'
    else:
        out = json.dumps(geoms)
    
    #resp = HttpResponse(out, mimetype="application/json")
    resp = HttpResponse(out)
    resp['X-ALBERT'] = "=)"
    return resp
