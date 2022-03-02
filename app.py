import gtfs_functions as gtfs
import pandas as pd
import geopandas as gpd
import sys 
from PyInquirer import prompt
import matplotlib.pyplot as plt
import os
import time
import utm
from helper_functions import check_routes, filter_dates

#Getting User Input###################################################
#Corridors dictionary for selecting routes in a single corridor
net_choices = ['Network Wide', 'Enter Route List']

dir_list = os.listdir('./feeds')
for file in dir_list[:]:
    if (file.find('zip') == -1):
        dir_list.remove(file)

questions = [{
    'type': 'list',
    'message': 'Choose a GTFS zip file in this folder',
    'name': 'GTFS',
    'choices': dir_list
},{
    'type': 'list',
    'message': 'Choose Direction',
    'name': 'direction',
    'choices': ['Inbound', 'Outbound', 'Both Ways']
},{
  'type': 'list',
  'message': 'Choose type of day: ',
  'name': 'day_type',
  'choices': ['Busiest Day', 'weekday', 'weekend', 'All Days']
}, {
  'type': 'list',
  'message': 'Choose network-wide analysis or enter routes',
  'name': 'network',
  'choices': net_choices
}]

#Save user preferences
answers = prompt(questions)
network = answers['network']
GTFS = answers['GTFS']
selected_day = answers['day_type']
chosen_direction = answers['direction']

if network == 'Enter Route List': 
  route_choices = input('Route List: ')
  route_list = route_choices.upper().replace(' ', '').split(",")

while True:
  start_hr = int(input('Start Hour: '))
  end_hr = int(input('End Hour: '))
  if (start_hr >= 0) & (start_hr <= 23) & (end_hr >= 1) & (end_hr <= 24) & (end_hr > start_hr):
    break

######Starting Analysis#############################################
#Start tracking runtime
start = time.time()

#Importing the GTFS
print('')
print("Importing GTFS...")
routes, stops, stop_times, trips, shapes = gtfs.import_gtfs('./feeds/' + GTFS, busiest_date = True if selected_day == 'Busiest Day' else False)
print('GTFS imported in ' + str(round((time.time() - start) / 60, 3)) + ' minutes')

#Filtering the GTFS to the appropriate corridor
if (network == 'Enter Route List'): 
  updated_route_list = check_routes(route_list, routes)
  print('Filtering gtfs for routes: ' + str(updated_route_list))
  routes = routes[routes.route_short_name.isin(updated_route_list)]

#time filter
start_secs = start_hr * 3600
end_secs = end_hr * 3600

trips_in_period = stop_times[(stop_times.arrival_time >= start_secs) & (stop_times.arrival_time <= end_secs)].trip_id.unique()

#Day type filter - weekday, weekend, etc. 
selected_ids = filter_dates(selected_day, GTFS)
#change data type of service id to match selected ids
trips['service_id'] = trips.service_id.astype(str)

#Apply the filters to the other tables
trips = trips[trips.route_id.isin(routes.route_id.unique()) & (trips.trip_id.isin(trips_in_period)) & (trips.service_id.isin(selected_ids))]
stop_times = stop_times[stop_times.trip_id.isin(trips.trip_id.unique())]
stops = stops[stops.stop_id.isin(stop_times.stop_id.unique())]
shapes = shapes[shapes.shape_id.isin(trips.shape_id.unique())]

#check that filter worked correctly
if len(shapes) == 0:
  print('No trips found with selected filters')

#might need to find more flexible way to filter just bus routes that works for multiple agencies

#Creating subsegments for each route
print('Splitting routes into segments...')
freq_start = time.time()

segments_gdf = gtfs.cut_gtfs(stop_times, stops, shapes)
print('Segments created in ' + str(round((time.time() - freq_start) / 60, 3)) + ' minutes')


#Frequencies for subsegments of each route
print("Calculating frequencies...")
cutoffs = list(range(start_hr, end_hr + 1))

seg_freq = gtfs.segments_freq(segments_gdf, stop_times, routes, cutoffs = cutoffs)

#Filter for time window, combine frequency along shared segments
if answers['direction'] != 'Both Ways': 
  combined = seg_freq[seg_freq.dir_id == chosen_direction]

else: 
  combined = seg_freq[(seg_freq.route_name != 'All lines')]


combined.groupby(['segment_id', 'window', 's_st_id', 's_st_name', 'e_st_name']).agg({'route_name': list, 'frequency': 'sum', 'ntrips': 'sum', 'geometry': 'first'}).reset_index()
combined['route_name'] = combined.route_name.apply(lambda x: ', '.join(map(str, x))) #turn list into string so can be saved in shapefile
combined['day_type'] = selected_day
combined['direction'] = chosen_direction
combined = gpd.GeoDataFrame(combined, crs="EPSG:3857")
#combined.drop(columns = ['route_id', 'route_name', 'dir_id'], inplace = True)

#calculate number of hours in each time window and headways (minute)
diff = pd.to_datetime(combined.window.str.split("-", expand = True)[1], format = '%H:%M') - pd.to_datetime(combined.window.str.split("-", expand = True)[0], format = '%H:%M')
hours = combined['hours'] = diff.dt.total_seconds() / 3600
combined['headway_mins'] = round((1 / (combined.frequency / hours)) * 60, 1)

#Ask for file name
while True: 
  file_name = input('Enter a name for the output file: ')
  if len(file_name) < 20:
    break

#Saving results in geoJSON / shapefile
print('Saving results...')


gtfs.save_gdf(combined, file_name, shapefile = True, geojson = False)
#Save a basic map for reference / error checking
ax = combined.plot(figsize=(20, 20), column = 'headway_mins', cmap = 'inferno', 
            scheme = 'NaturalBreaks', k = 6, legend = True, alpha = .7, markersize = 2)
ax.set_axis_off()
plt.savefig('map.png')

end = round((time.time() - start) / 60, 2)
print('Finished in ' + str(end) + ' minutes')


#print('failed to write output shapefile')

