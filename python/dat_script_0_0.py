#!/usr/bin/env python

import grass.script as grass                 #auto
import os                                      #fuer import
import subprocess
def main():
    grass.run_command('g.region', flags='p') #auto
    
#load input data
    #sets basepath
    input_path = "C:/Users/jocho/Desktop/opengis/project/data/in" 
    inter_path = "C:/Users/jocho/Desktop/opengis/project/data/inter"
    
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
    grass.run_command('v.in.ogr', input=path_tram_route, output='tramroute', overwrite=True, cnames=True)
    
    #streets
    path_streets=os.path.join(input_path, 'streets', 'streets.shp')
    grass.run_command('v.in.ogr', input=path_streets, output='streets', overwrite=True, cnames=True)

    #central point
    path_central_point=os.path.join(input_path, 'central_point', 'central_point.shp')
    grass.run_command('v.in.ogr', input=path_central_point, output='central_point', overwrite=True, cnames=True)

#central point to stops
    grass.run_command('v.patch', input=['central_point','tramstop'], output='c_tramstop', overwrite=True)    
    grass.run_command('v.patch', input=['central_point','busstop'], output='c_busstop', overwrite=True)    


#cleaning vectors
    grass.run_command('v.clean', input='tramroute', output='tramroute2', tool=['snap','break','rmdupl','rmdangle'],overwrite=True, threshold=[30,0,0,30])
    grass.run_command('v.clean', input='busroute', output='busroute2', tool=['break','rmdupl','rmdangle'],overwrite=True, threshold=[0,0,500])
    grass.run_command('v.clean', input='streets', output='streets2', tool=['break','rmdupl','rmdangle'],overwrite=True, threshold=[0,0,30])

#conntecting central point to buslines
    grass.run_command('v.net', input='busroute2', points='c_busstop', output='busnet', operation='connect', threshold = 20, overwrite=True, alayer=1,nlayer=2)

#conntecting central point to tramlines
    grass.run_command('v.net', input='tramroute2', points='c_tramstop', output='tramnet', operation='connect', threshold = 20, overwrite=True,alayer=1,nlayer=2)
    

#network analysis of from central point along the bus lines
    grass.run_command('v.net.iso', input='busnet', output='iso_bus2',center_cats=[1], costs=[1000,2000,3000,4000,5000,6000,7000,8000,9000,10000], overwrite=True, nlayer=2)
#network analysis of from central point along the tram lines
    
    costs_tram=[]   #trams travel at 295m/min-> input for costs
    speed_tram=295
    temp=295
    for i in range(1,99):
        costs_tram.append(temp)
        temp=temp+speed_tram
    grass.run_command('v.net.iso', input='tramnet', output='iso_tram',center_cats=[1], costs=costs_tram, overwrite=True, nlayer=2)

#creating table with category numbers
    grass.run_command('v.db.addtable', map='iso_tram',overwrite=True)
    grass.run_command('v.db.addtable', map='iso_bus2',overwrite=True)

#adding column
    grass.run_command('v.db.addcolumn', map='tramstop', columns='first_tram_distance integer',overwrite=True)

#connecting network with stations to keep catnum
    grass.run_command('v.distance',from_='tramstop', to='iso_tram', upload='cat',column='first_tram_distance', overwrite=True)    
 
#connecting tramstops to streets
    grass.run_command('v.net', input='streets2', points='tramstop', output='streets_tram', operation='connect', threshold = 20, overwrite=True, alayer=1,nlayer=2)
    y=[]
    x=[]                #this part creates a list x of ints from 1-999 as an input for center_cats -> all stops are center_cats
    for i in range(1,999): #and y as input for costs for walking in 100 meter distances
        x.append(i)
        y.append(i*100)

    grass.run_command('v.net.iso', input='streets_tram', output='iso_streets_tram',center_cats=x, costs=y, overwrite=True, nlayer=2)
    grass.run_command('v.db.addtable', map='iso_streets_tram',overwrite=True)

#    grass.run_command('v.select', ainput='iso_streets_tram', binput='streets2', output='streets_with_cat', overwrite=True, operator='overlap')
    grass.run_command('v.out.ogr',input='iso_streets_tram',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_streets_with_cat=os.path.join(inter_path, 'iso_streets_tram.shp')
    grass.run_command('v.in.ogr', input=path_streets_with_cat, output='streets_with_cat2', overwrite=True, cnames=True)


    grass.run_command('v.db.addcolumn', map='streets_with_cat2', columns='first_tram_distance2 int',overwrite=True)
    grass.run_command('v.distance',from_='streets_with_cat2', to='tramstop', upload='to_attr', to_column='first_tram_distance',column='first_tram_distance2', overwrite=True)    



if __name__ == '__main__':                     #auto
    main()                                     #auto
