# ---------------------------------------------------------------------------
# proc_module_b.py
# Author: J. S. Pedigo
# ---------------------------------------------------------------------------
import math
import os
import sys
import arcpy
import math
import string
import cgc_logging

#----------------------------------------------------------------------

def constructBusTripTbl(src_data, wkspace_gdb, temp_data, logger):

    log_message = "%%%%%%% Process B1 - Calculate Total Probability of Avg. Bus Trip Speed per Zone %%%%%%%"
    logger.info(log_message)

    # Templates -- BUS
    seasonal_bus_trip_tbl = os.path.join(temp_data, "SeasonalBusTrip")
    temp_cgc_bus_tbl = os.path.join(temp_data, "CGCBusTripTemp")

    # Trip variables - BUS:
    srcdata_bus_trip_zone1 = os.path.join(src_data, "WDCZone1BusTrip")
    spring_bus_trip_zone1 = wkspace_gdb + "\\SpringWDCZone1BusTrip"
    fall_bus_trip_zone1 = wkspace_gdb + "\\FallWDCZone1BusTrip"
    srcdata_bus_trip_zone2 = os.path.join(src_data, "WDCZone2BusTrip")
    spring_bus_trip_zone2 = wkspace_gdb + "\\SpringWDCZone2BusTrip"
    fall_bus_trip_zone2 = wkspace_gdb + "\\FallWDCZone2BusTrip"
    cgc_bus_trip = wkspace_gdb + "\\CGCBusTrip"  ## all combined avg. speed
    seasonBTblList = [spring_bus_trip_zone1, fall_bus_trip_zone1, spring_bus_trip_zone2, fall_bus_trip_zone2]

    log_message = "Checking for missing bus trip template ..."
    logger.info(log_message)

    if arcpy.Exists(seasonal_bus_trip_tbl):
        pass
    else:
        log_message = "Seasonal Bus Trip Table is missing - Resetting now ..."
        logger.info(log_message)

        # Process: Table To Table (Table To Table) (conversion)
        arcpy.TableToTable_conversion(in_rows=srcdata_bus_trip_zone1, out_path=temp_data, out_name="SeasonalBusTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 18,First,#," + srcdata_bus_trip_zone1 + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + srcdata_bus_trip_zone1 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_trip_zone1 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + srcdata_bus_trip_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_trip_zone1 + ",Trip_Speed_20__mph__percent_,-1,-1", config_keyword="")

        # Process: Delete Rows
        arcpy.DeleteRows_management(in_rows=seasonal_bus_trip_tbl)

    log_message = "Bus Trip template table ready"
    logger.info(log_message)
    ## Integrate the Bus Traffic Metrics for Insertion to the Transit Network Dataset
    log_message = "Begin Bus Trip Data Integration - Total Probability of Zonal Average Speed"
    logger.info(log_message)

    # # ZONE 1 Bus Trip Seasonal Split
    result = arcpy.GetCount_management(srcdata_bus_trip_zone1)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r1Count = int(result[0])/2

    log_message = "{} record count in {}".format(r1Count * 2, srcdata_bus_trip_zone1)
    logger.info(log_message)

    log_message = "Resetting Spring Bus Trip Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_bus_trip_zone1):
        arcpy.Delete_management(spring_bus_trip_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_trip_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone1BusTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_20__mph__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Bus Trip Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_bus_trip_zone1):
        arcpy.Delete_management(fall_bus_trip_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_trip_tbl, out_path=wkspace_gdb, out_name="FallWDCZone1BusTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_20__mph__percent_,-1,-1", config_keyword="")

    # # ZONE 2 Bus Trip Seasonal Split
    result = arcpy.GetCount_management(srcdata_bus_trip_zone2)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r2Count = int(result[0]) / 2

    log_message = "{} record count in {}".format(r2Count * 2, srcdata_bus_trip_zone2)
    logger.info(log_message)

    log_message = "Resetting Spring Bus Trip Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_bus_trip_zone2):
        arcpy.Delete_management(spring_bus_trip_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_trip_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone2BusTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_20__mph__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Bus Trip Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_bus_trip_zone2):
        arcpy.Delete_management(fall_bus_trip_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_trip_tbl, out_path=wkspace_gdb, out_name="FallWDCZone2BusTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_trip_tbl + ",Trip_Speed_20__mph__percent_,-1,-1", config_keyword="")

    edit = arcpy.da.Editor(wkspace_gdb)

    log_message = "Beginning edit session in {}".format(wkspace_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert - 50/50 split from source table to isolate seasonal data
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()
    # ZONE 1 Record Insertion *****************************************************************************************
    log_message = "Populating Bus Zone 1 Speed Data in Fall and Spring tables ..."
    logger.info(log_message)

    s1 = 1
    s2 = 0
    objectID = 0
    ndxS1Tbl = arcpy.da.InsertCursor(spring_bus_trip_zone1, ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name", "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction", "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL", "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_", "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_", "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_", "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_", "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_", "Trip_Speed_20__mph__percent_"])
    ndxS2Tbl = arcpy.da.InsertCursor(fall_bus_trip_zone1, ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name", "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction", "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL", "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_", "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_", "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_", "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_", "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_", "Trip_Speed_20__mph__percent_"])
    ndxTrip1Tbl = arcpy.da.SearchCursor(srcdata_bus_trip_zone1, ["Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name", "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction", "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL", "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_", "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_", "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_", "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_", "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_", "Trip_Speed_20__mph__percent_"], None, None, "False", (None, None))

    for t1Row in ndxTrip1Tbl:
        modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8, zoneSpd9, zoneSpd10, zoneSpd11 = t1Row[0], t1Row[1], t1Row[2], t1Row[3], t1Row[4], t1Row[5], t1Row[6], t1Row[7], t1Row[8], t1Row[9], t1Row[10], t1Row[11], t1Row[12], t1Row[13], t1Row[14], t1Row[15], t1Row[16], t1Row[17], t1Row[18], t1Row[19], t1Row[20]
        if (zoneNm == None):
            pass
        elif (s1 < r1Count + 1):
            objectID = s1
            ndxS1Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8, zoneSpd9, zoneSpd10, zoneSpd11])
        else:
            objectID = s1
            ndxS2Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8, zoneSpd9, zoneSpd10, zoneSpd11])
        s1 += 1
    del t1Row
    del ndxTrip1Tbl

    s2 = (s1 - 1)/2

    log_message = "Applied {} new records to {}".format(s2, spring_bus_trip_zone1)
    logger.info(log_message)

    del ndxS1Tbl

    log_message = "Applied {} new records to {}".format(s2, fall_bus_trip_zone1)
    logger.info(log_message)

    del ndxS2Tbl
    # ******************************************************************************************************************
    # ZONE 2 Record Insertion *****************************************************************************************
    log_message = "Populating Bus Zone 2 Speed Data in Fall and Spring tables ..."
    logger.info(log_message)

    s1 = 1
    s2 = 0
    objectID = 0
    ndxS1Tbl = arcpy.da.InsertCursor(spring_bus_trip_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_",
                                      "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_",
                                      "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_",
                                      "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_",
                                      "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_",
                                      "Trip_Speed_20__mph__percent_"])

    ndxS2Tbl = arcpy.da.InsertCursor(fall_bus_trip_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_",
                                      "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_",
                                      "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_",
                                      "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_",
                                      "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_",
                                      "Trip_Speed_20__mph__percent_"])
    ndxTrip2Tbl = arcpy.da.SearchCursor(srcdata_bus_trip_zone2,
                                        ["Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                          "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                          "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                          "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_",
                                          "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_",
                                          "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_",
                                          "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_",
                                          "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_",
                                          "Trip_Speed_20__mph__percent_"], None, None,
                                        "False", (None, None))

    for t2Row in ndxTrip2Tbl:
        modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8, zoneSpd9, zoneSpd10, zoneSpd11 = \
        t2Row[0], t2Row[1], t2Row[2], t2Row[3], t2Row[4], t2Row[5], t2Row[6], t2Row[7], t2Row[8], t2Row[9], t2Row[10], t2Row[11], t2Row[12], t2Row[13], t2Row[14], t2Row[15], t2Row[16], t2Row[17], t2Row[18], t2Row[19], t2Row[20]
        if (zoneNm == None):
            pass
        elif (s1 < r2Count + 1):
            objectID = s1
            ndxS1Tbl.insertRow(
                [objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8, zoneSpd9, zoneSpd10, zoneSpd11])
        else:
            objectID = s1
            ndxS2Tbl.insertRow(
                [objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8, zoneSpd9, zoneSpd10, zoneSpd11])
        s1 += 1
    del t2Row
    del ndxTrip2Tbl

    s2 = (s1 - 1) / 2

    log_message = "Applied {} new records to {}".format(s2, spring_bus_trip_zone2)
    logger.info(log_message)

    del ndxS1Tbl

    log_message = "Applied {} new records to {}".format(s2, fall_bus_trip_zone2)
    logger.info(log_message)

    del ndxS2Tbl
    # ******************************************************************************************************************

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(wkspace_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    log_message = "Removing rows of all-day avg. speeds in all seasonal traffic tables"
    logger.info(log_message)

    for xTbl in seasonBTblList:
        tripCount = arcpy.GetCount_management(xTbl)
        xCount = int(tripCount[0])

        log_message = "Filtering {}".format(xTbl)
        logger.info(log_message)

        oid = None
        zName = None
        dType = None
        x = 0
        xRecNDX = arcpy.da.UpdateCursor(xTbl, ["OBJECTID", "Zone_Name", "Day_Type"], None, None, "False", (None, None))
        for xRow in xRecNDX:
            oid, zName, dType = xRow[0], xRow[1], xRow[2]
            if (dType == '0: All Days (M-Su)'):
                x += 1
                xRecNDX.deleteRow()
            else:
                pass

        del xRow
        del xRecNDX

        log_message = "Cleared {} all-day average records of {} in {}".format(str(x), xCount, xTbl)
        logger.info(log_message)

        # Process: Add Field
        arcpy.AddField_management(in_table=xTbl, field_name="TripKey", field_type="TEXT",
                                  field_precision=None, field_scale=None, field_length=None, field_alias="TripKey",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        log_message = "Adding/Calculating Unique Trip Key field ..."
        logger.info(log_message)

        # Process: Calculate Field
        arcpy.CalculateField_management(in_table=xTbl, field="TripKey", expression="calcTripKey(!Zone_Name!, !Day_Type!, !Day_Part!)", expression_type="PYTHON_9.3", code_block="""def calcTripKey(zonenm, daytype, daypart):
            dptVal = \"\"
            dtStr = str(daytype)
            dpStr = str(daypart)
            zStr = str(int(zonenm))
            dtCode = dtStr[0:1]
            dpCode = dpStr[0:1]
            dptVal = zStr + \"-\" + dtCode + dpCode
            return dptVal""")

    log_message = "Joining Fall and Spring Zone 1 speed data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_bus_trip_zone1, in_field="TripKey",
                               join_table=fall_bus_trip_zone1, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                      "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_",
                                      "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_",
                                      "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_",
                                      "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_",
                                      "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_",
                                      "Trip_Speed_20__mph__percent_"])

    log_message = "Joining Fall and Spring Zone 2 speed data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_bus_trip_zone2, in_field="TripKey",
                               join_table=fall_bus_trip_zone2, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                      "Trip_Speed_0_2_mph__percent_", "Trip_Speed_2_4_mph__percent_",
                                      "Trip_Speed_4_6_mph__percent_", "Trip_Speed_6_8_mph__percent_",
                                      "Trip_Speed_8_10_mph__percent_", "Trip_Speed_10_12_mph__percent_",
                                      "Trip_Speed_12_14_mph__percent_", "Trip_Speed_14_16_mph__percent_",
                                      "Trip_Speed_16_18_mph__percent_", "Trip_Speed_18_20_mph__percent_",
                                      "Trip_Speed_20__mph__percent_"])

    log_message = "Resetting the All-Zone Bus Trip output table"
    logger.info(log_message)

    if arcpy.Exists(cgc_bus_trip):
        arcpy.Delete_management(cgc_bus_trip, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=temp_cgc_bus_tbl, out_path=wkspace_gdb, out_name="CGCBusTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_bus_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_20__mph__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + temp_cgc_bus_tbl + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Index1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_bus_tbl + ",Average_Daily_Zone_Traffic__StL_Index1,-1,-1;Trip_Speed_0_2_mph__percent1 \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_0_2_mph__percent1,-1,-1;Trip_Speed_2_4_mph__percent1 \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_2_4_mph__percent1,-1,-1;Trip_Speed_4_6_mph__percent1 \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_4_6_mph__percent1,-1,-1;Trip_Speed_6_8_mph__percent1 \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_6_8_mph__percent1,-1,-1;Trip_Speed_8_10_mph__percent1 \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_8_10_mph__percent1,-1,-1;Trip_Speed_10_12_mph__percent1 \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_10_12_mph__percent1,-1,-1;Trip_Speed_12_14_mph__percent1 \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_12_14_mph__percent1,-1,-1;Trip_Speed_14_16_mph__percent1 \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_14_16_mph__percent1,-1,-1;Trip_Speed_16_18_mph__percent1 \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_16_18_mph__percent1,-1,-1;Trip_Speed_18_20_mph__percent1 \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_18_20_mph__percent1,-1,-1;Trip_Speed_20__mph__percent1 \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_tbl + ",Trip_Speed_20__mph__percent1,-1,-1", config_keyword="")

    log_message = "Combining Zone 1 and Zone 2 trip speed data in {}".format(cgc_bus_trip)
    logger.info(log_message)

    # Process: Append
    arcpy.Append_management(inputs=[spring_bus_trip_zone1, spring_bus_trip_zone2], target=cgc_bus_trip, schema_type="NO_TEST", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Mode_of_Travel,0,2147483647," + spring_bus_trip_zone2 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Intersection_Type,0,2147483647," + spring_bus_trip_zone2 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Zone_ID,-1,-1," + spring_bus_trip_zone2 + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Zone_Name,-1,-1," + spring_bus_trip_zone2 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Zone_Is_Pass_Through,0,2147483647," + spring_bus_trip_zone2 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Zone_Direction__degrees_,0,2147483647," + spring_bus_trip_zone2 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Zone_is_Bi_Direction,0,2147483647," + spring_bus_trip_zone2 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Day_Type,0,2147483647," + spring_bus_trip_zone2 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + spring_bus_trip_zone1 + ",Day_Part,0,2147483647," + spring_bus_trip_zone2 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_bus_trip_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1," + spring_bus_trip_zone2 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_2_mph__percent_ \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_0_2_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_0_2_mph__percent_,-1,-1;Trip_Speed_2_4_mph__percent_ \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_2_4_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_2_4_mph__percent_,-1,-1;Trip_Speed_4_6_mph__percent_ \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_4_6_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_4_6_mph__percent_,-1,-1;Trip_Speed_6_8_mph__percent_ \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_6_8_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_6_8_mph__percent_,-1,-1;Trip_Speed_8_10_mph__percent_ \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_8_10_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_8_10_mph__percent_,-1,-1;Trip_Speed_10_12_mph__percent_ \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_10_12_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_10_12_mph__percent_,-1,-1;Trip_Speed_12_14_mph__percent_ \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_12_14_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_12_14_mph__percent_,-1,-1;Trip_Speed_14_16_mph__percent_ \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_14_16_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_14_16_mph__percent_,-1,-1;Trip_Speed_16_18_mph__percent_ \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_16_18_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_16_18_mph__percent_,-1,-1;Trip_Speed_18_20_mph__percent_ \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_18_20_mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_18_20_mph__percent_,-1,-1;Trip_Speed_20__mph__percent_ \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_20__mph__percent_,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_20__mph__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + spring_bus_trip_zone1 + ",TripKey,0,255," + spring_bus_trip_zone2 + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Index1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_bus_trip_zone1 + ",Average_Daily_Zone_Traffic__StL_Index1,-1,-1," + spring_bus_trip_zone2 + ",Average_Daily_Zone_Traffic__StL_Index1,-1,-1;Trip_Speed_0_2_mph__percent1 \"Trip_Speed_0_2_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_0_2_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_0_2_mph__percent1,-1,-1;Trip_Speed_2_4_mph__percent1 \"Trip_Speed_2_4_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_2_4_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_2_4_mph__percent1,-1,-1;Trip_Speed_4_6_mph__percent1 \"Trip_Speed_4_6_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_4_6_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_4_6_mph__percent1,-1,-1;Trip_Speed_6_8_mph__percent1 \"Trip_Speed_6_8_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_6_8_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_6_8_mph__percent1,-1,-1;Trip_Speed_8_10_mph__percent1 \"Trip_Speed_8_10_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_8_10_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_8_10_mph__percent1,-1,-1;Trip_Speed_10_12_mph__percent1 \"Trip_Speed_10_12_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_10_12_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_10_12_mph__percent1,-1,-1;Trip_Speed_12_14_mph__percent1 \"Trip_Speed_12_14_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_12_14_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_12_14_mph__percent1,-1,-1;Trip_Speed_14_16_mph__percent1 \"Trip_Speed_14_16_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_14_16_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_14_16_mph__percent1,-1,-1;Trip_Speed_16_18_mph__percent1 \"Trip_Speed_16_18_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_16_18_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_16_18_mph__percent1,-1,-1;Trip_Speed_18_20_mph__percent1 \"Trip_Speed_18_20_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_18_20_mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_18_20_mph__percent1,-1,-1;Trip_Speed_20__mph__percent1 \"Trip_Speed_20__mph__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_trip_zone1 + ",Trip_Speed_20__mph__percent1,-1,-1," + spring_bus_trip_zone2 + ",Trip_Speed_20__mph__percent1,-1,-1", subtype="")

    log_message = "Average Bus Trip Speed table is ready for processing"
    logger.info(log_message)

    log_message = "Adding fields for calculating annual percent of speeds to {}".format(cgc_bus_trip)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_1mph_Pct", field_type="FLOAT", field_precision=5,
                                                field_scale=4, field_length=None, field_alias="Avg_1mph_Pct",
                                                field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_3mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_3mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_5mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_5mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_7mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_7mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_9mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_9mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_11mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_11mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_13mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_13mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_15mph_Pct", field_type="FLOAT",
                                                field_precision=5, field_scale=4, field_length=None,
                                                field_alias="Avg_15mph_Pct", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_17mph_Pct", field_type="FLOAT",
                                                field_precision=5, field_scale=4, field_length=None,
                                                field_alias="Avg_17mph_Pct", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_19mph_Pct", field_type="FLOAT",
                                                field_precision=5, field_scale=4, field_length=None,
                                                field_alias="Avg_19mph_Pct", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="Avg_21mph_Pct", field_type="FLOAT",
                                                field_precision=5, field_scale=4, field_length=None,
                                                field_alias="Avg_21mph_Pct", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Adding the Average Annual Bus Speed field (AADS) to {}".format(cgc_bus_trip)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_trip, field_name="AvgAnnualBusSpeed", field_type="DOUBLE",
                              field_precision=7, field_scale=3, field_length=None, field_alias="AvgAnnualBusSpeed",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Calculating Average Speeds by category..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_1mph_Pct",
        expression="calcAvg1MphPct(!Trip_Speed_0_2_mph__percent_!, !Trip_Speed_0_2_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg1MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 1
        elif pct2 == None:
            avgVal = pct1 * 1
        else:
            avgVal = ((pct1 + pct2) / 2) * 1
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_3mph_Pct",
        expression="calcAvg3MphPct(!Trip_Speed_2_4_mph__percent_!, !Trip_Speed_2_4_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg3MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 3
        elif pct2 == None:
            avgVal = pct1 * 3
        else:
            avgVal = ((pct1 + pct2) / 2) * 3
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_5mph_Pct",
        expression="calcAvg5MphPct(!Trip_Speed_4_6_mph__percent_!, !Trip_Speed_4_6_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg5MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 5
        elif pct2 == None:
            avgVal = pct1 * 5
        else:
            avgVal = ((pct1 + pct2) / 2) * 5
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_7mph_Pct",
        expression="calcAvg7MphPct(!Trip_Speed_6_8_mph__percent_!, !Trip_Speed_6_8_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg7MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 7
        elif pct2 == None:
            avgVal = pct1 * 7
        else:
            avgVal = ((pct1 + pct2) / 2) * 7
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_9mph_Pct",
        expression="calcAvg9MphPct(!Trip_Speed_8_10_mph__percent_!, !Trip_Speed_8_10_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg9MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 9
        elif pct2 == None:
            avgVal = pct1 * 9
        else:
            avgVal = ((pct1 + pct2) / 2) * 9
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_11mph_Pct",
        expression="calcAvg11MphPct(!Trip_Speed_10_12_mph__percent_!, !Trip_Speed_10_12_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg11MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 11
        elif pct2 == None:
            avgVal = pct1 * 11
        else:
            avgVal = ((pct1 + pct2) / 2) * 11
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_13mph_Pct",
        expression="calcAvg13MphPct(!Trip_Speed_12_14_mph__percent_!, !Trip_Speed_12_14_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg13MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 13
        elif pct2 == None:
            avgVal = pct1 * 13
        else:
            avgVal = ((pct1 + pct2) / 2) * 13
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_15mph_Pct",
        expression="calcAvg15MphPct(!Trip_Speed_14_16_mph__percent_!, !Trip_Speed_14_16_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg15MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 15
        elif pct2 == None:
            avgVal = pct1 * 15
        else:
            avgVal = ((pct1 + pct2) / 2) * 15
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_17mph_Pct",
        expression="calcAvg17MphPct(!Trip_Speed_16_18_mph__percent_!, !Trip_Speed_16_18_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg17MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 17
        elif pct2 == None:
            avgVal = pct1 * 17
        else:
            avgVal = ((pct1 + pct2) / 2) * 17
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_19mph_Pct",
        expression="calcAvg19MphPct(!Trip_Speed_18_20_mph__percent_!, !Trip_Speed_18_20_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg19MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 19
        elif pct2 == None:
            avgVal = pct1 * 19
        else:
            avgVal = ((pct1 + pct2) / 2) * 19
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="Avg_21mph_Pct",
        expression="calcAvg21MphPct(!Trip_Speed_20__mph__percent_!, !Trip_Speed_20__mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg21MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 21
        elif pct2 == None:
            avgVal = pct1 * 21
        else:
            avgVal = ((pct1 + pct2) / 2) * 21
        return avgVal""")

    log_message = "Adding all results for Average Annual Bus Speed in all Zones"
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_trip, field="AvgAnnualBusSpeed",
        expression="calcTotalAADS(!Avg_1mph_Pct!, !Avg_3mph_Pct!, !Avg_5mph_Pct!, !Avg_7mph_Pct!, !Avg_9mph_Pct!, !Avg_11mph_Pct!, !Avg_13mph_Pct!, !Avg_15mph_Pct!, !Avg_17mph_Pct!, !Avg_19mph_Pct!, !Avg_21mph_Pct!)",
        expression_type="PYTHON_9.3", code_block="""def calcTotalAADS(avg1, avg2, avg3, avg4, avg5, avg6, avg7, avg8, avg9, avg10, avg11):
        retNum = 0.0
        retNum = avg1 + avg2 + avg3 + avg4 + avg5 + avg6 + avg7 + avg8 + avg9 + avg10 + avg11
        return retNum""")

    log_message = "The calculation of Average Annual Bus Trip Speed is complete for all zones"
    logger.info(log_message)

    log_message = "Performing housekeeping tasks ..."
    logger.info(log_message)

    for zTbl in seasonBTblList:

        log_message = "Deleting {}". format(zTbl)
        logger.info(log_message)

        if arcpy.Exists(zTbl):
            arcpy.Delete_management(zTbl, "Table")

    return "%%%%%%% Process B1 Complete %%%%%%%"



def constructBusTravellerTbl(src_data, wkspace_gdb, temp_data, logger):

    log_message = "%%%%%%% Process B2 - Calculate Total Probability of Avg. Bus Traveller Income per Zone %%%%%%%"
    logger.info(log_message)

    # Templates
    seasonal_bus_traveller_tbl = os.path.join(temp_data, "SeasonalBusTraveller")
    temp_cgc_bus_traveller_tbl = os.path.join(temp_data, "CGCBusTravelTemp")

    # Traveller variables:
    srcdata_bus_traveller_zone1 = os.path.join(src_data, "WDCZone1BusTraveler")
    spring_bus_traveller_zone1 = wkspace_gdb + "\\SpringWDCZone1BusTraveller"
    fall_bus_traveller_zone1 = wkspace_gdb + "\\FallWDCZone1BusTraveller"
    srcdata_bus_traveller_zone2 = os.path.join(src_data, "WDCZone2BusTraveler")
    spring_bus_traveller_zone2 = wkspace_gdb + "\\SpringWDCZone2BusTraveller"
    fall_bus_traveller_zone2 = wkspace_gdb + "\\FallWDCZone2BusTraveller"
    cgc_bus_traveller = wkspace_gdb + "\\CGCBusTraveller"  ## all combined avg. income
    seasonBTblList = [spring_bus_traveller_zone1, fall_bus_traveller_zone1, spring_bus_traveller_zone2, fall_bus_traveller_zone2]

    log_message = "Checking for missing bus traveller template ..."
    logger.info(log_message)

    if arcpy.Exists(seasonal_bus_traveller_tbl):
        pass
    else:
        log_message = "Seasonal Bus Traveller Table is missing - Resetting now ..."
        logger.info(log_message)

        # Process: Table To Table
        arcpy.TableToTable_conversion(in_rows=srcdata_bus_traveller_zone1, out_path=temp_data, out_name="SeasonalBusTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 18,First,#," + srcdata_bus_traveller_zone1 + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + srcdata_bus_traveller_zone1 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + srcdata_bus_traveller_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_bus_traveller_zone1 + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

        # Process: Delete Rows
        arcpy.DeleteRows_management(in_rows=seasonal_bus_traveller_tbl)

    log_message = "Bus Traveller template table ready"
    logger.info(log_message)
    # Integrate the Bus Traffic Metrics for Insertion to the Automobile Network Dataset
    log_message = "Begin Bus Traveller Data Integration - Total Probability of Zonal Average Bus Traveller Income"
    logger.info(log_message)

    # ZONE 1 Bus Traveller Seasonal Split
    result = arcpy.GetCount_management(srcdata_bus_traveller_zone1)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r1Count = int(result[0]) / 2

    log_message = "{} record count in {}".format(r1Count * 2, srcdata_bus_traveller_zone1)
    logger.info(log_message)

    log_message = "Resetting Spring Bus Traveller Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_bus_traveller_zone1):
        arcpy.Delete_management(spring_bus_traveller_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_traveller_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone1BusTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Bus Traveller Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_bus_traveller_zone1):
        arcpy.Delete_management(fall_bus_traveller_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_traveller_tbl, out_path=wkspace_gdb, out_name="FallWDCZone1BusTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    # ZONE 2 Auto Trip Seasonal Split
    result = arcpy.GetCount_management(srcdata_bus_traveller_zone2)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r2Count = int(result[0]) / 2

    log_message = "{} record count in {}".format(r2Count * 2, srcdata_bus_traveller_zone2)
    logger.info(log_message)

    log_message = "Resetting Spring Bus Traveller Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_bus_traveller_zone2):
        arcpy.Delete_management(spring_bus_traveller_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_traveller_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone2BusTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Bus Traveller Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_bus_traveller_zone2):
        arcpy.Delete_management(fall_bus_traveller_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_bus_traveller_tbl, out_path=wkspace_gdb, out_name="FallWDCZone2BusTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_ID,-1,-1;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_bus_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_bus_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_bus_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    edit = arcpy.da.Editor(wkspace_gdb)

    log_message = "Beginning edit session in {}".format(wkspace_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert - 50/50 split from source table to isolate seasonal data
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()
    # ZONE 1 Record Insertion *****************************************************************************************
    log_message = "Populating Bus Zone 1 Traveller Data in Fall and Spring tables ..."
    logger.info(log_message)

    t1 = 1
    t2 = 0
    objectID = 0
    ndxT1Tbl = arcpy.da.InsertCursor(spring_bus_traveller_zone1,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxT2Tbl = arcpy.da.InsertCursor(fall_bus_traveller_zone1,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxTrav1Tbl = arcpy.da.SearchCursor(srcdata_bus_traveller_zone1,
                                        ["Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                         "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                         "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                         "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                         "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                         "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                         "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                         "Income_More_than_200K__percent_"], None, None, "False", (None, None))

    for i1Row in ndxTrav1Tbl:
        modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneInc1, zoneInc2, zoneInc3, zoneInc4, zoneInc5, zoneInc6, zoneInc7, zoneInc8, zoneInc9 = \
        i1Row[0], i1Row[1], i1Row[2], i1Row[3], i1Row[4], i1Row[5], i1Row[6], i1Row[7], i1Row[8], i1Row[9], i1Row[10], i1Row[11], i1Row[12], i1Row[13], i1Row[14], i1Row[15], i1Row[16], i1Row[17], i1Row[18]
        if (zoneNm == None):
            pass
        elif (t1 < r1Count + 1):
            objectID = t1
            ndxT1Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneInc1, zoneInc2, zoneInc3, zoneInc4, zoneInc5, zoneInc6, zoneInc7, zoneInc8, zoneInc9])
        else:
            objectID = t1
            ndxT2Tbl.insertRow(
                [objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneInc1, zoneInc2, zoneInc3, zoneInc4, zoneInc5, zoneInc6, zoneInc7, zoneInc8, zoneInc9])
        t1 += 1
    del i1Row
    del ndxTrav1Tbl

    t2 = (t1 - 1) / 2

    log_message = "Applied {} new records to {}".format(t2, spring_bus_traveller_zone1)
    logger.info(log_message)

    del ndxT1Tbl

    log_message = "Applied {} new records to {}".format(t2, fall_bus_traveller_zone1)
    logger.info(log_message)

    del ndxT2Tbl
    # ******************************************************************************************************************
    # ZONE 2 Record Insertion *****************************************************************************************
    log_message = "Populating Bus Zone 2 Traveller Data in Fall and Spring tables ..."
    logger.info(log_message)

    t1 = 1
    t2 = 0
    objectID = 0
    ndxT1Tbl = arcpy.da.InsertCursor(spring_bus_traveller_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxT2Tbl = arcpy.da.InsertCursor(fall_bus_traveller_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxTrav2Tbl = arcpy.da.SearchCursor(srcdata_bus_traveller_zone2,
                                        ["Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                         "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                         "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                         "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                         "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                         "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                         "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                         "Income_More_than_200K__percent_"], None, None, "False", (None, None))

    for i2Row in ndxTrav2Tbl:
        modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneInc1, zoneInc2, zoneInc3, zoneInc4, zoneInc5, zoneInc6, zoneInc7, zoneInc8, zoneInc9 = \
            i2Row[0], i2Row[1], i2Row[2], i2Row[3], i2Row[4], i2Row[5], i2Row[6], i2Row[7], i2Row[8], i2Row[9], i2Row[10], i2Row[11], i2Row[12], i2Row[13], i2Row[14], i2Row[15], i2Row[16], i2Row[17], i2Row[18]
        if (zoneNm == None):
            pass
        elif (t1 < r2Count + 1):
            objectID = t1
            ndxT1Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneInc1, zoneInc2, zoneInc3, zoneInc4, zoneInc5, zoneInc6, zoneInc7, zoneInc8, zoneInc9])
        else:
            objectID = t1
            ndxT2Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneInc1, zoneInc2, zoneInc3, zoneInc4, zoneInc5, zoneInc6, zoneInc7, zoneInc8, zoneInc9])
        t1 += 1
    del i2Row
    del ndxTrav2Tbl

    t2 = (t1 - 1) / 2

    log_message = "Applied {} new records to {}".format(t2, spring_bus_traveller_zone2)
    logger.info(log_message)

    del ndxT1Tbl

    log_message = "Applied {} new records to {}".format(t2, fall_bus_traveller_zone2)
    logger.info(log_message)

    del ndxT2Tbl
    # ******************************************************************************************************************

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(wkspace_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    log_message = "Removing rows of all-day avg. income in all seasonal traveller tables"
    logger.info(log_message)

    for xTbl in seasonBTblList:
        travCount = arcpy.GetCount_management(xTbl)
        xCount = int(travCount[0])

        log_message = "Filtering {}".format(xTbl)
        logger.info(log_message)

        oid = None
        zName = None
        dType = None
        x = 0
        xRecNDX = arcpy.da.UpdateCursor(xTbl, ["OBJECTID", "Zone_Name", "Day_Type"], None, None, "False", (None, None))
        for xRow in xRecNDX:
            oid, zName, dType = xRow[0], xRow[1], xRow[2]
            if (dType == '0: All Days (M-Su)'):
                x += 1
                xRecNDX.deleteRow()
            else:
                pass

        del xRow
        del xRecNDX

        log_message = "Cleared {} all-day average records of {} in {}".format(str(x), xCount, xTbl)
        logger.info(log_message)

        # Process: Add Field
        arcpy.AddField_management(in_table=xTbl, field_name="TripKey", field_type="TEXT",
                                  field_precision=None, field_scale=None, field_length=None, field_alias="TripKey",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        log_message = "Adding/Calculating Unique Trip Key field ..."
        logger.info(log_message)

        # Process: Calculate Field
        arcpy.CalculateField_management(in_table=xTbl, field="TripKey",
                                        expression="calcTripKey(!Zone_Name!, !Day_Type!, !Day_Part!)",
                                        expression_type="PYTHON_9.3", code_block="""def calcTripKey(zonenm, daytype, daypart):
                    dptVal = \"\"
                    dtStr = str(daytype)
                    dpStr = str(daypart)
                    zStr = str(int(zonenm))
                    dtCode = dtStr[0:1]
                    dpCode = dpStr[0:1]
                    dptVal = zStr + \"-\" + dtCode + dpCode
                    return dptVal""")

    log_message = "Joining Fall and Spring Zone 1 traveller income data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_bus_traveller_zone1, in_field="TripKey",
                               join_table=fall_bus_traveller_zone1, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                        "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                        "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                        "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                        "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                        "Income_More_than_200K__percent_"])

    log_message = "Joining Fall and Spring Zone 2 traveller income data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_bus_traveller_zone2, in_field="TripKey",
                               join_table=fall_bus_traveller_zone2, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                        "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                        "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                        "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                        "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                        "Income_More_than_200K__percent_"])

    log_message = "Resetting the All-Zone Bus Traveller output table"
    logger.info(log_message)

    if arcpy.Exists(cgc_bus_traveller):
        arcpy.Delete_management(cgc_bus_traveller, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=temp_cgc_bus_traveller_tbl, out_path=wkspace_gdb, out_name="CGCBusTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Index1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Average_Daily_Zone_Traffic__StL_Index1,-1,-1;Income_Less_than_20K__percent1 \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_Less_than_20K__percent1,-1,-1;Income_20K_to_35K__percent1 \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_20K_to_35K__percent1,-1,-1;Income_35K_to_50K__percent1 \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_35K_to_50K__percent1,-1,-1;Income_50K_to_75K__percent1 \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_50K_to_75K__percent1,-1,-1;Income_75K_to_100K__percent1 \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_75K_to_100K__percent1,-1,-1;Income_100K_to_125K__percent1 \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_100K_to_125K__percent1,-1,-1;Income_125K_to_150K__percent1 \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_125K_to_150K__percent1,-1,-1;Income_150K_to_200K__percent1 \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_150K_to_200K__percent1,-1,-1;Income_More_than_200K__percent1 \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_bus_traveller_tbl + ",Income_More_than_200K__percent1,-1,-1", config_keyword="")

    log_message = "Combining Zone 1 and Zone 2 traveller income data in {}".format(cgc_bus_traveller)
    logger.info(log_message)

    # Process: Append
    arcpy.Append_management(inputs=[spring_bus_traveller_zone1, spring_bus_traveller_zone2], target=cgc_bus_traveller, schema_type="NO_TEST", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Mode_of_Travel,0,2147483647," + spring_bus_traveller_zone2 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Intersection_Type,0,2147483647," + spring_bus_traveller_zone2 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Zone_ID,0,2147483647," + spring_bus_traveller_zone2 + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Zone_Name,-1,-1," + spring_bus_traveller_zone2 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Zone_Is_Pass_Through,0,2147483647," + spring_bus_traveller_zone2 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Zone_Direction__degrees_,0,2147483647," + spring_bus_traveller_zone2 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Zone_is_Bi_Direction,0,2147483647," + spring_bus_traveller_zone2 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Day_Type,0,2147483647," + spring_bus_traveller_zone2 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",Day_Part,0,2147483647," + spring_bus_traveller_zone2 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_bus_traveller_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1," + spring_bus_traveller_zone2 + ",Average_Daily_Zone_Traffic__StL_Volume_,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_Less_than_20K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_20K_to_35K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_35K_to_50K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_50K_to_75K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_75K_to_100K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_100K_to_125K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_125K_to_150K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_150K_to_200K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_More_than_200K__percent_,-1,-1," + spring_bus_traveller_zone2 + ",Income_More_than_200K__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + spring_bus_traveller_zone1 + ",TripKey,0,255," + spring_bus_traveller_zone2 + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Index1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_bus_traveller_zone1 + ",Average_Daily_Zone_Traffic__StL_Index1,-1,-1," + spring_bus_traveller_zone2 + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1;Income_Less_than_20K__percent1 \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_Less_than_20K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_Less_than_20K__percent1,-1,-1;Income_20K_to_35K__percent1 \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_20K_to_35K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_20K_to_35K__percent1,-1,-1;Income_35K_to_50K__percent1 \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_35K_to_50K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_35K_to_50K__percent1,-1,-1;Income_50K_to_75K__percent1 \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_50K_to_75K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_50K_to_75K__percent1,-1,-1;Income_75K_to_100K__percent1 \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_75K_to_100K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_75K_to_100K__percent1,-1,-1;Income_100K_to_125K__percent1 \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_100K_to_125K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_100K_to_125K__percent1,-1,-1;Income_125K_to_150K__percent1 \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_125K_to_150K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_125K_to_150K__percent1,-1,-1;Income_150K_to_200K__percent1 \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_150K_to_200K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_150K_to_200K__percent1,-1,-1;Income_More_than_200K__percent1 \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_bus_traveller_zone1 + ",Income_More_than_200K__percent1,-1,-1," + spring_bus_traveller_zone2 + ",Income_More_than_200K__percent1,-1,-1", subtype="")

    log_message = "Average Bus Traveller income table is ready for processing"
    logger.info(log_message)

    log_message = "Adding fields for calculating annual percent of household incomes to {}".format(cgc_bus_traveller)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_18K_Pct", field_type="FLOAT", field_precision=5,
                              field_scale=4, field_length=None, field_alias="Avg_18K_Pct",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_28K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_28K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_42K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_42K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_58K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_58K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_87K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_87K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_113K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_113K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_137K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_137K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_175K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_175K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="Avg_225K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_225K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Adding the Average Annual Traveller Income field to {}".format(cgc_bus_traveller)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_bus_traveller, field_name="AvgAnnualIncome", field_type="DOUBLE",
                              field_precision=7, field_scale=3, field_length=None, field_alias="AvgAnnualIncome",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Calculating Average Incomes by category..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_18K_Pct",
            expression="calcAvg18KPct(!Income_Less_than_20K__percent_!, !Income_Less_than_20K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg18KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 18000
            elif pct2 == None:
                avgVal = pct1 * 18000
            else:
                avgVal = ((pct1 + pct2) / 2) * 18000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_28K_Pct",
            expression="calcAvg28KPct(!Income_20K_to_35K__percent_!, !Income_20K_to_35K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg28KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 28000
            elif pct2 == None:
                avgVal = pct1 * 28000
            else:
                avgVal = ((pct1 + pct2) / 2) * 28000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_42K_Pct",
            expression="calcAvg42KPct(!Income_35K_to_50K__percent_!, !Income_35K_to_50K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg42KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 42000
            elif pct2 == None:
                avgVal = pct1 * 42000
            else:
                avgVal = ((pct1 + pct2) / 2) * 42000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_58K_Pct",
            expression="calcAvg58KPct(!Income_50K_to_75K__percent_!, !Income_50K_to_75K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg58KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 58000
            elif pct2 == None:
                avgVal = pct1 * 58000
            else:
                avgVal = ((pct1 + pct2) / 2) * 58000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_87K_Pct",
            expression="calcAvg87KPct(!Income_75K_to_100K__percent_!, !Income_75K_to_100K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg87KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 87000
            elif pct2 == None:
                avgVal = pct1 * 87000
            else:
                avgVal = ((pct1 + pct2) / 2) * 87000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_113K_Pct",
            expression="calcAvg113KPct(!Income_100K_to_125K__percent_!, !Income_100K_to_125K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg113KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 113000
            elif pct2 == None:
                avgVal = pct1 * 113000
            else:
                avgVal = ((pct1 + pct2) / 2) * 113000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_137K_Pct",
            expression="calcAvg137KPct(!Income_125K_to_150K__percent_!, !Income_125K_to_150K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg137KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 137000
            elif pct2 == None:
                avgVal = pct1 * 137000
            else:
                avgVal = ((pct1 + pct2) / 2) * 137000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_175K_Pct",
            expression="calcAvg175KPct(!Income_150K_to_200K__percent_!, !Income_150K_to_200K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg175KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 175000
            elif pct2 == None:
                avgVal = pct1 * 175000
            else:
                avgVal = ((pct1 + pct2) / 2) * 175000
            return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="Avg_225K_Pct",
            expression="calcAvg225KPct(!Income_More_than_200K__percent_!, !Income_More_than_200K__percent1!)",
            expression_type="PYTHON_9.3", code_block="""def calcAvg225KPct(pct1, pct2):
            avgVal = 0
            if pct1 == None:
                avgVal = pct2 * 225000
            elif pct2 == None:
                avgVal = pct1 * 225000
            else:
                avgVal = ((pct1 + pct2) / 2) * 225000
            return avgVal""")

    log_message = "Adding all results for Average Annual Household Income in all Zones"
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_bus_traveller, field="AvgAnnualIncome",
            expression="calcTotalIncome(!Avg_18K_Pct!, !Avg_28K_Pct!, !Avg_42K_Pct!, !Avg_58K_Pct!, !Avg_87K_Pct!, !Avg_113K_Pct!, !Avg_137K_Pct!, !Avg_175K_Pct!, !Avg_225K_Pct!)",
            expression_type="PYTHON_9.3", code_block="""def calcTotalIncome(avg1, avg2, avg3, avg4, avg5, avg6, avg7, avg8, avg9):
            retNum = 0.0
            retNum = avg1 + avg2 + avg3 + avg4 + avg5 + avg6 + avg7 + avg8 + avg9
            return retNum""")

    log_message = "The calculation of Average Traveller Income is complete for all zones"
    logger.info(log_message)

    log_message = "Performing housekeeping tasks ..."
    logger.info(log_message)

    for zTbl in seasonBTblList:

        log_message = "Deleting {}". format(zTbl)
        logger.info(log_message)

        if arcpy.Exists(zTbl):
            arcpy.Delete_management(zTbl, "Table")

    return "%%%%%%% Process B2 Complete %%%%%%%"


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

    result_b1 = constructBusTripTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
    logger.info(result_b1)

    result_b2 = constructBusTravellerTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
    logger.info(result_b2)