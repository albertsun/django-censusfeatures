from django.contrib.gis import admin
from redistricting.apps.features.models import CensusBlock, CensusTract, CensusCounty

class CensusCountyAdmin(admin.OSMGeoAdmin):
    list_display = ('countyfp10', 'statefp10',)

class CensusTractAdmin(admin.OSMGeoAdmin):
    list_display = ('tractce10', 'countyfp10', 'statefp10',)

class CensusBlockAdmin(admin.OSMGeoAdmin):
    list_display = ('blockce10', 'tractce10', 'countyfp10', 'statefp10',)


admin.site.register(CensusBlock, CensusBlockAdmin)
admin.site.register(CensusTract, CensusTractAdmin)
admin.site.register(CensusCounty, CensusCountyAdmin)


