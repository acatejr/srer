import os, datetime
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from .convert_coords import utm_to_latlon
from appwgew.models import Raingage, PrecipEvent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run():
    print("Importing WGEW precip event data.")
    PrecipEvent.objects.all().delete()
    with open('scripts/wgew_precip.csv', 'r') as f:
        current_raingage_id = None
        rg = None
        events = []

        for i, l in enumerate(f.readlines()):
            if i > 0:
                values = l.strip().split('|')
                gage = values[0]
                dt = values[1].split('/')
                tm = values[2]
                duration = values[3]
                depth = values[4]
                time_est = values[5]

                if len(dt[0]) == 1:
                    mo = '0{}'.format(dt[0])
                else:
                    mo = dt[0]

                if len(dt[1]) == 1:
                    dy = '0{}'.format(dt[1])
                else:
                    dy = dt[1]

                if len(dt[2]) == 1:
                    yr = '0{}'.format(dt[2])
                else:
                    yr = dt[2]

                dt = '{}-{}-{}'.format(yr, mo, dy)

                try:
                    # Only query for the raingage if the precip event's
                    # gage id has changed.
                    if (current_raingage_id != gage):
                        rg = Raingage.objects.get(gage_id=gage, watershed_id=63)
                        current_raingage_id = gage

                    pe = PrecipEvent(
                        raingage = rg,
                        event_date = dt,
                        event_time = tm,
                        duration = duration,
                        depth = depth,
                        time_est = time_est
                    )
                    events.append(pe)
                # Raingage 6 is not in the db os it raises this exception.
                # TODO: Need to add logging here.
                except ObjectDoesNotExist:
                    pass

        if events:
            PrecipEvent.objects.bulk_create(events)

    print("Done!")