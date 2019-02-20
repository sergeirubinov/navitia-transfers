# navitia-transfers
Python version for CanalTP Navitia's GTFS to transfers project.
Uses for loops to iterate over all the stops and calcualtes the distances between them.
It evetually outputs a list of tuples of stops with the distance between them in meters, where the distance is less than 500 m

Use gtfs2transfers.py only as pandas.py doesn't work... It takes around 40 minutes for Israel conversion
