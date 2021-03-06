## analyse_knickpoints.py
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
## This scripts takes in the Mchi files with the knickpoint information
## and creates various plots.  User specifies a threshold knickpoint magnitude
## (difference in MChi between the upstream and downstream segments)
## MChi file is read in using pandas
##
## I'm writing this at midnight so here is a panda:
##             ,,,         ,,,
##          ;"   ^;     ;'   ",
##          ;    s$$$$$$$s     ;
##          ,  ss$$$$$$$$$$s  ,'
##          ;s$$$$$$$$$$$$$$$
##          $$$$$$$$$$$$$$$$$$
##         $$$$P""Y$$$Y""W$$$$$
##         $$$$  p"$$$"q  $$$$$
##         $$$$  .$$$$$.  $$$$
##           $$DcaU$$$$$$$$$$
##            "Y$$$"*"$$$Y"
##               "$b.$$"
##
##
## Knickpoint plots:
## 1. For each basin, it looks at the relationship between the flow distance
## (distance from the basin outlet) and the elevation of the knickpoints
## 2. Knickpoint magnitude vs elevation
##
## IDEAS TO ADD TO PLOTS:
## - Colour points by lithology (import USGS lithologies). Theory predicts that
## - the knickpoints of all the tributaries should be at the same elevation. How does
## lithology affect this?
## - Normalise flow distance by channel length/drainage area (chi coordinate)
## - Different marker for convex/concave knickpoints
## - Plots for along the mountain front: Distance from N - S along the Sierras. How
## does the elevation of the knickpoints vary as you move from N - S?
##
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
## Authors: FJC, BG
## 02/06/17
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

#set backend to run on server
import matplotlib
matplotlib.use('Agg')

#import modules
from matplotlib import pyplot as plt
import numpy as np
import os
import matplotlib
import pandas
from LSDPlottingTools import LSDMap_PointTools as PointTools

def read_MChi_file(DataDirectory, csv_name):
    """
    This function reads in the MChi file using pandas - the data is raw, I'll add processing functions
    file structure:
    latitude longitude elevation	flow distance	drainage area	diff ratio sign	source_key	basin_key
    FJC/BG 29/03/17
    """
    df = pandas.read_csv(DataDirectory+csv_name, sep=",")
    return df

def get_data_columns_from_csv(DataDirectory, csv_name, columns):
    """
    This function returns lists of specified column names from the MChi csv file.
    Must be strings equal to the column headers.
    FJC 29/03/17
    """
    column_lists = []
    df = read_MChi_file(DataDirectory, csv_name)
    for column_name in columns:
        print("I'm returning the "+column_name+" values as a list")
        column_values = list(df[column_name])
        column_lists.append(column_values)
    return column_lists

def make_cumulative_plot(DataDirectory, csv_name):
    print("Now printing the cumulative plot")
    sorted_data = read_MChi_file(DataDirectory, csv_name)
    temp_count = 0
    x_cumul, y_cumul = np.unique(sorted_data[:,11],return_counts= True)
    #y_cumul = np.unique(sorted_data[:,11],return_counts= True)
    for i in range(1,x_cumul.size):
        y_cumul[i] = y_cumul[i]+y_cumul[i-1]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x_cumul, y_cumul, 'k--', linewidth=1)

    print("Saving the Cumulative plot")
    # tidy up the figure
    ax.grid(True)
    ax.set_title('Cumulative step histograms')
    ax.set_xlabel('kinckpoint value')
    ax.set_ylabel('Cumulative %')
    #ax.set_ylim(0,100)
    ax.set_xlim(0,sorted_data[:,11].max())
    write_name = "kp_cumulative"
    file_ext = "png"
    plt.savefig(DataDirectory+write_name+"."+file_ext,dpi=300)
    plt.clf()

    #### Elevation against Knickpoints ####
def plot_knickpoint_elevations(DataDirectory, csv_name, kp_type = "diff"):
    """
    This function creates a plot of knickpoint elevations against magnitude
    FJC 29/03/17, modified from code by BG.
    """
    # read in the data from the csv to lists
    elevation = get_data_column_from_csv(DataDirectory, csv_name, kp_threshold, "elevation")
    kp_data = get_data_column_from_csv(DataDirectory, csv_name, kp_threshold, kp_type)

    # plot the figure
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(kp_data, elevation, 'k+', linewidth=0.5)
    ax.grid(True)
    ax.set_title('Elevation against knickpoint value')
    ax.set_xlabel('Knickpoint '+kp_type)
    ax.set_ylabel('Elevation (m)')
    #ax.set_ylim(0,100)
    ax.set_xlim(0,1000)
    write_name = "knickpoint_elevation_"+kp_type
    file_ext = "png"
    plt.savefig(DataDirectory+write_name+"."+file_ext,dpi=300)
    plt.clf()

