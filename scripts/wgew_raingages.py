import os
from .convert_coords import utm_to_latlon
from appwgew.models import Raingage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run():
    print("Importing WGEW raingage data.")
    Raingage.objects.all().delete()
    with open('scripts/wgew_raingages.csv', 'r') as f:
        for i, l in enumerate(f.readlines()):
            if i > 0:
                values = l.strip().split('|')
                watershed_id = values[0]
                gage_id = values[1]
                east = values[2]
                north = values[3]
                elevation = values[4]
                err = values[5]

                lat, lng = utm_to_latlon(12, float(east), float(north))
                rg = Raingage(
                    watershed_id = watershed_id,
                    gage_id = gage_id,
                    latitude = lat,
                    longitude = lng,
                    elevation = elevation,
                    err = err
                )
                rg.save()

    print("Done!")