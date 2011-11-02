from django.conf.urls.defaults import *
import views

# urls coming after ^geom/
urlpatterns = patterns('',
    # (r'^CensusBlocksBox/$', views.blocks_by_bounds),
    # (r'^CensusTractsBox/$', views.tracts_by_bounds),

    (r'^CensusBlockTile/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)\.json$', views.serve_block_tiles),
)
