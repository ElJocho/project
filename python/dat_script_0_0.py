#!/usr/bin/env python

import grass.script as grass                 #auto
import os                                    #for importing data
   
def main():
    grass.run_command('g.region', flags='p') #auto
    grass.run_command('g.remove', flags='f' , type='vector', pattern='*') #optional - delets old files to delete corrupted data and have a fresh start


#                                                                      1. importing and preparing data

#load input data
    #sets basepath
    input_path = "C:/Users/jocho/Desktop/opengis/project/data/in"   #for input data
    inter_path = "C:/Users/jocho/Desktop/opengis/project/data/inter"#cache
    out_path = "C:/Users/jocho/Desktop/opengis/project/data/out"    #output data
    
    #bus -> route as lines, stops as points
    path_bus_stop=os.path.join(input_path, 'bus', 'bus_stop.shp')
    grass.run_command('v.in.ogr', input=path_bus_stop, output='busstop', overwrite=True, cnames=True)
    
    path_bus_route=os.path.join(input_path, 'bus', 'bus_route.shp')
    grass.run_command('v.in.ogr', input=path_bus_route, output='busroute', overwrite=True, cnames=True)
    
    #tram -> route as lines, stops as points
    path_tram_stop=os.path.join(input_path, 'tram', 'tram_stops.shp')
    grass.run_command('v.in.ogr', input=path_tram_stop, output='tramstop', overwrite=True, cnames=True)

    path_tram_route=os.path.join(input_path, 'tram', 'tram_route.shp')
    grass.run_command('v.in.ogr', input=path_tram_route, output='tramroute', overwrite=True, cnames=True)
    
    #streets as lines
    path_streets=os.path.join(input_path, 'streets', 'streets.shp')
    grass.run_command('v.in.ogr', input=path_streets, output='streets', overwrite=True, cnames=True)

    #central point
    path_central_point=os.path.join(input_path, 'central_point', 'central_point.shp')
    grass.run_command('v.in.ogr', input=path_central_point, output='central_point', overwrite=True, cnames=True)

#patching bus and tram routes together: 
    grass.run_command('v.patch', input=['tramroute','busroute'], output='tbroute', overwrite=True)   
    grass.run_command('v.patch', input=['busstop','tramstop'], output='tbstop', overwrite=True)   


#connecting central point to stops
    grass.run_command('v.patch', input=['central_point','tramstop'], output='c_tramstop', overwrite=True)    
    grass.run_command('v.patch', input=['central_point','busstop'], output='c_busstop', overwrite=True)    
    grass.run_command('v.patch', input=['central_point','tbstop'], output='c_tbstop', overwrite=True)    
    grass.run_command('v.db.addtable', map='tbstop',overwrite=True) 

