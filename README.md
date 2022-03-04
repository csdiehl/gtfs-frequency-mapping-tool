This tool provides an easy-to-use command line interface for producing shapefiles with transit headways and frequencies for user-selected time periods and routes. It relies heavily on the [gtfs_functions](https://github.com/Bondify/gtfs_functions) python library for the essential calculations. 

## First time setup and installation

1. Download Anaconda (miniconda version) – a package and environment manager for Python

2. Clone this repo somewhere on your computer. This will be your working directory.

3. Open Anaconda Prompt. Run cd (path to working directory)

4. Run conda create –name (env name) –file environment.yml.

## Running the tool

1. Place input GTFS zip files in the working directory. Do not unzip them.

2. Open Anaconda Prompt. Cd to your working directory.

3. Run conda activate (env name)

4. Run python application.py

5. Follow the messages displayed in the prompt.

6. When finished, run conda deactivate.

## Settings

Route list: comma-separated list of routes (corresponding to route short name in GTFS)
Time Interval: Integer in 24-hr clock. frequencies will only be calculated for the specified hours

## Optional Configuration

The tool can be configured using an optional file. Use the config.py file as an example. 

Name the configuration file anything you want and place in the same folder. Run the tool with the name of the file (excluding .py) as a command line argument. 
