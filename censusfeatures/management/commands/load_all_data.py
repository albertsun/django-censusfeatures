from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
#from django.contrib.gis.utils import LayerMapping, add_postgis_srs
from django.core import management

class Command(BaseCommand):
    help="Run through all the other commands in order to load data"
    #option_list= NoArgsCommand.option_list + ()
    args = "<data_dir>"

    def get_version(self):
        return "0.2"

    def handle(self, *args, **options):

        datadir = args[0]
        print "Calling ./manage.py load_censuscounties"
        management.call_command('load_censuscounties', datadir)

        print "Calling ./manage.py load_censustracts"
        management.call_command('load_censustracts', datadir)

        print "Calling ./manage.py load_censusblocks"
        management.call_command('load_censusblocks', datadir)

        print "Calling ./manage.py load_pl94data"
        management.call_command('load_pl94data', datadir)
