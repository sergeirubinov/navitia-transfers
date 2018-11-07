import csv, sys, argparse, math
from argparse import RawTextHelpFormatter

EARTH_RADIUS = 6372797.560856;

# holds Transfer metrics between stops
class TransferMetrics:
    def __init__(self, from_stop_id, to_stop_id,  transfer_type, min_transfer_time):
        self.from_stop_id = from_stop_id;
        self.to_stop_id = to_stop_id;
        self.transfer_type = transfer_type
        self.min_transfer_time = min_transfer_time

    def __str__(self):
        return self.from_stop_id + "," + self.to_stop_id + "," + self.transfer_type + "," + self.min_transfer_time


class Stop:
    def __init__(self, stop_id, lon, lat, location_type):
        self.stop_id = stop_id
        self.lon = lon
        self.lat = lat
        self.location_type = location_type
        
    def __str__ (self):
        return self.stop_id + "," + self.lon + "," + self.lat;


def read_file(input):
    stops = dict()

    with open('stops.txt', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        stop_idInd = header.index("stop_id")
        stop_lonInd = header.index("stop_lon")
        stop_latInd = header.index("stop_lat")

        for row in reader:
            dataTpl = Stop(row[stop_idInd], row[stop_lonInd], row[stop_latInd])
            # Store the stop data: id, lon, Lat
            stopID = row[stop_idInd]
            stops[stopID] = dataTpl

    return stops


def calculate_transfers():




    network = list()
    #iterate over source stops
    for sstopA in stops:
        stopA = stops[sstopA]
        for sstopB in stops:
            stopB = stops[sstopB]
            routeCounter = 0
    #dont work on the same stop
            if (stopA.id != stopB.id):
    #iterate over stopA routes
                for datumA in stopA.metrics:
                    routeA = datumA.route
                    seqA = datumA.seq
                    for datumB in stopB.metrics:
                        routeB = datumB.route
                        seqB = datumB.seq
                        if routeA == routeB and int(seqA)+1 == int(seqB):
                            #network.append(TruplteStop(stopA.id, stopB.id,routeCounter))
                            routeCounter += 1
                if routeCounter > 0:
                    network.append(TruplteStop(stopA.id, stopB.id,routeCounter))

    # The arcs need to be defined by the node ids not the stopIDs
    stopsToNodes = dict()

    with open("OnlyNodesAndEdges.net", "w") as text_file:
        stopsLen = len(stops)
        print (f"*Vertices {stopsLen}", file=text_file)
        for ind, stop in enumerate(stops):
            #print (f"{ind+1} \"{stops[stop].name}\" \"{stops[stop].lon}\" \"{stops[stop].lat}\" \"{stops[stop].id}\"", file=text_file)
            print (f"{ind+1} \"{stops[stop].id}\"", file=text_file)
            stopsToNodes[stop] = ind+1

        print (f"*Arcs", file=text_file)
        for stop in network:
            print (f"{stopsToNodes[stop.stopA]} {stopsToNodes[stop.stopB]} {stop.numOfLines} ", file=text_file)




def calculate_man_distance (stopOne, stopTwo):
    phi1 = stopOne.stop_lat.to_radians()
    phi2 = stopTwo.stop_lat.to_radians()
    lambda1 = stopOne.stop_lon.to_radians()
    lambda2 = stopOne.stop_lon.to_radians()

    x = math.sin((phi2 - phi1) / 2)**2
    y = math.cos(phi1) * math.cos(phi2) * math.sin((lambda2 - lambda1) / 2.)**2;

    return 2 * EARTH_RADIUS * math.asin(math.sqrt(x + y))


def main (argv):
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('input', nargs='?', help='input file', default='stops.txt')
    parser.add_argument('out', nargs='?', help='output file', default='transfers.txt')
    parser.add_argument('walking_speed', type=float, nargs='?', help='The walking speed is meters per second.\n '
                                                          'You may want to divide your initial speed by \n '
                                                          'sqrt(2) to simulate Manhattan distances', default=0.785)
    parser.add_argument('transfer-time', type=int, nargs='?', help='Transfer time in seconds', default='0')
    parser.add_argument('max-distance', type=float, nargs='?', help='The max distance in meters to compute the transfer',
                        default=500)

    args = parser.parse_args(argv)

    stops = read_file(args.input)

    calculate_man_distance(stops)
    print("done")

if __name__ == "__main__":
   main(sys.argv[1:])
