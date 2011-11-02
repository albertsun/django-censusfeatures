import os
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.gdal import OGRException
from django.db.utils import IntegrityError

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core import management

from censusfeatures.models import CensusTract

from django.conf import settings
settings.DEBUG = False

censustracts_mapping = {
    'statefp10' : 'STATEFP10',
    'countyfp10' : 'COUNTYFP10',
    'tractce10' : 'TRACTCE10',
    'geoid10' : 'GEOID10',
    'name10' : 'NAME10',
    'namelsad10' : 'NAMELSAD10',
    'mtfcc10' : 'MTFCC10',
    'funcstat10' : 'FUNCSTAT10',
    'aland10' : 'ALAND10',
    'awater10' : 'AWATER10',
    'intptlat10' : 'INTPTLAT10',
    'intptlon10' : 'INTPTLON10',
    'the_geom' : 'MULTIPOLYGON',
}

class Command(BaseCommand):
    help="Import shapefiles of 2010 Tiger Census Tracts"
    args = "<data_dir>"

    def get_version(self):
        return "0.2"
    
    def handle(self, *args, **options):

        datadir = args[0]
        
        # Need to do this 50 times, onece for the shapefile of each state
        for i in range(1,57):
            # files are named with zero padded FIPS codes
            if i < 10:
                padded_i = "0"+str(i)
            else:
                padded_i = str(i)
            
            shpfile = os.path.abspath(os.path.join(os.path.dirname(__file__), datadir+'/state_tract_shapefiles/tl_2010_'+padded_i+'_tract10/tl_2010_'+padded_i+'_tract10.shp'))

            print "Attempting import of shapefile "+shpfile

            try:
                lm = LayerMapping(CensusTract, shpfile, censustracts_mapping)
            except OGRException:
                print "Could not open datasource ",
                print shpfile
            else:
                try:
                    lm.save(strict=True, verbose=False, progress=True)
                except IntegrityError:
                    print "Already imported ",
                    print shpfile
                    from django.db import transaction
                    transaction.rollback()
                else:
                    print "Imported shapefile "+shpfile
                    print
