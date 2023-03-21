# ---------------------------------------------------------------------------
# proc_module_g.py -- load and format metrics; build relationship classes
# for NAD 83 GCS
# Author: J. S. Pedigo
# ---------------------------------------------------------------------------
import os
import sys
import arcpy
import math
import string
import cgc_logging

#----------------------------------------------------------------------

def loadAutoMetrics(wkspcdata_gdb, auto_fd_gdb, logger):

    log_message = "%%%%%%% Process G1 - Load Auto Metrics to the Local Auto Feature Dataset %%%%%%%"
    logger.info(log_message)

    auto_metrics_trip = os.path.join(wkspcdata_gdb, "ProjAutoTripMetrics")
    auto_metrics_trav = os.path.join(wkspcdata_gdb, "ProjAutoTravMetrics")
    auto_trip_metrics = auto_fd_gdb + "\\AutoTripMetrics"
    auto_trav_metrics = auto_fd_gdb + "\\AutoTravMetrics"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    log_message = "Writing Auto Trip Speed in GCS NAD83 to {}".format(auto_trip_metrics)
    logger.info(log_message)

    if arcpy.Exists(auto_trip_metrics):
        arcpy.Delete_management(auto_trip_metrics, "FeatureClass")

    # Process: Project (8)
    arcpy.Project_management(auto_metrics_trip, auto_trip_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Auto Traveler Income in GCS NAD83 to {}".format(auto_trav_metrics)
    logger.info(log_message)

    if arcpy.Exists(auto_trav_metrics):
        arcpy.Delete_management(auto_trav_metrics, "FeatureClass")

    # Process: Project (9)
    arcpy.Project_management(auto_metrics_trav, auto_trav_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    return "%%%%%%% Process G1 - Auto Metrics - Projection to Local FGDB Complete %%%%%%%"


def loadTransitMetrics(wkspcdata_gdb, transit_fd_gdb, logger):

    log_message = "%%%%%%% Process G2 - Load All Transit Cost Metrics to the Local Transit Feature Dataset %%%%%%%"
    logger.info(log_message)

    bus_metrics_trip = os.path.join(wkspcdata_gdb, "ProjBusTripMetrics")
    bus_metrics_trav = os.path.join(wkspcdata_gdb, "ProjBusTravellerMetrics")
    bus_trip_metrics = transit_fd_gdb + "\\BusTripMetrics"
    bus_trav_metrics = transit_fd_gdb + "\\BusTravellerMetrics"
    ped_metrics_trip = os.path.join(wkspcdata_gdb, "ProjPedTripMetrics")
    ped_metrics_trav = os.path.join(wkspcdata_gdb, "ProjPedTravellerMetrics")
    ped_trip_metrics = transit_fd_gdb + "\\PedTripMetrics"
    ped_trav_metrics = transit_fd_gdb + "\\PedTravellerMetrics"
    rail_metrics_trip = os.path.join(wkspcdata_gdb, "ProjRailTripMetrics")
    rail_metrics_trav = os.path.join(wkspcdata_gdb, "ProjRailTravellerMetrics")
    rail_trip_metrics = transit_fd_gdb + "\\RailTripMetrics"
    rail_trav_metrics = transit_fd_gdb + "\\RailTravellerMetrics"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    log_message = "Writing Bus Trip Speed in GCS NAD83 to {}".format(bus_trip_metrics)
    logger.info(log_message)

    if arcpy.Exists(bus_trip_metrics):
        arcpy.Delete_management(bus_trip_metrics, "FeatureClass")

    # Process: Project (10)
    arcpy.Project_management(bus_metrics_trip, bus_trip_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Bus Traveler Income in GCS NAD83 to {}".format(bus_trav_metrics)
    logger.info(log_message)

    if arcpy.Exists(bus_trav_metrics):
        arcpy.Delete_management(bus_trav_metrics, "FeatureClass")

    # Process: Project (11)
    arcpy.Project_management(bus_metrics_trav, bus_trav_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Pedestrian Trip Speed in GCS NAD83 to {}".format(ped_trip_metrics)
    logger.info(log_message)

    if arcpy.Exists(ped_trip_metrics):
        arcpy.Delete_management(ped_trip_metrics, "FeatureClass")

    # Process: Project (12)
    arcpy.Project_management(ped_metrics_trip, ped_trip_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Pedestrian Traveler Income in GCS NAD83 to {}".format(ped_trav_metrics)
    logger.info(log_message)

    if arcpy.Exists(ped_trav_metrics):
        arcpy.Delete_management(ped_trav_metrics, "FeatureClass")

    # Process: Project (13)
    arcpy.Project_management(ped_metrics_trav, ped_trav_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Rail Trip Speed in GCS NAD83 to {}".format(rail_trip_metrics)
    logger.info(log_message)

    if arcpy.Exists(rail_trip_metrics):
        arcpy.Delete_management(rail_trip_metrics, "FeatureClass")

    # Process: Project (14)
    arcpy.Project_management(rail_metrics_trip, rail_trip_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Rail Traveler Income in GCS NAD83 to {}".format(rail_trav_metrics)
    logger.info(log_message)

    if arcpy.Exists(rail_trav_metrics):
        arcpy.Delete_management(rail_trav_metrics, "FeatureClass")

    # Process: Project (15)
    arcpy.Project_management(rail_metrics_trav, rail_trav_metrics,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    return "%%%%%%% Process G2 - Multimodal Transit Metrics - Projection to Local FGDB Complete %%%%%%%"


def create_base_relclass(transit_gdb, transit_fd_gdb, logger):

    log_message = "%%%%%%% Process G3 - Build Relationship Classes for Transit %%%%%%%"
    logger.info(log_message)

    bus_taz_stops = os.path.join(transit_fd_gdb, "Bus_TAZ_Stops")
    bus_metrics_trip = os.path.join(transit_fd_gdb, "BusTripMetrics")
    bus_metrics_lkup_lyr = os.path.join(transit_gdb, "BusMetricLkUpLyr")
    bus_metrics_lkup_tbl = os.path.join(transit_gdb, "BusMetricLkUpTbl")
    bus_stop_to_route_ln = transit_fd_gdb + "\\bus_stop_to_route_ln"
    rail_taz_stations = os.path.join(transit_fd_gdb, "Rail_TAZ_Stations")
    rail_metrics_trip = os.path.join(transit_fd_gdb, "RailTripMetrics")
    rail_metrics_lkup_lyr = os.path.join(transit_gdb, "RailMetricLkUpLyr")
    rail_metrics_lkup_tbl = os.path.join(transit_gdb, "RailMetricLkUpTbl")
    rail_stop_to_route_ln = transit_fd_gdb + "\\rail_stop_to_route_ln"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = transit_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    log_message = "Creating Bus Speed Lookup STEP 1 - Spatial Join between Bus Stops and Bus Routes - Output: {}".format(bus_metrics_lkup_lyr)
    logger.info(log_message)

    if arcpy.Exists(bus_metrics_lkup_lyr):
        arcpy.Delete_management(bus_metrics_lkup_lyr, "FeatureClass")

    # Process: Spatial Join
    arcpy.SpatialJoin_analysis(bus_metrics_trip, bus_taz_stops, bus_metrics_lkup_lyr, "JOIN_ONE_TO_MANY", "KEEP_ALL", "MetricKey \"MetricKey\" true true false 250 Text 0 0 ,First,#," + bus_metrics_trip + ",MetricKey,-1,-1;GeoID \"GeoID\" true true false 30 Text 0 0 ,First,#," + bus_taz_stops + ",GeoID,-1,-1", "CLOSEST", "0.0005 DecimalDegrees", "")

    log_message = "Creating Bus Speed Lookup STEP 2 - Table Conversion - Output: {}".format(bus_metrics_lkup_tbl)
    logger.info(log_message)

    if arcpy.Exists(bus_metrics_lkup_tbl):
        arcpy.Delete_management(bus_metrics_lkup_tbl, "Table")

    # Process: Table to Table
    arcpy.TableToTable_conversion(bus_metrics_lkup_lyr, transit_gdb, "BusMetricLkUpTbl", "GeoID IS NOT NULL", "MetricKey \"MetricKey\" true true false 250 Text 0 0 ,First,#," + bus_metrics_lkup_lyr + ",MetricKey,-1,-1;GeoID \"GeoID\" true true false 30 Text 0 0 ,First,#," + bus_metrics_lkup_lyr + ",GeoID,-1,-1", "")

    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Creating Rail Speed Lookup STEP 1 - Spatial Join between Rail Stations and Rail Routes - Output: {}".format(rail_metrics_lkup_lyr)
    logger.info(log_message)

    if arcpy.Exists(rail_metrics_lkup_lyr):
        arcpy.Delete_management(rail_metrics_lkup_lyr, "FeatureClass")

    # Process: Spatial Join (2)
    arcpy.SpatialJoin_analysis(rail_metrics_trip, rail_taz_stations, rail_metrics_lkup_lyr, "JOIN_ONE_TO_MANY", "KEEP_ALL", "MetricKey \"MetricKey\" true true false 50 Text 0 0 ,First,#," + rail_metrics_trip + ",MetricKey,-1,-1;GeoID \"GeoID\" true true false 30 Text 0 0 ,First,#," + rail_taz_stations + ",GeoID,-1,-1", "INTERSECT", "0.0005 DecimalDegrees", "")

    log_message = "Creating Bus Speed Lookup STEP 2 - Table Conversion - Output: {}".format(rail_metrics_lkup_tbl)
    logger.info(log_message)

    if arcpy.Exists(rail_metrics_lkup_tbl):
        arcpy.Delete_management(rail_metrics_lkup_tbl, "Table")

    # Process: Table to Table (2)
    arcpy.TableToTable_conversion(rail_metrics_lkup_lyr, transit_gdb, "RailMetricLkUpTbl", "GeoID IS NOT NULL", "MetricKey \"MetricKey\" true true false 50 Text 0 0 ,First,#," + rail_metrics_lkup_lyr + ",MetricKey,-1,-1;GeoID \"GeoID\" true true false 30 Text 0 0 ,First,#," + rail_metrics_lkup_lyr + ",GeoID,-1,-1", "")

    if arcpy.Exists(bus_stop_to_route_ln):
        arcpy.Delete_management(bus_stop_to_route_ln, "RelationshipClass")

    log_message = "Building Bus Stop to Bus Route Relation: {}".format(bus_stop_to_route_ln)
    logger.info(log_message)

    # Process: Table To Relationship Class
    arcpy.TableToRelationshipClass_management(bus_metrics_trip, bus_taz_stops,
                                              bus_stop_to_route_ln, "SIMPLE", "to_bus_pnt",
                                              "to_bus_ln", "BOTH", "MANY_TO_MANY", bus_metrics_lkup_tbl,
                                              "GeoID;MetricKey", "MetricKey", "MetricKey", "GeoID", "GeoID")

    if arcpy.Exists(rail_stop_to_route_ln):
        arcpy.Delete_management(rail_stop_to_route_ln, "RelationshipClass")

    log_message = "Building Rail Stop to Rail Route Relation: {}".format(rail_stop_to_route_ln)
    logger.info(log_message)

    # Process: Table To Relationship Class
    arcpy.TableToRelationshipClass_management(rail_metrics_trip, rail_taz_stations,
                                              rail_stop_to_route_ln, "SIMPLE", "to_rail_pnt",
                                              "to_rail_ln", "BOTH", "MANY_TO_MANY", rail_metrics_lkup_tbl,
                                              "GeoID;MetricKey", "MetricKey", "MetricKey", "GeoID", "GeoID")

    return "%%%%%%% Process G3 - Relationship Class Build for Transit Complete %%%%%%%"


if __name__ == '__main__':
    conn_data_path = r"G:\SSCI594\CommuteGeolocator"
    etl_dir_nm = "Scripts"
    data_dir_nm = "Data"
    local_dir_nm = "Local"
    logs_dir_nm = "Logs"
    logs_file_nm = "cgc_data_log.txt"
    template_gdb_nm = "cgctemplates.gdb"
    workspace_gdb_nm = "CommuteGeolocator.gdb"
    staging_gdb_nm = "MetricsStaging.gdb"
    cgc_auto_gdb_nm = "CGCAutoNet.gdb"
    cgc_transit_gdb_nm = "CGCTransitNet.gdb"

    cgcsrcdata = r"D:\Projects\CGCLocator\Data\Connections\cgcSDEConnections\GISDW_DEV_SANDBOX_STAGING_DATAOWNER.sde"  ## All StreetLight and GTFS Downloads -- SSI Server: r"G:\SSCI594\CommuteGeolocator\Data\Connections\SSI\SRCDATA.sde"
    cgcmetrics = r"D:\Projects\CGCLocator\Data\Connections\cgcSDEConnections\GISDW_DEV_SANDBOX_STATIC_DATAOWNER.sde"  ## Remote ND Data Store and Supplementary Auto Layers/Tables -- SSI Server:  r"G:\SSCI594\CommuteGeolocator\Data\Connections\SSI\METRICS.sde"

    # Set up logging
    logs_dir = os.path.join(conn_data_path, logs_dir_nm)
    logs_file = os.path.join(logs_dir, logs_file_nm)
    logger = cgc_logging.setup_logging(logs_file)

    # Local GDB paths
    local_dir = os.path.join(conn_data_path, local_dir_nm)
    template_gdb = os.path.join(local_dir, template_gdb_nm)
    data_dir = os.path.join(conn_data_path, data_dir_nm)
    staging_gdb = os.path.join(conn_data_path, staging_gdb_nm)
    workspace_gdb = os.path.join(conn_data_path, workspace_gdb_nm)
    cgc_auto_gdb = os.path.join(conn_data_path, cgc_auto_gdb_nm)
    cgc_transit_gdb = os.path.join(conn_data_path, cgc_transit_gdb_nm)

    arcpy.env.scratchWorkspace = workspace_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace
    arcpy.env.overwriteOutput = True

    localAutoFD = str(os.path.join(cgc_auto_gdb, "AutoNetwork"))  # Local home for auto network dataset in WGS 1984 Web Mercator Auxillary Sphere
    localTransitFD = str(os.path.join(cgc_transit_gdb, "TransitNetwork"))  # Local home for transit network dataset in WGS 1984 Web Mercator Auxillary Sphere

    result_g1 = loadAutoMetrics(workspace_gdb, localAutoFD, logger)
    logger.info(result_g1)

    result_g2 = loadTransitMetrics(workspace_gdb, localTransitFD, logger)
    logger.info(result_g2)

    result_g3 = create_base_relclass(cgc_transit_gdb, localTransitFD, logger)
    logger.info(result_g3)
