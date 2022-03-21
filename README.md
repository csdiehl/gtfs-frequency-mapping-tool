This tool provides an easy-to-use command line interface for producing shapefiles with transit headways and frequencies for user-selected time periods and routes. It relies heavily on the [gtfs_functions](https://github.com/Bondify/gtfs_functions) python library for the essential calculations. 

## First time setup and installation

1. Download Anaconda (miniconda version) – a package and environment manager for Python

2. Clone this repo somewhere on your computer. This will be your working directory.

3. Open Anaconda Prompt. Run cd (path to working directory)

4. Run conda create –name (env name) –file environment.yml.

## Running the tool

1. Place input GTFS zip files in the "feeds" folder inside the working directory. Do not unzip them.

2. Open Anaconda Prompt. Cd to your working directory.

3. Run conda activate (env name)

4. Run python app.py

5. Follow the messages displayed in the prompt (see "settings" and "configuration" below).

6. When finished, run conda deactivate.

## Settings

Route list: comma-separated list of routes (corresponding to route short name in GTFS)
Time Interval: Integer in 24-hr clock. frequencies will only be calculated for the specified hours

Day type: Busiest Date will filter the feed to the single busiest service date. Weekend or weekday will select all trips of the corresponding type.

Direction: Uses the inbound / outbound identifier from GTFS. Note that this does not correspond to a particular cardinal direction and may be more useful for corridor-specific or other local analyses. 

Split results by hour? If selected, will create a separate feature in the shapefile for each hour within the specified time interval. Otherwise, all trips in the time interval will be aggregated into one time bucket (appropriate for most use cases). 

## Optional Configuration

The tool can be configured using an optional file. Use the config.py file as an example. This file consists of a dictionary with the following key-value pairs:

Feed: name of the GTFS zip file including extension
Direction: One of "Inbound" or "Outbound"
Day Type: One of "weekday", "weekend", "All Days", "Busiest Day"
Routes: List of routes entered as strings (e.g. ["101", "102", "156"]. These should correspond to the route_short_name field in GTFS.
Time Interval: List containing 3 items. Integer for start and end hour (24-hr clock), and "yes" or "no" for splitting results by hour (e.g. [6,9, "yes"]). 
File name: what to call the output file (without the extension)

Name the configuration file anything you want and place in the same folder. Run the tool with the name of the config file (excluding the .py extension) as a command line argument (e.g. python app.py config). 
