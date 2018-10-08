import os
from django.contrib.gis.geos import fromstr
from .convert_coords import utm_to_latlon
from appsrer.models import PhotoStation

SRID = 4326
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run():
    print("Running photo station import.")

    with open(BASE_DIR + '/scripts/photostations.csv', 'r') as f:
        lines = f.read().split()
        for l in lines:
            values = l.split('|')
            station_id = values[0]
            x_coord = values[1]
            y_coord = values[2]
            lat, lng = utm_to_latlon(12, float(x_coord), float(y_coord))
            point = fromstr('POINT(%s %s)' % (lng, lat), srid=SRID)
            ps = PhotoStation(name=station_id, location=point)
            ps.save()

    print("Done!")