def knickpoint_plots_for_basins(DataDirectory, csv_name, kp_type = "diff"):
    """
    This function creates subplots of knickpoint characteristics for each individual
    basin. kp_type define if you want the ratio data or the differencee data (diff by default).
    FJC 29/03/17
    """
    # read in data from the csv to lists
    columns = ["elevation", "flow distance", "drainage area", kp_type, "sign", "basin_key"]
    column_lists = get_data_columns_from_csv(DataDirectory, csv_name, columns)
    print(len(column_lists))
    elevation = column_lists[0]
    flow_distance = column_lists[1]
    drainage_area = column_lists[2]
    kp_data = column_lists[3]
    kp_sign = column_lists[4]
    basin_id = column_lists[5]
    #list_of_lists = zip(elevation,flow_distance,basin_id)
    #print column_lists

    # loop through and get a plot for each basin id
    ids = set(basin_id)
    for id in ids:
        print("This basin id/key is: "+str(id))
        these_lists = [(a,b,c,d,e,f) for (a,b,c,d,e,f) in zip(elevation,flow_distance,drainage_area,kp_data,kp_sign,basin_id) if f == id]
        this_elev, this_distance, this_area, this_magnitude, this_sign, this_id = zip(*these_lists)

        fig,ax = plt.subplots(figsize=(10,12))
        #ax = ax.ravel()
        #for i in range(len(ax)):
        ax.scatter(this_distance,this_elev,facecolors="None", edgecolors="k", s=this_magnitude)
        ax.set_xlabel('Flow distance (m)')
        ax.set_ylabel('Elevation (m)')

        write_name = "knickpoint_plots_basin_"
        file_ext = "png"
        plt.savefig(DataDirectory+write_name+str(id)+"."+file_ext,dpi=100)
        plt.close()

def select_main_basin(pd):
    """
    Function that takes a dataframe from the knickpoint anaysis tool and mask it on the main basin

    Args:
    pd = pandas dataframe to mask

    Returns:
    The new pandas dataframe sorted/masked

    Author: Yes
    """
    basins_count =  pd.groupby("basin_key")["basin_key"].count()
    maxi =basins_count[basins_count == basins_count.max()]
    biggest_basin = maxi.index.values[0]
    pd = pd[pd["basin_key"] == biggest_basin]
    return pd


def knickpoint_plotter(DataDirectory = "none", DEM_prefix ="none" , kp_type = "diff", FigFormat='pdf', processed = False, pd_name = "none"):
    """
    Function to test LSDMap_KnickpointPlotting

    Args:
        DataDirectory (str): the data directory of the chi csv file
        DEM_prefix (str): DEM name without extension
        kp_type (string): select the type of knickpoint data you want (diff vs ratio).
        processed (bool): Switch on to directly give a pandas dataframe to plots
        pd_name (string or pandas dataframe): Name of this theoretical pandas dataframe

    Returns:
        Plot of knickpoint (diff or ratio) for each basin

    Author: FJC
    """
    from LSDPlottingTools import LSDMap_PointTools as PointTools
    from LSDPlottingTools import LSDMap_KnickpointPlotting as KP

    # read in the raw csv file
    if(processed):
        if(DEM_prefix !="none" and DataDirectory != "none"):
            print("I will directly load your pandas dataframe, or at least try")
            kp_csv_fname = read_MChi_file(DataDirectory,DEM_prefix+'_KsnKn.csv')
            # get the point data objects
            PointData = PointTools.LSDMap_PointData(kp_csv_fname,data_type ="pandas", PANDEX = True)
        else:
            if(isinstance(pd_name, pandas.DataFrame)):
                PointData = PointTools.LSDMap_PointData(pd_name,data_type ="pandas", PANDEX = True)
    else:
        kp_csv_fname = DataDirectory+DEM_prefix+'_KsnKn.csv'
        print("I'm reading in the csv file "+kp_csv_fname)

        # get the point data objects
        PointData = PointTools.LSDMap_PointData(+kp_csv_fname, data_type ="csv", PANDEX = True)

    # get the basin keys
    basin = PointData.QueryData('basin_key')
    basin = [int(x) for x in basin]
    Basin = np.asarray(basin)
    basin_keys = np.unique(Basin)
    print('There are %s basins') %(len(basin_keys))

    # loop through each basin and make the figure
    for basin_key in basin_keys:
        FileName = DEM_prefix+"_KP_elevations_%s.%s" %(str(basin_key),FigFormat)
        KP.plot_knickpoint_elevations(PointData, DataDirectory, DEM_prefix, basin_key, kp_type, FileName, FigFormat)

if __name__ == "__main__":

    DataDirectory = '/home/s1675537/PhD/DataStoreBoris/GIS/Data/Carpathian/knickpoint/'
    baseName = "Buzau"
    dfp = read_MChi_file(DataDirectory,baseName+"_KsnKn.csv")
    dfp = select_main_basin(dfp)
    #csv_name = baseName + "_MChi.csv"
    kp_type = "diff" # every knickpoint below this will be erased
    FigFormat = 'png'
    #knickpoint_plots_for_basins(DataDirectory,csv_name, kp_type)
    #get_data_column_from_csv(DataDirectory,csv_name,kp_type,column_name="latitude")
    knickpoint_plotter(kp_type=kp_type,FigFormat=FigFormat, processed = True, pd_name = dfp)