#exporting/importing to write features with cat 1 into seperate features -> otherwise 2 have the same id
    grass.run_command('v.out.ogr',input='c_tramstop',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_c_tramstop=os.path.join(inter_path, 'c_tramstop.shp')
    grass.run_command('v.in.ogr', input=path_c_tramstop, output='c_tramstop', overwrite=True, cnames=True)
    grass.run_command('v.out.ogr',input='c_busstop',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_c_busstop=os.path.join(inter_path, 'c_busstop.shp')
    grass.run_command('v.in.ogr', input=path_c_busstop, output='c_busstop', overwrite=True, cnames=True)
    grass.run_command('v.out.ogr',input='c_tbstop',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_c_tbstop=os.path.join(inter_path, 'c_tbstop.shp')
    grass.run_command('v.in.ogr', input=path_c_tbstop, output='c_tbstop', overwrite=True, cnames=True)

#cleaning vectors -> removes unconnected lines (rmdangle), duplicates(rmdupl), parallel lines within a certain distance(snap) and connects lines at every intersection (break)
    grass.run_command('v.clean', input='tramroute', output='tramroute2', tool=['snap','break','rmdupl','rmdangle'],overwrite=True, threshold=[30,0,0,30])
    grass.run_command('v.clean', input='busroute', output='busroute2', tool=['snap','break','rmdupl','rmdangle'],overwrite=True, threshold=[30,0,0,30])
    grass.run_command('v.clean', input='tbroute', output='tbroute2', tool=['snap','break','rmdupl','rmdangle'],overwrite=True, threshold=[30,0,0,30])
    grass.run_command('v.clean', input='streets', output='streets2', tool=['break','rmdupl','rmdangle'],overwrite=True, threshold=[0,0,30])


#                                                           2. network 1 and preparation

#conntecting central point to lines
    grass.run_command('v.net', input='busroute2', points='c_busstop', output='busnet', operation='connect', threshold = 20, overwrite=True, alayer=1,nlayer=2)
    grass.run_command('v.net', input='tramroute2', points='c_tramstop', output='tramnet', operation='connect', threshold = 20, overwrite=True,alayer=1,nlayer=2)
    grass.run_command('v.net', input='tbroute2', points='c_tbstop', output='tbnet', operation='connect', threshold = 20, overwrite=True,alayer=1,nlayer=2)
   
#Preparing lists that are classified by traveled distance in meters with different methods.
    costs_tram=[]   #trams travel at 295m/min-> input for costs
    costs_bus=[]    #buses travel at 233m/min
    costs_foot=[]   #traveling by foot comes in at 67m/min
    costs_tb=[]
    speed_tram=295
    speed_bus=233
    speed_foot=67
    speed_tb=264
    for i in range(1,99):       #-> 99 categories and +1 in category means +x traveled distance
        costs_tram.append(temp_tram)
        costs_bus.append(temp_bus)
        costs_foot.append(temp_foot)
        costs_tb.append(temp_tb)
        temp_tram=temp_tram+speed_tram
        temp_bus=temp_bus+speed_bus
        temp_foot=temp_foot+speed_foot
        temp_tb=temp_tb+speed_tb

#network analysis of from central point along the lines
    grass.run_command('v.net.iso', input='tramnet', output='iso_tram',center_cats=[1], costs=costs_tram, overwrite=True, nlayer=2)
    grass.run_command('v.net.iso', input='busnet', output='iso_bus',center_cats=[1], costs=costs_bus, overwrite=True, nlayer=2)
    grass.run_command('v.net.iso', input='tbnet', output='iso_tb',center_cats=[1], costs=costs_tb, overwrite=True, nlayer=2)


#                                                        3. extracting cats from network 1

#creating table with category numbers
    grass.run_command('v.db.addtable', map='iso_tram',overwrite=True)
    grass.run_command('v.db.addtable', map='iso_bus',overwrite=True)
    grass.run_command('v.db.addtable', map='iso_tb',overwrite=True)

#adding column
    grass.run_command('v.db.addcolumn', map='tramstop', columns='first_tram_distance integer',overwrite=True)
    grass.run_command('v.db.addcolumn', map='busstop', columns='first_bus_distance integer',overwrite=True)
    grass.run_command('v.db.addcolumn', map='tbstop', columns='first_tb_distance integer',overwrite=True)

#connecting network with stations to keep catnum
    grass.run_command('v.distance',from_='tramstop', to='iso_tram', upload='cat',column='first_tram_distance', overwrite=True)    
    grass.run_command('v.distance',from_='busstop', to='iso_bus', upload='cat',column='first_bus_distance', overwrite=True)    
    grass.run_command('v.distance',from_='tbstop', to='iso_tb', upload='cat',column='first_tb_distance', overwrite=True)    


#                                                       4. network 2 and preparation

#connecting tramstops to streets
    grass.run_command('v.net', input='streets2', points='tramstop', output='streets_tram', operation='connect', threshold = 20, overwrite=True, alayer=1,nlayer=2)
    grass.run_command('v.net', input='streets2', points='busstop', output='streets_bus', operation='connect', threshold = 20, overwrite=True, alayer=1,nlayer=2)
    grass.run_command('v.net', input='streets2', points='tbstop', output='streets_tb', operation='connect', threshold = 20, overwrite=True, alayer=1,nlayer=2)

#Preparation for iso_streets_*
    all_centers=[]                #this part creates a list x of ints from 1-999 as an input for center_cats -> all stops are center_cats
    for i in range(1,999):
        all_centers.append(i)

#iso from stops into streets
    grass.run_command('v.net.iso', input='streets_tram', output='iso_streets_tram',center_cats=all_centers, costs=costs_foot, overwrite=True, nlayer=2)
    grass.run_command('v.net.iso', input='streets_bus', output='iso_streets_bus',center_cats=all_centers, costs=costs_foot, overwrite=True, nlayer=2)
    grass.run_command('v.net.iso', input='streets_tb', output='iso_streets_tb',center_cats=all_centers, costs=costs_foot, overwrite=True, nlayer=2)


#                                                   5. calculating the shortest time and preparation

#creating table with category numbers
    grass.run_command('v.db.addtable', map='iso_streets_tram',overwrite=True)
    grass.run_command('v.db.addtable', map='iso_streets_bus',overwrite=True)
    grass.run_command('v.db.addtable', map='iso_streets_tb',overwrite=True)

#exporting and then importing to convert net into vector feature and to split features with the same cat
    #tram
    grass.run_command('v.out.ogr',input='iso_streets_tram',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_streets_tram_cat=os.path.join(inter_path, 'iso_streets_tram.shp')
    grass.run_command('v.in.ogr', input=path_streets_tram_cat, output='streets_tram_cat2', overwrite=True, cnames=True)
    #bus
    grass.run_command('v.out.ogr',input='iso_streets_bus',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_streets_bus_cat=os.path.join(inter_path, 'iso_streets_bus.shp')
    grass.run_command('v.in.ogr', input=path_streets_bus_cat, output='streets_bus_cat2', overwrite=True, cnames=True)
    #tb
    grass.run_command('v.out.ogr',input='iso_streets_tb',output=inter_path, format='ESRI_Shapefile',overwrite=True)
    path_streets_tb_cat=os.path.join(inter_path, 'iso_streets_tb.shp')
    grass.run_command('v.in.ogr', input=path_streets_tb_cat, output='streets_tb_cat2', overwrite=True, cnames=True)

#adds cost value from center to stop in new column
    #tram
    grass.run_command('v.db.addcolumn', map='streets_tram_cat2', columns='first_tram_distance2 int',overwrite=True)
    grass.run_command('v.distance',from_='streets_tram_cat2', to='tramstop', upload='to_attr', to_column='first_tram_distance',column='first_tram_distance2', overwrite=True)   
    #bus
    grass.run_command('v.db.addcolumn', map='streets_bus_cat2', columns='first_bus_distance2 int',overwrite=True)
    grass.run_command('v.distance',from_='streets_bus_cat2', to='busstop', upload='to_attr', to_column='first_bus_distance',column='first_bus_distance2', overwrite=True)   
    #tb
    grass.run_command('v.db.addcolumn', map='streets_tb_cat2', columns='first_tb_distance2 int',overwrite=True)
    grass.run_command('v.distance',from_='streets_tb_cat2', to='tbstop', upload='to_attr', to_column='first_tb_distance',column='first_tb_distance2', overwrite=True)   

#adds both values -> final time cost from street to center without waiting times
    #tram
    grass.run_command('v.db.addcolumn', map='streets_tram_cat2', columns='final_costs_tram int',overwrite=True)
    grass.run_command('v.db.update', map='streets_tram_cat2',layer=1, column='final_costs_tram', query_column="first_tram_distance2 + cat_",overwrite=True)
    #bus
    grass.run_command('v.db.addcolumn', map='streets_bus_cat2', columns='final_costs_bus int',overwrite=True)
    grass.run_command('v.db.update', map='streets_bus_cat2',layer=1, column='final_costs_bus', query_column="first_bus_distance2 + cat_",overwrite=True)
    #tb !!+5 because you need to wait between lines
    grass.run_command('v.db.addcolumn', map='streets_tb_cat2', columns='final_costs_tb int',overwrite=True)
    grass.run_command('v.db.update', map='streets_tb_cat2',layer=1, column='final_costs_tb', query_column="first_tb_distance2 + cat_ + 5",overwrite=True)
#deleting lines not connected to the center
    grass.run_command('v.db.update', map='streets_bus_cat2', column='final_costs_bus', value=99999, where="first_bus_distance2 = 0",overwrite=True)

#adding all final colums into streets_tb_cat2 for easier comparability (is that a word?)
    grass.run_command('v.db.addcolumn', map='streets_tb_cat2', columns='tram_cost int',overwrite=True)
    grass.run_command('v.distance',from_='streets_tb_cat2', to='streets_tram_cat2', upload='to_attr', to_column='final_costs_tram',column='tram_cost', overwrite=True)   
    grass.run_command('v.db.addcolumn', map='streets_tb_cat2', columns='bus_cost int',overwrite=True)
    grass.run_command('v.distance',from_='streets_tb_cat2', to='streets_bus_cat2', upload='to_attr', to_column='final_costs_bus',column='bus_cost', overwrite=True)   

#selecting the lowest possible value for each street -> potentially very bad method
    grass.run_command('v.db.addcolumn', map='streets_tb_cat2', columns='lowest int',overwrite=True)
    grass.run_command('v.db.update', map='streets_tb_cat2',layer=1, column='lowest', qcolumn="tram_cost",overwrite=True, where="tram_cost <= bus_cost<=final_costs_tb")
    grass.run_command('v.db.update', map='streets_tb_cat2',layer=1, column='lowest', qcolumn="bus_cost",overwrite=True, where="bus_cost <= tram_cost AND bus_cost <= final_costs_tb")
    grass.run_command('v.db.update', map='streets_tb_cat2',layer=1, column='lowest', qcolumn="final_costs_tb", overwrite=True, where="final_costs_tb <= tram_cost AND final_costs_tb <= bus_cost")



#                                                    7. exporting final layers

#exporting final layers
    grass.run_command('v.out.ogr',input='streets_tb_cat2',output=out_path, format='ESRI_Shapefile',overwrite=True)
    grass.run_command('v.out.ogr',input='streets_tram_cat2',output=out_path, format='ESRI_Shapefile',overwrite=True)
    grass.run_command('v.out.ogr',input='streets_bus_cat2',output=out_path, format='ESRI_Shapefile',overwrite=True)




if __name__ == '__main__':                     #executes main
    main()                                     
