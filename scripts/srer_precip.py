import os
from precip.models import Raingage, PrecipEvent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

station_name_map = [
    {"id": "white", "name": "Whitehouse"},
    {"id": "watre", "name": "Water Retention"},
    {"id": "sw", "name": "Southwest"},
    {"id": "scs5n", "name": "SCS-5N"},
    # {"id": "scs#1", "name": "SCS" },
    {"id": "scs#1", "name": "SCS #1"},
    {"id": "ruela", "name": "Ruelas"},
    {"id": "roden", "name": "Rodent"},
    {"id": "robin", "name": "Robinson"},
    {"id": "road", "name": "Road"},
    {"id": "past3", "name": "Pasture 3"},
    {"id": "parke", "name": "Parker"},
    {"id": "pa11a", "name": "Pasture 11A"},
    {"id": "nw", "name": "Northwest"},
    {"id": "nrnch", "name": "North Ranch"},
    {"id": "ne", "name": "Northeast"},
    {"id": "muhle", "name": "Muhlenbergia"},
    {"id": "mcgib", "name": "McGibbon"},
    {"id": "limst", "name": "Limestone"},
    {"id": "johns", "name": "Johnson Ranch"},
    {"id": "ibp", "name": "IBP"},
    {"id": "hughe", "name": "Hughes"},
    {"id": "huerf", "name": "Huerfano"},
    {"id": "grari", "name": "Gravelly Ridge"},
    {"id": "fores", "name": "Forest"},
    {"id": "flori", "name": "Florida"},
    {"id": "fagan", "name": "Fagan"},
    {"id": "eriop", "name": "Eriopoda"},
    {"id": "desst", "name": "Desert Station"},
    {"id": "desri", "name": "Desert Rim"},
    {"id": "desgr", "name": "Desert Grassland"},
    {"id": "choll", "name": "Cholla"},
    {"id": "box", "name": "Box"},
    {"id": "amado", "name": "Amado"},
    {"id": "airst", "name": "Airstrip"},
    {"id": "164", "name": "Enclosure 164"},
    {"id": "45", "name": "Enclosure 45"},
    {"id": "41", "name": "Enclosure 41"},
    {"id": "205", "name": "Enclosure 205"},
    {"id": "18", "name": "Enclosure 18"},
    {"id": "131", "name": "Encl. No. 131"},
]


def precip_values(values):
    output = []

    for k, v in enumerate(values):
        if v in ['-9999', '']:
            output.append(None)
        else:
            output.append(float(int(v) / 100.00))

    return output


def find_station_name(name):
    station_name = None

    for s in station_name_map:
        if s['id'] == name:
            station_name = s['name']

    return station_name


def run():
    print("Loading precip data.")
    PrecipEvent.objects.all().delete()
    events = []
    # STATION|YEAR|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|||
    i = 0
    with open(BASE_DIR + '/scripts/srer_precip.csv', 'r') as f:
        for line in f.readlines():
            if i > 0:
                values = line.strip().split('|')
                station = values[0].lower()
                year = values[1]
                station_name = None

                station_id_list = list(i['id'] for i in station_name_map)
                if station in station in station_id_list:
                    station_name = find_station_name(station)
                else:
                    station_name = station

                try:
                    raingage = Raingage.objects.get(name=station_name)
                except Exception:
                    print("Rain station not found: %s, %s, %s" % (station, station_name, year))

                precip_vals = precip_values(values[2:])

                for k, v in enumerate(precip_vals):
                    # month = PrecipEvent.MONTH_CHOICES[k][0]
                    event = PrecipEvent(raingage=raingage, year=year, month=k, precip=v)
                    events.append(event)
                    # event.save()
            i += 1

    if events:
        PrecipEvent.objects.bulk_create(events)

    print("Done.")
