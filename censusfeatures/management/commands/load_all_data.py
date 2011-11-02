from optparse import make_option

from django.core.management.base import NoArgsCommand, CommandError
from django.contrib.gis.utils import LayerMapping, add_postgis_srs
from django.core import management

class Command(NoArgsCommand):
    help="Run through all the other commands in order to load data"
    option_list= NoArgsCommand.option_list + ()

    def get_version(self):
        return "0.1"

    def handle_noargs(self, **options):
        
        print "Calling ./manage.py load_censuscounties"
        management.call_command('load_censuscounties')

        print "Calling ./manage.py load_censustracts"
        management.call_command('load_censustracts')

        print "Calling ./manage.py load_censusblocks"
        management.call_command('load_censusblocks')

        print "Calling ./manage.py load_pl94data"
        management.call_command('load_pl94data')
