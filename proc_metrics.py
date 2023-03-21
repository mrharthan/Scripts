# ---------------------------------------------------------------------------
# proc_metrics.py
# Modified on: 2022-12-29
# Description: Wrapper execution file for ETL to the METRICS database
# Processing Spatial Reference:  EPSG:3857 -- WGS84 Web Mercator (Auxiliary Sphere)
# Author: J. S. Pedigo --- \\SSCI594\CommuteGeolocator\Scripts
# ---------------------------------------------------------------------------

import os
import sys
import arcpy

#from typing import List, Union
import cgc_logging
import proc_module_a
import proc_module_b
import proc_module_c
import proc_module_d
import proc_module_e
import proc_module_f
import proc_module_g

conn_data_path = r"D:\Projects\CGCLocator"  ### r"G:\SSCI594\CommuteGeolocator"
etl_dir_nm = "Scripts"
data_dir_nm = "Data"
local_dir_nm = "Local"
logs_dir_nm = "Logs"
logs_file_nm = "cgc_data_log.txt"
template_gdb_nm = "CGCTemplates.gdb"        ## Table and Layer Templates
workspace_gdb_nm = "CommuteGeolocator.gdb"  ## Source Table and Layer Imports
staging_gdb_nm = "MetricsStaging.gdb"       ## All Reference and Analysis Project Layers
cgc_auto_gdb_nm = "CGCAutoNet.gdb"          ## Local AutoNetwork ND and Supplementary Auto Layers/Tables
cgc_transit_gdb_nm = "CGCTransitNet.gdb"    ## Local TransitNetwork ND and Supplementary Transit Layers/Tables

cgcsrcdata = r"D:\Projects\CGCLocator\Data\Connections\cgcSDEConnections\GISDW_DEV_SANDBOX_STAGING_DATAOWNER.sde"   ## All StreetLight and GTFS Downloads -- SSI Server: r"G:\SSCI594\CommuteGeolocator\Data\Connections\SSI\SRCDATA.sde"
cgcmetrics = r"D:\Projects\CGCLocator\Data\Connections\cgcSDEConnections\GISDW_DEV_SANDBOX_STATIC_DATAOWNER.sde"   ## Remote ND Data Store and Supplementary Auto Layers/Tables -- SSI Server:  r"G:\SSCI594\CommuteGeolocator\Data\Connections\SSI\METRICS.sde"

# ListGroups = []

# # Script arguments
# Input_Network = arcpy.GetParameterAsText(0)
# if Input_Network == '#' or not Input_Network:
#         ListGroups.append('#')  # provide a default value if unspecified


