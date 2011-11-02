import os
import csv

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core import management

#from redistricting.apps.features.models import DataBlock
from django.db import connection, transaction

from django.conf import settings
settings.DEBUG = False

class Command(BaseCommand):
    help="Import Fairplan 2020 aggregated PL94 block level census data"
    args = "<data_dir>"
    
    def get_version(self):
        return "0.2"
    
    def handle(self, *args, **options):
        """
        Assume files are located as below, and named like:
        ak_PL94_block2010.txt
        al_PL94_block2010.txt
        etc.
        The fileset has Puerto Rico, but we don't actually want to import it, because we didn't import the shapefile for it.

        Since we've already done ./manage.py load_censusblocks there are already CensusBlock objects in place. As noted in https://code.djangoproject.com/ticket/7623 we can't convert these into DataBlock objects, so we're just going to do it in raw SQL.
        """

        """
        Data files have the same number of census blocks as shapefiles
        $ wc -l `find . -name '*.txt'`
        lines 11155538 - 77190 (for pr) - 51 (for headers) = 11078297
        # SELECT COUNT(geoid10) FROM censusblocks;
        11078297 in postgresql
        """

        datadir = args[0]
        
        cursor = connection.cursor()
        cursor.execute("""TRUNCATE TABLE datablocks""")
        transaction.commit_unless_managed()
        
        for filename in os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), datadir+"/fairplan2020data/"))):
            filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), datadir+"/fairplan2020data/"+filename))
            if ((filename[3:7] == 'PL94') and (filename[0:2] != 'pr')):
                print "Attempting import of PL94 data in "+filepath
                with open(filepath) as f:
                    reader = csv.reader(f)

                    counter = 0
                    for row in reader:
                        if (counter > 0):
                            # skip the first row, it just has header information
                            row[0]
                            
                            cursor.execute("""INSERT INTO datablocks VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", [ row[0], int(row[46]), int(row[77]), int(row[75]), int(row[48]), int(row[49]), int(row[50]), int(row[51]), int(row[82]), int(row[99]), int(row[112]), int(row[143]), int(row[141]), int(row[114]), int(row[115]), int(row[116]), int(row[117]), int(row[148]), int(row[165]) ])
                        counter += 1
                        if (counter % 1000 == 0):
                            print "Imported "+str(counter)+" rows"
                print "Imported PL94 data in "+filepath
        print "Finalizing..."
        transaction.commit_unless_managed() #commit the transaction

"""
SELECT statefp10 || countyfp10 || tractce10 AS tractgeoid10, SUM(totpop), SUM(totpop_wnh), SUM(totpop_h), SUM(totpop_black), SUM(totpop_na), SUM(totpop_a), SUM(totpop_hi), SUM(totpop_other), SUM(totpop_multiracial), SUM(vap), SUM(vap_wnh), SUM(vap_h), SUM(vap_black), SUM(vap_na), SUM(vap_a), SUM(vap_hi), SUM(vap_other), SUM(vap_multiracial) FROM "datablocks" INNER JOIN "censusblocks" ON ("datablocks"."censusblock_ptr_id" = "censusblocks"."geoid10") GROUP BY statefp10, countyfp10, tractce10

"""
