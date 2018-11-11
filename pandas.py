import argparse
import csv
import math
import sys
import pandas as pd
import numpy as np
from geopy.distance import vincenty
from argparse import RawTextHelpFormatter

EARTH_RADIUS = 6372797.560856


# holds Transfer metrics between stops
class TransferMetrics:
    def __init__(self, from_stop_id, to_stop_id, transfer_type, min_transfer_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.transfer_type = transfer_type
        self.min_transfer_time = min_transfer_time

    def __str__(self):
        return self.from_stop_id + "," + self.to_stop_id + "," + self.transfer_type + "," + self.min_transfer_time


class Stop:
    # def __init__(self, sid, lon, lat, location_type):
    def __init__(self, sid, lon, lat):
        self.sid = sid
        self.lat = lat
        self.lon = lon
        # self.location_type = location_type

    def __str__(self):
        return self.sid + "," + self.lon + "," + self.lat + ","\
               # + self.location_type

    def to_dict(self):
        return {
            'sid': self.sid,
            'lon': self.lon,
            'lat': self.lat,
            # 'location_type': self.location_type
        }

def read_file(input_file):
    # stops = dict()
    stops = list()
    columns_to_read = ['stop_id', 'stop_lon', 'stop_lat', 'location_type']
    df = pd.read_csv(input_file, usecols=columns_to_read, converters={"stop_id": int, "stop_lon": float, "stop_lat": float, "location_type": int})
    # we want only stops of type 0 (which are stops and not physical station or entrance - see GTFS docs
    df = df[df['location_type'] == 0]
    return df
    #
    # with open(input_file, encoding="utf8", mode='r') as f:
    #     reader = csv.reader(f)
    #     header = next(reader)
    #     stop_id_ind = header.index("stop_id")
    #     stop_lon_ind = header.index("stop_lon")
    #     stop_lat_ind = header.index("stop_lat")
    #     location_type_ind = header.index("location_type")
    #
    #     for row in reader:
    #         # we want only stops of type 0 (which are stops and not physical station or entrance - see GTFS docs)
    #         stop_location_type = row[location_type_ind]
    #         if stop_location_type == '0':
    #             data_tpl = Stop(row[stop_id_ind], row[stop_lon_ind], row[stop_lat_ind])
    #             # Store the stop data: id, lon, Lat
    #             # stop_id = row[stop_id_ind]
    #             # stops [stop_id] = data_tpl
    #             stops.append(data_tpl)
    #
    #     stops_df = pd.DataFrame.from_records([s.to_dict() for s in stops])
    # return stops_df


def calculate_transfers(stops, walking_speed, transfer_time, max_distance):
    transfers = list()
    pd.DataFrame(dq)
    for stop_1_ind in stops:
        stop_1 = stops[stop_1_ind]
        for stop_2_ind in stops:
            stop_2 = stops[stop_2_ind]
            # if stop_1.sid != stop_2.sid: - Navitia's rust code doesnt ignore this
            man_distance = calculate_man_distance(stop_1, stop_2)
            if man_distance <= max_distance:
                print(man_distance)
                transfers.append(TransferMetrics(stop_1.sid, stop_2.sid, 2, int(man_distance / walking_speed)
                                                 + transfer_time))
    return transfers

def calculate_man_distance(stop1, stop2):
    phi1 = math.radians(float(stop1.lat))
    phi2 = math.radians(float(stop2.lat))
    lambda1 = math.radians(float(stop1.lon))
    lambda2 = math.radians(float(stop2.lon))

    x = math.sin((phi2 - phi1) / 2) ** 2
    y = math.cos(phi1) * math.cos(phi2) * math.sin((lambda2 - lambda1) / 2.) ** 2

    return 2 * EARTH_RADIUS * math.asin(math.sqrt(x + y))


def write_file(output, transfers):
    with open(output, "w") as text_file:
        print(f"from_stop_id,to_stop_id,transfer_type,min_transfer_time", file=text_file)
        for ind, transfer in enumerate(transfers):
            transfer_datum = transfers[ind]
            print(f"{transfer_datum.from_stop_id},{transfer_datum.to_stop_id},{transfer_datum.transfer_type}, "
                  f"{transfer_datum.min_transfer_time} ", file=text_file)


def main(argv):
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('input', nargs='?', help='input file', default='stops.txt')
    parser.add_argument('output', nargs='?', help='output file', default='transfers.txt')
    parser.add_argument('walking_speed', type=float, nargs='?',
                        help='The walking speed is meters per second.\n '
                             'You may want to divide your initial speed by \n '
                             'sqrt(2) to simulate Manhattan distances', default=0.785)
    parser.add_argument('transfer_time', type=int, nargs='?', help='Transfer time in seconds',
                        default='0')
    parser.add_argument('max_distance', type=float, nargs='?',
                        help='The max distance in meters to compute the transfer',
                        default=500)

    args = parser.parse_args(argv)

    stops = read_file(args.input)
    stopCoordinates = pd.DataFrame()
    stopCoordinates['coords'] = list(zip(stops.stop_lat, stops.stop_lon))
    square = pd.DataFrame(
        np.zeros(len(stopCoordinates) ** 2).reshape(len(stopCoordinates), len(stopCoordinates)),
        index=stopCoordinates.index, columns=stopCoordinates.index)

    def get_distance(col):
        end = stopCoordinates.ix[col.name]['coords']
        return stopCoordinates['coords'].apply(vincenty, args=(end,), ellipsoid='WGS-84')

    distances = square.apply(get_distance, axis=1).T

    def units(input_instance):
        return input_instance.meters

    distances_meters = distances.applymap(units)

    # transfers = calculate_transfers(stops, args.walking_speed, args.transfer_time, args.max_distance)
    # write_file(args.output, transfers)
    print("done")


if __name__ == "__main__":
    main(sys.argv[1:])


# USE https://stackoverflow.com/questions/46572860/speeding-up-a-nested-for-loop-through-two-pandas-dataframes