import os
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.gdal import OGRException
from django.db.utils import IntegrityError

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core import management

from censusfeatures.models import CensusCounty

from django.conf import settings
settings.DEBUG = False

censuscounty_mapping = {
    'statefp10' : 'STATEFP10',
    'countyfp10' : 'COUNTYFP10',
    'countyns10' : 'COUNTYNS10',
    'geoid10' : 'GEOID10',
    'name10' : 'NAME10',
    'namelsad10' : 'NAMELSAD10',
    'lsad10' : 'LSAD10',
    'classfp10' : 'CLASSFP10',
    'mtfcc10' : 'MTFCC10',
    'csafp10' : 'CSAFP10',
    'cbsafp10' : 'CBSAFP10',
    'metdivfp10' : 'METDIVFP10',
    'funcstat10' : 'FUNCSTAT10',
    'aland10' : 'ALAND10',
    'awater10' : 'AWATER10',
    'intptlat10' : 'INTPTLAT10',
    'intptlon10' : 'INTPTLON10',
    'the_geom' : 'MULTIPOLYGON',
}

class Command(BaseCommand):
    help="Import shapefiles of 2010 Tiger Counties"
    args = "<data_dir>"

    def get_version(self):
        return "0.1"
    
    def handle(self, *args, **options):

        datadir = args[0]
        shpfile = os.path.abspath(os.path.join(os.path.dirname(__file__), datadir+'/us_county_shapefiles//tl_2010_us_county10.shp'))

        print "Attempting import of shapefile "+shpfile

        try:
            lm = LayerMapping(CensusCounty, shpfile, censuscounty_mapping, encoding='latin-1')
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