def run_cgc_data_etl():

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

        ## Auto Local FGDB Reset
        log_message = "Refreshing Local Network File Geodatabases ..."
        logger.info(log_message)

        # Process: Delete Net Model Workspace
        log_message = "Deleting: {}".format(cgc_auto_gdb)
        logger.info(log_message)

        arcpy.Delete_management(cgc_auto_gdb, "Workspace")

        # Process: Rebuild Net Model Workspace
        log_message = "Recreating local file GDB: {}".format(cgc_auto_gdb)
        logger.info(log_message)

        arcpy.CreateFileGDB_management(conn_data_path, cgc_auto_gdb_nm)

        ## Transit Local FGDB Reset
        log_message = "Deleting: {}".format(cgc_transit_gdb)
        logger.info(log_message)

        arcpy.Delete_management(cgc_transit_gdb, "Workspace")

        # Process: Rebuild
        log_message = "Creating local file GDB: {}".format(cgc_transit_gdb)
        logger.info(log_message)

        arcpy.CreateFileGDB_management(conn_data_path, cgc_transit_gdb_nm)

        log_message = "Local Network FGDB Refresh is complete"
        logger.info(log_message)

        localAutoFD = str(os.path.join(cgc_auto_gdb, "AutoNetwork"))  # Local home for auto network dataset in WGS 1984 Web Mercator Auxillary Sphere

        log_message = "Refreshing the Automobile Network Feature Dataset ..."
        logger.info(log_message)

        if arcpy.Exists(localAutoFD):
                arcpy.Delete_management(localAutoFD, "FeatureDataset")

        # (RE)CREATE THE AUTO FEATURE DATASET
        arcpy.CreateFeatureDataset_management(out_dataset_path=cgc_auto_gdb, out_name="AutoNetwork", spatial_reference="GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision")

        log_message = "New {} Feature Dataset Ready ...".format(localAutoFD)
        logger.info(log_message)

        localTransitFD = str(os.path.join(cgc_transit_gdb, "TransitNetwork"))  # Local home for transit network dataset in WGS 1984 Web Mercator Auxillary Sphere

        log_message = "Refreshing the Transit Network Feature Dataset ..."
        logger.info(log_message)

        if arcpy.Exists(localTransitFD):
                arcpy.Delete_management(localTransitFD, "FeatureDataset")

        # (RE)CREATE THE TRANSIT FEATURE DATASET
        arcpy.CreateFeatureDataset_management(out_dataset_path=cgc_transit_gdb, out_name="TransitNetwork", spatial_reference="GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision")

        log_message = "New {} Feature Dataset Ready ...".format(localTransitFD)
        logger.info(log_message)

        logger.info("*************************************************************************")
        logger.info("START CGC Source Data ETL PROCESS")

        try:
                log_message = "RUNNING ..."
                logger.info(log_message)

                result_a1 = proc_module_a.defineServiceArea(workspace_gdb, staging_gdb, data_dir, logger)
                logger.info(result_a1)

                result_a2 = proc_module_a.constructAutoTripTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_a2)

                result_a3 = proc_module_a.constructAutoTravellerTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_a3)

                result_a4 = proc_module_a.generateTransferStreets(staging_gdb, localAutoFD, localTransitFD, logger)
                logger.info(result_a4)

                result_b1 = proc_module_b.constructBusTripTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_b1)

                result_b2 = proc_module_b.constructBusTravellerTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_b2)

                result_c1 = proc_module_c.constructPedTripTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_c1)

                result_c2 = proc_module_c.constructPedTravellerTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_c2)

                result_d1 = proc_module_d.constructRailTripTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_d1)

                result_d2 = proc_module_d.constructRailTravellerTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
                logger.info(result_d2)

                result_e1 = proc_module_e.constructAutoNetwork(staging_gdb, workspace_gdb, localAutoFD, logger)
                logger.info(result_e1)

                result_e2 = proc_module_e.segmentPedestrianPaths(staging_gdb, workspace_gdb, template_gdb, logger)
                logger.info(result_e2)

                result_e3 = proc_module_e.segmentBusRoutes(cgcsrcdata, staging_gdb, workspace_gdb, template_gdb, logger)
                logger.info(result_e3)

                result_e4 = proc_module_e.segmentRailLines(cgcsrcdata, staging_gdb, workspace_gdb, template_gdb, logger)
                logger.info(result_e4)

                result_e5 = proc_module_e.loadTransitNetworkInputs(workspace_gdb, localTransitFD, logger)
                logger.info(result_e5)

                result_f1 = proc_module_f.linearizeAutoTripSpeed(workspace_gdb, logger)
                logger.info(result_f1)

                result_f2 = proc_module_f.linearizeAutoTravellerIncome(workspace_gdb, logger)
                logger.info(result_f2)

                result_f3 = proc_module_f.linearizePedestrianTripSpeed(workspace_gdb, logger)
                logger.info(result_f3)

                result_f4 = proc_module_f.linearizePedestrianIncome(workspace_gdb, logger)
                logger.info(result_f4)

                result_f5 = proc_module_f.linearizeBusTripSpeed(workspace_gdb, logger)
                logger.info(result_f5)

                result_f6 = proc_module_f.linearizeBusTravellerIncome(workspace_gdb, logger)
                logger.info(result_f6)

                result_f7 = proc_module_f.linearizeRailTripSpeed(workspace_gdb, logger)
                logger.info(result_f7)

                result_f8 = proc_module_f.linearizeRailTravellerIncome(workspace_gdb, logger)
                logger.info(result_f8)

                result_g1 = proc_module_g.loadAutoMetrics(workspace_gdb, localAutoFD, logger)
                logger.info(result_g1)

                result_g2 = proc_module_g.loadTransitMetrics(workspace_gdb, localTransitFD, logger)
                logger.info(result_g2)

                result_g3 = proc_module_g.create_base_relclass(cgc_transit_gdb, localTransitFD, logger)
                logger.info(result_g3)

        except Exception as e:
                error_message1 = "Error in Asset Data ETL process!"
                error_message2 = str(e)
                logger.exception(error_message1 + "\n" + error_message2)
        logger.info("END CGC Source Data ETL PROCESS")
        logger.info("*************************************************************************")


if __name__ == '__main__':
        run_cgc_data_etl()



