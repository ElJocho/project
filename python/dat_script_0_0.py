#!/usr/bin/env python

import grass.script as grass                 #auto
import os                                      #fuer import

def main():
    grass.run_command('g.region', flags='p') #auto
    
#load input data
    #sets basepath
    input_path = "C:/Users/jocho/Desktop/opengis/project/data/in" 
    #bus
    path_bus_stop=os.path.join(input_path, 'bus', 'bus_stop.shp')
    grass.run_command('v.in.ogr', input=path_bus_stop, output='busstop', overwrite=True, cnames=True)
    
    path_bus_route=os.path.join(input_path, 'bus', 'bus_route.shp')
    grass.run_command('v.in.ogr', input=path_bus_route, output='busroute', overwrite=True, cnames=True)
    #train
    path_train_stop=os.path.join(input_path, 'train', 'train_stops.shp')
    grass.run_command('v.in.ogr', input=path_train_stop, output='trainstop', overwrite=True, cnames=True)

    path_train_route=os.path.join(input_path, 'train', 'train_route.shp')
    grass.run_command('v.in.ogr', input=path_train_route, output='trainroute', overwrite=True, cnames=True)
    #tram
    path_tram_stop=os.path.join(input_path, 'tram', 'tram_stops.shp')
    grass.run_command('v.in.ogr', input=path_tram_stop, output='tramstop', overwrite=True, cnames=True)

    path_tram_route=os.path.join(input_path, 'tram', 'tram_route.shp')
    grass.run_command('v.in.ogr', input=path_bus_route, output='tramroute', overwrite=True, cnames=True)



#conntecting stops to lines
    grass.run_command('v.net', input='busroute', points='busstop', output='busnet', operation='connect', threshold = 20, overwrite=True)


    
if __name__ == '__main__':                     #auto
    main()                                     #auto
