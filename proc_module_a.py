# ---------------------------------------------------------------------------
# proc_module_a.py
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
def defineServiceArea(wkspace_gdb, mstaging_gdb, data_directory, logger):

    log_message = "%%%%%%% Process A1 - Define the Study Area %%%%%%%"
    logger.info(log_message)

    # Local variables -- AUTO
    usblkgrps = os.path.join(mstaging_gdb, "USBlockGroups")
    wmcog_boundary = os.path.join(mstaging_gdb, "MWCOG_Boundary")
    wmcog_blkgrps = mstaging_gdb + "\\WMCOG_BlockGroups"
    wmcog_auto_zone1 = data_directory + "\\SL\\442249_MWCOG_Auto_Zone1\\Shapefile\\442249_MWCOG_Auto_Zone1_zone_activity.shp"
    svcarea_auto_zone1 = wkspace_gdb + "\\WDC_ZoneSet1"
    wmcog_auto_zone2 = data_directory + "\\SL\\948950_MWCOG_Auto_Zone2\\Shapefile\\948950_MWCOG_Auto_Zone2_zone_activity.shp"
    svcarea_auto_zone2 = wkspace_gdb + "\\WDC_ZoneSet2"
    svcarea_taz = mstaging_gdb + "\\WDC_TAZ_StudyArea"

    if arcpy.Exists(wmcog_blkgrps):
        arcpy.Delete_management(wmcog_blkgrps, "FeatureClass")

    log_message = "Clipping US Census Block Groups by Boundary Area to create: {}".format(wmcog_blkgrps)
    logger.info(log_message)

    # Process: Clip
    with arcpy.EnvManager(outputCoordinateSystem='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'):
        arcpy.Clip_analysis(in_features=usblkgrps, clip_features=wmcog_boundary, out_feature_class=wmcog_blkgrps, cluster_tolerance="")

        if arcpy.Exists(svcarea_auto_zone1):
            arcpy.Delete_management(svcarea_auto_zone1, "FeatureClass")

        log_message = "Converting initial service area shapefile to: {}".format(svcarea_auto_zone1)
        logger.info(log_message)

        arcpy.FeatureClassToFeatureClass_conversion(in_features=wmcog_auto_zone1, out_path=wkspace_gdb, out_name="WDC_ZoneSet1", where_clause="", field_mapping="id \"id\" true true false 3 Text 0 0,First,#," + wmcog_auto_zone1 + ",id,0,3;name \"name\" true true false 13 Text 0 0,First,#," + wmcog_auto_zone1 + ",name,0,13;direction \"direction\" true true false 32 Double 10 31,First,#," + wmcog_auto_zone1 + ",direction,-1,-1;is_pass \"is_pass\" true true false 11 Double 0 11,First,#," + wmcog_auto_zone1 + ",is_pass,-1,-1;is_bidi \"is_bidi\" true true false 11 Double 0 11,First,#," + wmcog_auto_zone1 + ",is_bidi,-1,-1", config_keyword="")

        if arcpy.Exists(svcarea_auto_zone2):
            arcpy.Delete_management(svcarea_auto_zone2, "FeatureClass")

        log_message = "Converting next service area shapefile to: {}".format(svcarea_auto_zone2)
        logger.info(log_message)

        arcpy.FeatureClassToFeatureClass_conversion(in_features=wmcog_auto_zone2, out_path=wkspace_gdb, out_name="WDC_ZoneSet2", where_clause="", field_mapping="id \"id\" true true false 3 Text 0 0,First,#," + wmcog_auto_zone2 + ",id,0,3;name \"name\" true true false 13 Text 0 0,First,#," + wmcog_auto_zone2 + ",name,0,13;direction \"direction\" true true false 32 Double 10 31,First,#," + wmcog_auto_zone2 + ",direction,-1,-1;is_pass \"is_pass\" true true false 11 Double 0 11,First,#," + wmcog_auto_zone2 + ",is_pass,-1,-1;is_bidi \"is_bidi\" true true false 11 Double 0 11,First,#," + wmcog_auto_zone2 + ",is_bidi,-1,-1", config_keyword="")

        if arcpy.Exists(svcarea_taz):
            arcpy.Delete_management(svcarea_taz, "FeatureClass")

        log_message = "Merging service area zone sets into: {}".format(svcarea_taz)
        logger.info(log_message)

        arcpy.Merge_management(inputs=[svcarea_auto_zone1, svcarea_auto_zone2], output=svcarea_taz, field_mappings="id \"id\" true true false 3 Text 0 0,First,#," + svcarea_auto_zone1 + ",id,0,3," + svcarea_auto_zone2 + ",id,0,3;name \"name\" true true false 13 Text 0 0,First,#," + svcarea_auto_zone1 + ",name,0,13," + svcarea_auto_zone2 + ",name,0,13;direction \"direction\" true true false 8 Double 0 0,First,#," + svcarea_auto_zone1 + ",direction,-1,-1," + svcarea_auto_zone2 + ",direction,-1,-1;is_pass \"is_pass\" true true false 8 Double 0 0,First,#," + svcarea_auto_zone1 + ",is_pass,-1,-1," + svcarea_auto_zone2 + ",is_pass,-1,-1;is_bidi \"is_bidi\" true true false 8 Double 0 0,First,#," + svcarea_auto_zone1 + ",is_bidi,-1,-1," + svcarea_auto_zone2 + ",is_bidi,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0,First,#," + svcarea_auto_zone1 + ",Shape_Length,-1,-1," + svcarea_auto_zone2 + ",Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0,First,#," + svcarea_auto_zone1 + ",Shape_Area,-1,-1," + svcarea_auto_zone2 + ",Shape_Area,-1,-1")  ## Pro:  add_source="NO_SOURCE_INFO"

    log_message = "The Service/Study Area is Ready!"
    logger.info(log_message)

    return "%%%%%%% Process A1 Complete %%%%%%%"

def constructAutoTripTbl(src_data, wkspace_gdb, temp_data, logger):

    log_message = "%%%%%%% Process A2 - Calculate Total Probability of Avg. Trip Speed per Zone %%%%%%%"
    logger.info(log_message)

    # Templates
    seasonal_auto_trip_tbl = os.path.join(temp_data, "SeasonalAutoTrip")
    temp_cgc_auto_tbl = os.path.join(temp_data, "CGCAutoTripTemp")

    # Trip variables:
    srcdata_auto_trip_zone1 = os.path.join(src_data, "WDCZone1AutoTrip")
    spring_auto_trip_zone1 = wkspace_gdb + "\\SpringWDCZone1AutoTrip"
    fall_auto_trip_zone1 = wkspace_gdb + "\\FallWDCZone1AutoTrip"
    srcdata_auto_trip_zone2 = os.path.join(src_data, "WDCZone2AutoTrip")
    spring_auto_trip_zone2 = wkspace_gdb + "\\SpringWDCZone2AutoTrip"
    fall_auto_trip_zone2 = wkspace_gdb + "\\FallWDCZone2AutoTrip"
    cgc_auto_trip = wkspace_gdb + "\\CGCAutoTrip"  ## all combined avg. speed
    seasonTblList = [spring_auto_trip_zone1, fall_auto_trip_zone1, spring_auto_trip_zone2, fall_auto_trip_zone2]

    log_message = "Checking for missing auto trip template ..."
    logger.info(log_message)

    if arcpy.Exists(seasonal_auto_trip_tbl):
        pass
    else:
        log_message = "Seasonal Auto Trip Table is missing - Resetting now ..."
        logger.info(log_message)

        # Process: Table To Table
        arcpy.TableToTable_conversion(in_rows=srcdata_auto_trip_zone1, out_path=temp_data, out_name="SeasonalAutoTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + srcdata_auto_trip_zone1 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_trip_zone1 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + srcdata_auto_trip_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_trip_zone1 + ",Trip_Speed_70__mph__percent_,-1,-1", config_keyword="")

        # Process: Delete Rows
        arcpy.DeleteRows_management(in_rows=seasonal_auto_trip_tbl)

    log_message = "Auto Trip template table ready"
    logger.info(log_message)
    # Integrate the Auto Traffic Metrics for Insertion to the Automobile Network Dataset
    log_message = "Begin Auto Trip Data Integration - Total Probability of Zonal Average Speed"
    logger.info(log_message)

    # ZONE 1 Auto Trip Seasonal Split
    result = arcpy.GetCount_management(srcdata_auto_trip_zone1)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r1Count = int(result[0])/2

    log_message = "{} record count in {}".format(r1Count * 2, srcdata_auto_trip_zone1)
    logger.info(log_message)

    log_message = "Resetting Spring Auto Trip Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_auto_trip_zone1):
        arcpy.Delete_management(spring_auto_trip_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_trip_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone1AutoTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + seasonal_auto_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + seasonal_auto_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_70__mph__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Auto Trip Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_auto_trip_zone1):
        arcpy.Delete_management(fall_auto_trip_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_trip_tbl, out_path=wkspace_gdb, out_name="FallWDCZone1AutoTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + seasonal_auto_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + seasonal_auto_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_70__mph__percent_,-1,-1", config_keyword="")

    # ZONE 2 Auto Trip Seasonal Split
    result = arcpy.GetCount_management(srcdata_auto_trip_zone2)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r2Count = int(result[0]) / 2

    log_message = "{} record count in {}".format(r2Count * 2, srcdata_auto_trip_zone2)
    logger.info(log_message)

    log_message = "Resetting Spring Auto Trip Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_auto_trip_zone2):
        arcpy.Delete_management(spring_auto_trip_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_trip_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone2AutoTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + seasonal_auto_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + seasonal_auto_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_70__mph__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Auto Trip Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_auto_trip_zone2):
        arcpy.Delete_management(fall_auto_trip_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_trip_tbl, out_path=wkspace_gdb, out_name="FallWDCZone2AutoTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + seasonal_auto_trip_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_trip_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + seasonal_auto_trip_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_trip_tbl + ",Trip_Speed_70__mph__percent_,-1,-1", config_keyword="")

    edit = arcpy.da.Editor(wkspace_gdb)

    log_message = "Beginning edit session in {}".format(wkspace_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert - 50/50 split from source table to isolate seasonal data
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()
    # ZONE 1 Record Insertion *****************************************************************************************
    log_message = "Populating Auto Zone 1 Speed Data in Fall and Spring tables ..."
    logger.info(log_message)

    s1 = 1
    s2 = 0
    objectID = 0
    ndxS1Tbl = arcpy.da.InsertCursor(spring_auto_trip_zone1, ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name", "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction", "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL", "Trip_Speed_0_10_mph__percent_", "Trip_Speed_10_20_mph__percent_", "Trip_Speed_20_30_mph__percent_", "Trip_Speed_30_40_mph__percent_", "Trip_Speed_40_50_mph__percent_", "Trip_Speed_50_60_mph__percent_", "Trip_Speed_60_70_mph__percent_", "Trip_Speed_70__mph__percent_"])
    ndxS2Tbl = arcpy.da.InsertCursor(fall_auto_trip_zone1, ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name", "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction", "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL", "Trip_Speed_0_10_mph__percent_", "Trip_Speed_10_20_mph__percent_", "Trip_Speed_20_30_mph__percent_", "Trip_Speed_30_40_mph__percent_", "Trip_Speed_40_50_mph__percent_", "Trip_Speed_50_60_mph__percent_", "Trip_Speed_60_70_mph__percent_", "Trip_Speed_70__mph__percent_"])
    ndxTrip1Tbl = arcpy.da.SearchCursor(srcdata_auto_trip_zone1, ["Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name", "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction", "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL", "Trip_Speed_0_10_mph__percent_", "Trip_Speed_10_20_mph__percent_", "Trip_Speed_20_30_mph__percent_", "Trip_Speed_30_40_mph__percent_", "Trip_Speed_40_50_mph__percent_", "Trip_Speed_50_60_mph__percent_", "Trip_Speed_60_70_mph__percent_", "Trip_Speed_70__mph__percent_"], None, None, "False", (None, None))

    for t1Row in ndxTrip1Tbl:
        modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8 = t1Row[0], t1Row[1], t1Row[2], t1Row[3], t1Row[4], t1Row[5], t1Row[6], t1Row[7], t1Row[8], t1Row[9], t1Row[10], t1Row[11], t1Row[12], t1Row[13], t1Row[14], t1Row[15], t1Row[16], t1Row[17]
        if (zoneNm == None):
            pass
        elif (s1 < r1Count + 1):
            objectID = s1
            ndxS1Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8])
        else:
            objectID = s1
            ndxS2Tbl.insertRow([objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8])
        s1 += 1
    del t1Row
    del ndxTrip1Tbl

    s2 = (s1 - 1)/2

    log_message = "Applied {} new records to {}".format(s2, spring_auto_trip_zone1)
    logger.info(log_message)

    del ndxS1Tbl

    log_message = "Applied {} new records to {}".format(s2, fall_auto_trip_zone1)
    logger.info(log_message)

    del ndxS2Tbl
    # ******************************************************************************************************************
    # ZONE 2 Record Insertion *****************************************************************************************
    log_message = "Populating Auto Zone 2 Speed Data in Fall and Spring tables ..."
    logger.info(log_message)

    s1 = 1
    s2 = 0
    objectID = 0
    ndxS1Tbl = arcpy.da.InsertCursor(spring_auto_trip_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Trip_Speed_0_10_mph__percent_", "Trip_Speed_10_20_mph__percent_",
                                      "Trip_Speed_20_30_mph__percent_", "Trip_Speed_30_40_mph__percent_",
                                      "Trip_Speed_40_50_mph__percent_", "Trip_Speed_50_60_mph__percent_",
                                      "Trip_Speed_60_70_mph__percent_", "Trip_Speed_70__mph__percent_"])
    ndxS2Tbl = arcpy.da.InsertCursor(fall_auto_trip_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Trip_Speed_0_10_mph__percent_", "Trip_Speed_10_20_mph__percent_",
                                      "Trip_Speed_20_30_mph__percent_", "Trip_Speed_30_40_mph__percent_",
                                      "Trip_Speed_40_50_mph__percent_", "Trip_Speed_50_60_mph__percent_",
                                      "Trip_Speed_60_70_mph__percent_", "Trip_Speed_70__mph__percent_"])
    ndxTrip2Tbl = arcpy.da.SearchCursor(srcdata_auto_trip_zone2,
                                        ["Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                         "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                         "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                         "Trip_Speed_0_10_mph__percent_", "Trip_Speed_10_20_mph__percent_",
                                         "Trip_Speed_20_30_mph__percent_", "Trip_Speed_30_40_mph__percent_",
                                         "Trip_Speed_40_50_mph__percent_", "Trip_Speed_50_60_mph__percent_",
                                         "Trip_Speed_60_70_mph__percent_", "Trip_Speed_70__mph__percent_"], None, None,
                                        "False", (None, None))

    for t2Row in ndxTrip2Tbl:
        modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT, zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8 = \
        t2Row[0], t2Row[1], t2Row[2], t2Row[3], t2Row[4], t2Row[5], t2Row[6], t2Row[7], t2Row[8], t2Row[9], t2Row[10], \
        t2Row[11], t2Row[12], t2Row[13], t2Row[14], t2Row[15], t2Row[16], t2Row[17]
        if (zoneNm == None):
            pass
        elif (s1 < r2Count + 1):
            objectID = s1
            ndxS1Tbl.insertRow(
                [objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8])
        else:
            objectID = s1
            ndxS2Tbl.insertRow(
                [objectID, modeTrav, intType, zoneID, zoneNm, zonePass, zoneDir, zoneBiDir, dayType, dayPart, zoneAADT,
                 zoneSpd1, zoneSpd2, zoneSpd3, zoneSpd4, zoneSpd5, zoneSpd6, zoneSpd7, zoneSpd8])
        s1 += 1
    del t2Row
    del ndxTrip2Tbl

    s2 = (s1 - 1) / 2

    log_message = "Applied {} new records to {}".format(s2, spring_auto_trip_zone2)
    logger.info(log_message)

    del ndxS1Tbl

    log_message = "Applied {} new records to {}".format(s2, fall_auto_trip_zone2)
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

    for xTbl in seasonTblList:
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
            return dptVal""")  ### field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS"

    log_message = "Joining Fall and Spring Zone 1 speed data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_auto_trip_zone1, in_field="TripKey",
                               join_table=fall_auto_trip_zone1, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                       "Trip_Speed_0_10_mph__percent_",
                                       "Trip_Speed_10_20_mph__percent_",
                                       "Trip_Speed_20_30_mph__percent_",
                                       "Trip_Speed_30_40_mph__percent_",
                                       "Trip_Speed_40_50_mph__percent_",
                                       "Trip_Speed_50_60_mph__percent_",
                                       "Trip_Speed_60_70_mph__percent_",
                                       "Trip_Speed_70__mph__percent_"])

    log_message = "Joining Fall and Spring Zone 2 speed data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_auto_trip_zone2, in_field="TripKey",
                               join_table=fall_auto_trip_zone2, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                       "Trip_Speed_0_10_mph__percent_",
                                       "Trip_Speed_10_20_mph__percent_",
                                       "Trip_Speed_20_30_mph__percent_",
                                       "Trip_Speed_30_40_mph__percent_",
                                       "Trip_Speed_40_50_mph__percent_",
                                       "Trip_Speed_50_60_mph__percent_",
                                       "Trip_Speed_60_70_mph__percent_",
                                       "Trip_Speed_70__mph__percent_"])

    log_message = "Resetting the All-Zone Auto Trip output table"
    logger.info(log_message)

    if arcpy.Exists(cgc_auto_trip):
        arcpy.Delete_management(cgc_auto_trip, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=temp_cgc_auto_tbl, out_path=wkspace_gdb, out_name="CGCAutoTrip", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_auto_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_70__mph__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + temp_cgc_auto_tbl + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Volume1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_auto_tbl + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1;Trip_Speed_0_10_mph__percent1 \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_0_10_mph__percent1,-1,-1;Trip_Speed_10_20_mph__percent1 \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_10_20_mph__percent1,-1,-1;Trip_Speed_20_30_mph__percent1 \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_20_30_mph__percent1,-1,-1;Trip_Speed_30_40_mph__percent1 \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_30_40_mph__percent1,-1,-1;Trip_Speed_40_50_mph__percent1 \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_40_50_mph__percent1,-1,-1;Trip_Speed_50_60_mph__percent1 \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_50_60_mph__percent1,-1,-1;Trip_Speed_60_70_mph__percent1 \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_60_70_mph__percent1,-1,-1;Trip_Speed_70__mph__percent1 \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_tbl + ",Trip_Speed_70__mph__percent1,-1,-1", config_keyword="")

    log_message = "Combining Zone 1 and Zone 2 trip speed data in {}".format(cgc_auto_trip)
    logger.info(log_message)

    # Process: Append
    arcpy.Append_management(inputs=[spring_auto_trip_zone1, spring_auto_trip_zone2], target=cgc_auto_trip, schema_type="NO_TEST", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Mode_of_Travel,0,2147483647," + spring_auto_trip_zone2 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Intersection_Type,0,2147483647," + spring_auto_trip_zone2 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Zone_ID,0,2147483647," + spring_auto_trip_zone2 + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Zone_Name,-1,-1," + spring_auto_trip_zone2 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Zone_Is_Pass_Through,0,2147483647," + spring_auto_trip_zone2 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Zone_Direction__degrees_,0,2147483647," + spring_auto_trip_zone2 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Zone_is_Bi_Direction,0,2147483647," + spring_auto_trip_zone2 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Day_Type,0,2147483647," + spring_auto_trip_zone2 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + spring_auto_trip_zone1 + ",Day_Part,0,2147483647," + spring_auto_trip_zone2 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_auto_trip_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1," + spring_auto_trip_zone2 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Trip_Speed_0_10_mph__percent_ \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_0_10_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_0_10_mph__percent_,-1,-1;Trip_Speed_10_20_mph__percent_ \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_10_20_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_10_20_mph__percent_,-1,-1;Trip_Speed_20_30_mph__percent_ \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_20_30_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_20_30_mph__percent_,-1,-1;Trip_Speed_30_40_mph__percent_ \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_30_40_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_30_40_mph__percent_,-1,-1;Trip_Speed_40_50_mph__percent_ \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_40_50_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_40_50_mph__percent_,-1,-1;Trip_Speed_50_60_mph__percent_ \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_50_60_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_50_60_mph__percent_,-1,-1;Trip_Speed_60_70_mph__percent_ \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_60_70_mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_60_70_mph__percent_,-1,-1;Trip_Speed_70__mph__percent_ \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_70__mph__percent_,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_70__mph__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + spring_auto_trip_zone1 + ",TripKey,0,255," + spring_auto_trip_zone2 + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Volume1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_auto_trip_zone1 + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1," + spring_auto_trip_zone2 + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1;Trip_Speed_0_10_mph__percent1 \"Trip_Speed_0_10_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_0_10_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_0_10_mph__percent1,-1,-1;Trip_Speed_10_20_mph__percent1 \"Trip_Speed_10_20_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_10_20_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_10_20_mph__percent1,-1,-1;Trip_Speed_20_30_mph__percent1 \"Trip_Speed_20_30_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_20_30_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_20_30_mph__percent1,-1,-1;Trip_Speed_30_40_mph__percent1 \"Trip_Speed_30_40_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_30_40_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_30_40_mph__percent1,-1,-1;Trip_Speed_40_50_mph__percent1 \"Trip_Speed_40_50_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_40_50_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_40_50_mph__percent1,-1,-1;Trip_Speed_50_60_mph__percent1 \"Trip_Speed_50_60_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_50_60_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_50_60_mph__percent1,-1,-1;Trip_Speed_60_70_mph__percent1 \"Trip_Speed_60_70_mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_60_70_mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_60_70_mph__percent1,-1,-1;Trip_Speed_70__mph__percent1 \"Trip_Speed_70__mph__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_trip_zone1 + ",Trip_Speed_70__mph__percent1,-1,-1," + spring_auto_trip_zone2 + ",Trip_Speed_70__mph__percent1,-1,-1", subtype="")  ## , expression=""

    log_message = "Average Auto Trip Speed table is ready for processing"
    logger.info(log_message)

    log_message = "Adding fields for calculating annual percent of speeds to {}".format(cgc_auto_trip)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_5mph_Pct", field_type="FLOAT", field_precision=5,
                              field_scale=4, field_length=None, field_alias="Avg_5mph_Pct",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_15mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_15mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_25mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_25mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_35mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_35mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_45mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_45mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_55mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_55mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_65mph_Pct", field_type="FLOAT",
                                               field_precision=5, field_scale=4, field_length=None,
                                               field_alias="Avg_65mph_Pct", field_is_nullable="NULLABLE",
                                               field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="Avg_75mph_Pct", field_type="FLOAT",
                                                field_precision=5, field_scale=4, field_length=None,
                                                field_alias="Avg_75mph_Pct", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Adding the Average Annual Auto Speed field (AADS) to {}".format(cgc_auto_trip)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_trip, field_name="AvgAnnualAutoSpeed", field_type="DOUBLE",
                              field_precision=7, field_scale=3, field_length=None, field_alias="AvgAnnualAutoSpeed",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Calculating Average Speeds by category..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_5mph_Pct",
        expression="calcAvg5MphPct(!Trip_Speed_0_10_mph__percent_!, !Trip_Speed_0_10_mph__percent1!)",
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
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_15mph_Pct",
        expression="calcAvg15MphPct(!Trip_Speed_10_20_mph__percent_!, !Trip_Speed_10_20_mph__percent1!)",
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
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_25mph_Pct",
        expression="calcAvg25MphPct(!Trip_Speed_20_30_mph__percent_!, !Trip_Speed_20_30_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg25MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 25
        elif pct2 == None:
            avgVal = pct1 * 25
        else:
            avgVal = ((pct1 + pct2) / 2) * 25
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_35mph_Pct",
        expression="calcAvg35MphPct(!Trip_Speed_30_40_mph__percent_!, !Trip_Speed_30_40_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg35MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 35
        elif pct2 == None:
            avgVal = pct1 * 35
        else:
            avgVal = ((pct1 + pct2) / 2) * 35
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_45mph_Pct",
        expression="calcAvg45MphPct(!Trip_Speed_40_50_mph__percent_!, !Trip_Speed_40_50_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg45MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 45
        elif pct2 == None:
            avgVal = pct1 * 45
        else:
            avgVal = ((pct1 + pct2) / 2) * 45
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_55mph_Pct",
        expression="calcAvg55MphPct(!Trip_Speed_50_60_mph__percent_!, !Trip_Speed_50_60_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg55MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 55
        elif pct2 == None:
            avgVal = pct1 * 55
        else:
            avgVal = ((pct1 + pct2) / 2) * 55
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_65mph_Pct",
        expression="calcAvg65MphPct(!Trip_Speed_60_70_mph__percent_!, !Trip_Speed_60_70_mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg65MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 65
        elif pct2 == None:
            avgVal = pct1 * 65
        else:
            avgVal = ((pct1 + pct2) / 2) * 65
        return avgVal""")

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="Avg_75mph_Pct",
        expression="calcAvg75MphPct(!Trip_Speed_70__mph__percent_!, !Trip_Speed_70__mph__percent1!)",
        expression_type="PYTHON_9.3", code_block="""def calcAvg75MphPct(pct1, pct2):
        avgVal = 0
        if pct1 == None:
            avgVal = pct2 * 75
        elif pct2 == None:
            avgVal = pct1 * 75
        else:
            avgVal = ((pct1 + pct2) / 2) * 75
        return avgVal""")

    log_message = "Adding all results for Average Annual Auto Speed in all Zones"
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_trip, field="AvgAnnualAutoSpeed",
        expression="calcTotalAADS(!Avg_5mph_Pct!, !Avg_15mph_Pct!, !Avg_25mph_Pct!, !Avg_35mph_Pct!, !Avg_45mph_Pct!, !Avg_55mph_Pct!, !Avg_65mph_Pct!, !Avg_75mph_Pct!)",
        expression_type="PYTHON_9.3", code_block="""def calcTotalAADS(avg1, avg2, avg3, avg4, avg5, avg6, avg7, avg8):
        retNum = 0.0
        retNum = avg1 + avg2 + avg3 + avg4 + avg5 + avg6 + avg7 + avg8
        return retNum""")

    log_message = "The calculation of Average Annual Auto Trip Speed is complete for all zones"
    logger.info(log_message)

    log_message = "Performing housekeeping tasks ..."
    logger.info(log_message)

    for zTbl in seasonTblList:

        log_message = "Deleting {}". format(zTbl)
        logger.info(log_message)

        if arcpy.Exists(zTbl):
            arcpy.Delete_management(zTbl, "Table")

    return "%%%%%%% Process A2 Complete %%%%%%%"


def constructAutoTravellerTbl(src_data, wkspace_gdb, temp_data, logger):

    log_message = "%%%%%%% Process A3 - Calculate Total Probability of Avg. Traveller Income per Zone %%%%%%%"
    logger.info(log_message)

    # Templates
    seasonal_auto_traveller_tbl = os.path.join(temp_data, "SeasonalAutoTraveller")
    temp_cgc_auto_traveller_tbl = os.path.join(temp_data, "CGCAutoTravelTemp")

    # Traveller variables:
    srcdata_auto_traveller_zone1 = os.path.join(src_data, "WDCZone1AutoTraveler")
    spring_auto_traveller_zone1 = wkspace_gdb + "\\SpringWDCZone1AutoTraveller"
    fall_auto_traveller_zone1 = wkspace_gdb + "\\FallWDCZone1AutoTraveller"
    srcdata_auto_traveller_zone2 = os.path.join(src_data, "WDCZone2AutoTraveler")
    spring_auto_traveller_zone2 = wkspace_gdb + "\\SpringWDCZone2AutoTraveller"
    fall_auto_traveller_zone2 = wkspace_gdb + "\\FallWDCZone2AutoTraveller"
    cgc_auto_traveller = wkspace_gdb + "\\CGCAutoTraveller"  ## all combined avg. income
    seasonTblList = [spring_auto_traveller_zone1, fall_auto_traveller_zone1, spring_auto_traveller_zone2, fall_auto_traveller_zone2]

    log_message = "Checking for missing auto traveller template ..."
    logger.info(log_message)

    if arcpy.Exists(seasonal_auto_traveller_tbl):
        pass
    else:
        log_message = "Seasonal Auto Traveller Table is missing - Resetting now ..."
        logger.info(log_message)

        # Process: Table To Table
        arcpy.TableToTable_conversion(in_rows=srcdata_auto_traveller_zone1, out_path=temp_data, out_name="SeasonalAutoTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 18,First,#," + srcdata_auto_traveller_zone1 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 10,First,#," + srcdata_auto_traveller_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + srcdata_auto_traveller_zone1 + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

        # Process: Delete Rows (2) (Delete Rows) (management)
        arcpy.DeleteRows_management(in_rows=seasonal_auto_traveller_tbl)

    log_message = "Auto Traveller template table ready"
    logger.info(log_message)
    # Integrate the Auto Traffic Metrics for Insertion to the Automobile Network Dataset
    log_message = "Begin Auto Traveller Data Integration - Total Probability of Zonal Average Auto Traveller Income"
    logger.info(log_message)

    # ZONE 1 Auto Traveller Seasonal Split
    result = arcpy.GetCount_management(srcdata_auto_traveller_zone1)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r1Count = int(result[0]) / 2

    log_message = "{} record count in {}".format(r1Count * 2, srcdata_auto_traveller_zone1)
    logger.info(log_message)

    log_message = "Resetting Spring Auto Traveller Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_auto_traveller_zone1):
        arcpy.Delete_management(spring_auto_traveller_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_traveller_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone1AutoTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_auto_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Auto Traveller Table for Zone1 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_auto_traveller_zone1):
        arcpy.Delete_management(fall_auto_traveller_zone1, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_traveller_tbl, out_path=wkspace_gdb, out_name="FallWDCZone1AutoTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_auto_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    # ZONE 2 Auto Trip Seasonal Split
    result = arcpy.GetCount_management(srcdata_auto_traveller_zone2)  # Get the table record count, to mark the partition between Fall and Spring data capture
    r2Count = int(result[0]) / 2

    log_message = "{} record count in {}".format(r2Count * 2, srcdata_auto_traveller_zone2)
    logger.info(log_message)

    log_message = "Resetting Spring Auto Traveller Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(spring_auto_traveller_zone2):
        arcpy.Delete_management(spring_auto_traveller_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_traveller_tbl, out_path=wkspace_gdb, out_name="SpringWDCZone2AutoTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_auto_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    log_message = "Resetting Fall Auto Traveller Table for Zone2 ..."
    logger.info(log_message)

    if arcpy.Exists(fall_auto_traveller_zone2):
        arcpy.Delete_management(fall_auto_traveller_zone2, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=seasonal_auto_traveller_tbl, out_path=wkspace_gdb, out_name="FallWDCZone2AutoTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + seasonal_auto_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + seasonal_auto_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + seasonal_auto_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1", config_keyword="")

    edit = arcpy.da.Editor(wkspace_gdb)

    log_message = "Beginning edit session in {}".format(wkspace_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert - 50/50 split from source table to isolate seasonal data
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()
    # ZONE 1 Record Insertion *****************************************************************************************
    log_message = "Populating Auto Zone 1 Traveller Data in Fall and Spring tables ..."
    logger.info(log_message)

    t1 = 1
    t2 = 0
    objectID = 0
    ndxT1Tbl = arcpy.da.InsertCursor(spring_auto_traveller_zone1,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxT2Tbl = arcpy.da.InsertCursor(fall_auto_traveller_zone1,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxTrav1Tbl = arcpy.da.SearchCursor(srcdata_auto_traveller_zone1,
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

    log_message = "Applied {} new records to {}".format(t2, spring_auto_traveller_zone1)
    logger.info(log_message)

    del ndxT1Tbl

    log_message = "Applied {} new records to {}".format(t2, fall_auto_traveller_zone1)
    logger.info(log_message)

    del ndxT2Tbl
    # ******************************************************************************************************************
    # ZONE 2 Record Insertion *****************************************************************************************
    log_message = "Populating Auto Zone 2 Traveller Data in Fall and Spring tables ..."
    logger.info(log_message)

    t1 = 1
    t2 = 0
    objectID = 0
    ndxT1Tbl = arcpy.da.InsertCursor(spring_auto_traveller_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxT2Tbl = arcpy.da.InsertCursor(fall_auto_traveller_zone2,
                                     ["OBJECTID", "Mode_of_Travel", "Intersection_Type", "Zone_ID", "Zone_Name",
                                      "Zone_Is_Pass_Through", "Zone_Direction__degrees_", "Zone_is_Bi_Direction",
                                      "Day_Type", "Day_Part", "Average_Daily_Zone_Traffic__StL",
                                      "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                      "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                      "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                      "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                      "Income_More_than_200K__percent_"])
    ndxTrav2Tbl = arcpy.da.SearchCursor(srcdata_auto_traveller_zone2,
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

    log_message = "Applied {} new records to {}".format(t2, spring_auto_traveller_zone2)
    logger.info(log_message)

    del ndxT1Tbl

    log_message = "Applied {} new records to {}".format(t2, fall_auto_traveller_zone2)
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

    for xTbl in seasonTblList:
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
    arcpy.JoinField_management(in_data=spring_auto_traveller_zone1, in_field="TripKey",
                               join_table=fall_auto_traveller_zone1, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                        "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                        "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                        "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                        "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                        "Income_More_than_200K__percent_"])

    log_message = "Joining Fall and Spring Zone 2 traveller income data"
    logger.info(log_message)

    # Process: Join Field
    arcpy.JoinField_management(in_data=spring_auto_traveller_zone2, in_field="TripKey",
                               join_table=fall_auto_traveller_zone2, join_field="TripKey",
                               fields=["Average_Daily_Zone_Traffic__StL",
                                        "Income_Less_than_20K__percent_", "Income_20K_to_35K__percent_",
                                        "Income_35K_to_50K__percent_", "Income_50K_to_75K__percent_",
                                        "Income_75K_to_100K__percent_", "Income_100K_to_125K__percent_",
                                        "Income_125K_to_150K__percent_", "Income_150K_to_200K__percent_",
                                        "Income_More_than_200K__percent_"])

    log_message = "Resetting the All-Zone Auto Traveller output table"
    logger.info(log_message)

    if arcpy.Exists(cgc_auto_traveller):
        arcpy.Delete_management(cgc_auto_traveller, "Table")

    # Process: Table To Table
    arcpy.TableToTable_conversion(in_rows=temp_cgc_auto_traveller_tbl, out_path=wkspace_gdb, out_name="CGCAutoTraveller", where_clause="", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_More_than_200K__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Volume1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1;Income_Less_than_20K__percent1 \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_Less_than_20K__percent1,-1,-1;Income_20K_to_35K__percent1 \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_20K_to_35K__percent1,-1,-1;Income_35K_to_50K__percent1 \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_35K_to_50K__percent1,-1,-1;Income_50K_to_75K__percent1 \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_50K_to_75K__percent1,-1,-1;Income_75K_to_100K__percent1 \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_75K_to_100K__percent1,-1,-1;Income_100K_to_125K__percent1 \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_100K_to_125K__percent1,-1,-1;Income_125K_to_150K__percent1 \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_125K_to_150K__percent1,-1,-1;Income_150K_to_200K__percent1 \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_150K_to_200K__percent1,-1,-1;Income_More_than_200K__percent1 \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + temp_cgc_auto_traveller_tbl + ",Income_More_than_200K__percent1,-1,-1", config_keyword="")

    log_message = "Combining Zone 1 and Zone 2 traveller income data in {}".format(cgc_auto_traveller)
    logger.info(log_message)

    # Process: Append
    arcpy.Append_management(inputs=[spring_auto_traveller_zone1, spring_auto_traveller_zone2], target=cgc_auto_traveller, schema_type="NO_TEST", field_mapping="Mode_of_Travel \"Mode_of_Travel\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Mode_of_Travel,0,2147483647," + spring_auto_traveller_zone2 + ",Mode_of_Travel,0,2147483647;Intersection_Type \"Intersection_Type\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Intersection_Type,0,2147483647," + spring_auto_traveller_zone2 + ",Intersection_Type,0,2147483647;Zone_ID \"Zone_ID\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Zone_ID,0,2147483647," + spring_auto_traveller_zone2 + ",Zone_ID,0,2147483647;Zone_Name \"Zone_Name\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Zone_Name,-1,-1," + spring_auto_traveller_zone2 + ",Zone_Name,-1,-1;Zone_Is_Pass_Through \"Zone_Is_Pass_Through\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Zone_Is_Pass_Through,0,2147483647," + spring_auto_traveller_zone2 + ",Zone_Is_Pass_Through,0,2147483647;Zone_Direction__degrees_ \"Zone_Direction__degrees_\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Zone_Direction__degrees_,0,2147483647," + spring_auto_traveller_zone2 + ",Zone_Direction__degrees_,0,2147483647;Zone_is_Bi_Direction \"Zone_is_Bi_Direction\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Zone_is_Bi_Direction,0,2147483647," + spring_auto_traveller_zone2 + ",Zone_is_Bi_Direction,0,2147483647;Day_Type \"Day_Type\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Day_Type,0,2147483647," + spring_auto_traveller_zone2 + ",Day_Type,0,2147483647;Day_Part \"Day_Part\" true true false 2147483647 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",Day_Part,0,2147483647," + spring_auto_traveller_zone2 + ",Day_Part,0,2147483647;Average_Daily_Zone_Traffic__StL \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_auto_traveller_zone1 + ",Average_Daily_Zone_Traffic__StL,-1,-1," + spring_auto_traveller_zone2 + ",Average_Daily_Zone_Traffic__StL,-1,-1;Income_Less_than_20K__percent_ \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_Less_than_20K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_Less_than_20K__percent_,-1,-1;Income_20K_to_35K__percent_ \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_20K_to_35K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_20K_to_35K__percent_,-1,-1;Income_35K_to_50K__percent_ \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_35K_to_50K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_35K_to_50K__percent_,-1,-1;Income_50K_to_75K__percent_ \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_50K_to_75K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_50K_to_75K__percent_,-1,-1;Income_75K_to_100K__percent_ \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_75K_to_100K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_75K_to_100K__percent_,-1,-1;Income_100K_to_125K__percent_ \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_100K_to_125K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_100K_to_125K__percent_,-1,-1;Income_125K_to_150K__percent_ \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_125K_to_150K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_125K_to_150K__percent_,-1,-1;Income_150K_to_200K__percent_ \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_150K_to_200K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_150K_to_200K__percent_,-1,-1;Income_More_than_200K__percent_ \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_More_than_200K__percent_,-1,-1," + spring_auto_traveller_zone2 + ",Income_More_than_200K__percent_,-1,-1;TripKey \"TripKey\" true true false 255 Text 0 0,First,#," + spring_auto_traveller_zone1 + ",TripKey,0,255," + spring_auto_traveller_zone2 + ",TripKey,0,255;Average_Daily_Zone_Traffic__StL_Volume1 \"Average_Daily_Zone_Traffic__StL\" true true false 4 Long 0 0,First,#," + spring_auto_traveller_zone1 + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1," + spring_auto_traveller_zone2 + ",Average_Daily_Zone_Traffic__StL_Volume1,-1,-1;Income_Less_than_20K__percent1 \"Income_Less_than_20K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_Less_than_20K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_Less_than_20K__percent1,-1,-1;Income_20K_to_35K__percent1 \"Income_20K_to_35K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_20K_to_35K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_20K_to_35K__percent1,-1,-1;Income_35K_to_50K__percent1 \"Income_35K_to_50K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_35K_to_50K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_35K_to_50K__percent1,-1,-1;Income_50K_to_75K__percent1 \"Income_50K_to_75K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_50K_to_75K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_50K_to_75K__percent1,-1,-1;Income_75K_to_100K__percent1 \"Income_75K_to_100K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_75K_to_100K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_75K_to_100K__percent1,-1,-1;Income_100K_to_125K__percent1 \"Income_100K_to_125K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_100K_to_125K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_100K_to_125K__percent1,-1,-1;Income_125K_to_150K__percent1 \"Income_125K_to_150K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_125K_to_150K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_125K_to_150K__percent1,-1,-1;Income_150K_to_200K__percent1 \"Income_150K_to_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_150K_to_200K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_150K_to_200K__percent1,-1,-1;Income_More_than_200K__percent1 \"Income_More_than_200K__percent_\" true true false 8 Double 0 0,First,#," + spring_auto_traveller_zone1 + ",Income_More_than_200K__percent1,-1,-1," + spring_auto_traveller_zone2 + ",Income_More_than_200K__percent1,-1,-1", subtype="")

    log_message = "Average Auto Traveller income table is ready for processing"
    logger.info(log_message)

    log_message = "Adding fields for calculating annual percent of household incomes to {}".format(cgc_auto_traveller)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_18K_Pct", field_type="FLOAT", field_precision=5,
                              field_scale=4, field_length=None, field_alias="Avg_18K_Pct",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_28K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_28K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_42K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_42K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_58K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_58K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_87K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_87K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_113K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_113K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_137K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_137K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_175K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_175K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="Avg_225K_Pct", field_type="FLOAT",
                              field_precision=5, field_scale=4, field_length=None,
                              field_alias="Avg_225K_Pct", field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Adding the Average Annual Traveller Income field to {}".format(cgc_auto_traveller)
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(in_table=cgc_auto_traveller, field_name="AvgAnnualIncome", field_type="DOUBLE",
                              field_precision=7, field_scale=3, field_length=None, field_alias="AvgAnnualIncome",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

    log_message = "Calculating Average Incomes by category..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_18K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_28K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_42K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_58K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_87K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_113K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_137K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_175K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="Avg_225K_Pct",
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
    arcpy.CalculateField_management(in_table=cgc_auto_traveller, field="AvgAnnualIncome",
            expression="calcTotalIncome(!Avg_18K_Pct!, !Avg_28K_Pct!, !Avg_42K_Pct!, !Avg_58K_Pct!, !Avg_87K_Pct!, !Avg_113K_Pct!, !Avg_137K_Pct!, !Avg_175K_Pct!, !Avg_225K_Pct!)",
            expression_type="PYTHON_9.3", code_block="""def calcTotalIncome(avg1, avg2, avg3, avg4, avg5, avg6, avg7, avg8, avg9):
            retNum = 0.0
            retNum = avg1 + avg2 + avg3 + avg4 + avg5 + avg6 + avg7 + avg8 + avg9
            return retNum""")

    log_message = "The calculation of Average Traveller Income is complete for all zones"
    logger.info(log_message)

    log_message = "Performing housekeeping tasks ..."
    logger.info(log_message)

    for zTbl in seasonTblList:

        log_message = "Deleting {}". format(zTbl)
        logger.info(log_message)

        if arcpy.Exists(zTbl):
            arcpy.Delete_management(zTbl, "Table")

    return "%%%%%%% Process A3 Complete %%%%%%%"


def generateTransferStreets(mstaging_gdb, autoFD, transitFD, logger):

    log_message = "%%%%%%% Process A4 - Create Transfer Streets for Parking Penalties %%%%%%%"
    logger.info(log_message)

    wmcog_blkgrps = os.path.join(mstaging_gdb, "WMCOG_BlockGroups")
    svcarea_taz = os.path.join(mstaging_gdb, "WDC_TAZ_StudyArea")
    ucb_roadcl = os.path.join(mstaging_gdb, "UCB_Roads")
    svcarea_blkgrps = mstaging_gdb + "\\WDC_BlockGroups"
    svcarea_blkgrp_roads = mstaging_gdb + "\\WDC_BlkGrp_Roads"
    transfer_streets = mstaging_gdb + "\\WDC_Transfer_Streets"
    transfer_auto_stations = autoFD + "\\Transfer_Street_Stations"
    ## transfer_transit_stations = transitFD + "\\Transfer_Street_Stations"

    log_message = "Selecting US Block Groups by service area TAZ polygons"
    logger.info(log_message)

    # SWITCH Process to Polygon Intersect: Select Layer By Location
    with arcpy.EnvManager(outputCoordinateSystem='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'):
        # WMCOG_BlockGroups_Layer, Output_Layer_Names, Count = arcpy.SelectLayerByLocation_management(in_layer=[wmcog_blkgrps], overlap_type="INTERSECT", select_features=svcarea_taz, search_distance="", selection_type="NEW_SELECTION", invert_spatial_relationship="NOT_INVERT")

        if arcpy.Exists(svcarea_blkgrps):
            arcpy.Delete_management(svcarea_blkgrps, "FeatureClass")

        log_message = "Converting selection to: {}".format(svcarea_blkgrps)
        logger.info(log_message)

        ### # Process: Feature Class To Feature Class (Feature Class To Feature Class) (conversion)
        ### arcpy.FeatureClassToFeatureClass_conversion(in_features=WMCOG_BlockGroups_Layer, out_path=mstaging_gdb, out_name="WDC_BlockGroups", where_clause="", field_mapping="STATE_FIPS \"State FIPS\" true true false 2 Text 0 0,First,#,WMCOG_BlockGroups_Layer,STATE_FIPS,0,2;CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0,First,#,WMCOG_BlockGroups_Layer,CNTY_FIPS,0,3;STCOFIPS \"County FIPS\" true true false 5 Text 0 0,First,#,WMCOG_BlockGroups_Layer,STCOFIPS,0,5;TRACT \"Tract\" true true false 6 Text 0 0,First,#,WMCOG_BlockGroups_Layer,TRACT,0,6;BLKGRP \"Block Group\" true true false 1 Text 0 0,First,#,WMCOG_BlockGroups_Layer,BLKGRP,0,1;FIPS \"FIPS\" true true false 12 Text 0 0,First,#,WMCOG_BlockGroups_Layer,FIPS,0,12;POP2010 \"POP2010\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,POP2010,-1,-1;POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,POP10_SQMI,-1,-1;POP2012 \"POP2020\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,POP2012,-1,-1;POP12_SQMI \"POP20_SQMI\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,POP12_SQMI,-1,-1;WHITE \"WHITE\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,WHITE,-1,-1;BLACK \"BLACK\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,BLACK,-1,-1;AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AMERI_ES,-1,-1;ASIAN \"ASIAN\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,ASIAN,-1,-1;HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,HAWN_PI,-1,-1;HISPANIC \"HISPANIC\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,HISPANIC,-1,-1;OTHER \"OTHER\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,OTHER,-1,-1;MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,MULT_RACE,-1,-1;MALES \"MALES\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,MALES,-1,-1;FEMALES \"FEMALES\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,FEMALES,-1,-1;AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_UNDER5,-1,-1;AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_5_9,-1,-1;AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_10_14,-1,-1;AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_15_19,-1,-1;AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_20_24,-1,-1;AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_25_34,-1,-1;AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_35_44,-1,-1;AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_45_54,-1,-1;AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_55_64,-1,-1;AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_65_74,-1,-1;AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_75_84,-1,-1;AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,AGE_85_UP,-1,-1;MED_AGE \"MED_AGE\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,MED_AGE,-1,-1;MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,MED_AGE_M,-1,-1;MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,MED_AGE_F,-1,-1;HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,HOUSEHOLDS,-1,-1;AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,AVE_HH_SZ,-1,-1;HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,HSEHLD_1_M,-1,-1;HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,HSEHLD_1_F,-1,-1;MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,MARHH_CHD,-1,-1;MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,MARHH_NO_C,-1,-1;MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,MHH_CHILD,-1,-1;FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,FHH_CHILD,-1,-1;FAMILIES \"FAMILIES\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,FAMILIES,-1,-1;AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,AVE_FAM_SZ,-1,-1;HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,HSE_UNITS,-1,-1;VACANT \"VACANT\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,VACANT,-1,-1;OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,OWNER_OCC,-1,-1;RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0,First,#,WMCOG_BlockGroups_Layer,RENTER_OCC,-1,-1;SQMI \"SQMI\" true true false 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,SQMI,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0,First,#,WMCOG_BlockGroups_Layer,Shape_Area,-1,-1", config_keyword="")

        # Process: Spatial Join
        arcpy.SpatialJoin_analysis(wmcog_blkgrps, svcarea_taz, svcarea_blkgrps, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "STATE_FIPS \"State FIPS\" true true false 2 Text 0 0 ,First,#," + wmcog_blkgrps + ",STATE_FIPS,-1,-1;CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#," + wmcog_blkgrps + ",CNTY_FIPS,-1,-1;STCOFIPS \"County FIPS\" true true false 5 Text 0 0 ,First,#," + wmcog_blkgrps + ",STCOFIPS,-1,-1;TRACT \"Tract\" true true false 6 Text 0 0 ,First,#," + wmcog_blkgrps + ",TRACT,-1,-1;BLKGRP \"Block Group\" true true false 1 Text 0 0 ,First,#," + wmcog_blkgrps + ",BLKGRP,-1,-1;FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#," + wmcog_blkgrps + ",FIPS,-1,-1;POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",POP2010,-1,-1;POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",POP10_SQMI,-1,-1;POP2012 \"POP2020\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",POP2012,-1,-1;POP12_SQMI \"POP20_SQMI\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",POP12_SQMI,-1,-1;WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",WHITE,-1,-1;BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",BLACK,-1,-1;AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AMERI_ES,-1,-1;ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",ASIAN,-1,-1;HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",HAWN_PI,-1,-1;HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",HISPANIC,-1,-1;OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",OTHER,-1,-1;MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",MULT_RACE,-1,-1;MALES \"MALES\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",MALES,-1,-1;FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",FEMALES,-1,-1;AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_UNDER5,-1,-1;AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_5_9,-1,-1;AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_10_14,-1,-1;AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_15_19,-1,-1;AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_20_24,-1,-1;AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_25_34,-1,-1;AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_35_44,-1,-1;AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_45_54,-1,-1;AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_55_64,-1,-1;AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_65_74,-1,-1;AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_75_84,-1,-1;AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",AGE_85_UP,-1,-1;MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",MED_AGE,-1,-1;MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",MED_AGE_M,-1,-1;MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",MED_AGE_F,-1,-1;HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",HOUSEHOLDS,-1,-1;AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",AVE_HH_SZ,-1,-1;HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",HSEHLD_1_M,-1,-1;HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",HSEHLD_1_F,-1,-1;MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",MARHH_CHD,-1,-1;MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",MARHH_NO_C,-1,-1;MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",MHH_CHILD,-1,-1;FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",FHH_CHILD,-1,-1;FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",FAMILIES,-1,-1;AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",AVE_FAM_SZ,-1,-1;HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",HSE_UNITS,-1,-1;VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",VACANT,-1,-1;OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",OWNER_OCC,-1,-1;RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#," + wmcog_blkgrps + ",RENTER_OCC,-1,-1;SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",SQMI,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#," + wmcog_blkgrps + ",Shape_Area,-1,-1;id \"id\" true true false 3 Text 0 0 ,First,#," + svcarea_taz + ",id,-1,-1", "INTERSECT", "", "")

        if arcpy.Exists(svcarea_blkgrp_roads):
            arcpy.Delete_management(svcarea_blkgrp_roads, "FeatureClass")

        log_message = "Clipping Road Centerlines by service area Block Groups to: {}".format(svcarea_blkgrp_roads)
        logger.info(log_message)

        # Process: Clip
        arcpy.Clip_analysis(in_features=ucb_roadcl, clip_features=svcarea_blkgrps, out_feature_class=svcarea_blkgrp_roads, cluster_tolerance="")

        if arcpy.Exists(transfer_streets):
            arcpy.Delete_management(transfer_streets, "FeatureClass")

        log_message = "Spatially Joining US/Employment Block Group information with Road Centerlined to form: {}".format(transfer_streets)
        logger.info(log_message)

        # Process: Spatial Join
        arcpy.SpatialJoin_analysis(target_features=svcarea_blkgrp_roads, join_features=svcarea_blkgrps, out_feature_class=transfer_streets, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", field_mapping="LINEARID \"LINEARID\" true true false 22 Text 0 0,First,#," + svcarea_blkgrp_roads + ",LINEARID,0,22;FULLNAME \"FULLNAME\" true true false 100 Text 0 0,First,#," + svcarea_blkgrp_roads + ",FULLNAME,0,100;RTTYP \"RTTYP\" true true false 1 Text 0 0,First,#," + svcarea_blkgrp_roads + ",RTTYP,0,1;MTFCC \"MTFCC\" true true false 5 Text 0 0,First,#," + svcarea_blkgrp_roads + ",MTFCC,0,5;PREQUAL \"PREQUAL\" true true false 3 Text 0 0,First,#," + svcarea_blkgrp_roads + ",PREQUAL,0,3;PREDIR \"PREDIR\" true true false 2 Text 0 0,First,#," + svcarea_blkgrp_roads + ",PREDIR,0,2;PRETYP \"PRETYP\" true true false 14 Text 0 0,First,#," + svcarea_blkgrp_roads + ",PRETYP,0,14;NAME \"NAME\" true true false 100 Text 0 0,First,#," + svcarea_blkgrp_roads + ",NAME,0,100;SUFTYP \"SUFTYP\" true true false 14 Text 0 0,First,#," + svcarea_blkgrp_roads + ",SUFTYP,0,14;SUFDIR \"SUFDIR\" true true false 2 Text 0 0,First,#," + svcarea_blkgrp_roads + ",SUFDIR,0,2;SUFQUAL \"SUFQUAL\" true true false 3 Text 0 0,First,#," + svcarea_blkgrp_roads + ",SUFQUAL,0,3;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0,First,#," + svcarea_blkgrp_roads + ",SHAPE_Length,-1,-1," + svcarea_blkgrps + ",Shape_Length,-1,-1;STATE_FIPS \"State FIPS\" true true false 2 Text 0 0,First,#," + svcarea_blkgrps + ",STATE_FIPS,0,2;CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0,First,#," + svcarea_blkgrps + ",CNTY_FIPS,0,3;STCOFIPS \"County FIPS\" true true false 5 Text 0 0,First,#," + svcarea_blkgrps + ",STCOFIPS,0,5;TRACT \"Tract\" true true false 6 Text 0 0,First,#," + svcarea_blkgrps + ",TRACT,0,6;BLKGRP \"Block Group\" true true false 1 Text 0 0,First,#," + svcarea_blkgrps + ",BLKGRP,0,1;FIPS \"FIPS\" true true false 12 Text 0 0,First,#," + svcarea_blkgrps + ",FIPS,0,12;POP2010 \"POP2010\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",POP2010,-1,-1;POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0,First,#," + svcarea_blkgrps + ",POP10_SQMI,-1,-1;POP2012 \"POP2020\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",POP2012,-1,-1;POP12_SQMI \"POP20_SQMI\" true true false 8 Double 0 0,First,#," + svcarea_blkgrps + ",POP12_SQMI,-1,-1;MED_AGE \"MED_AGE\" true true false 8 Double 0 0,First,#," + svcarea_blkgrps + ",MED_AGE,-1,-1;HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",HOUSEHOLDS,-1,-1;AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0,First,#," + svcarea_blkgrps + ",AVE_HH_SZ,-1,-1;AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0,First,#," + svcarea_blkgrps + ",AVE_FAM_SZ,-1,-1;HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",HSE_UNITS,-1,-1;VACANT \"VACANT\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",VACANT,-1,-1;OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",OWNER_OCC,-1,-1;RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0,First,#," + svcarea_blkgrps + ",RENTER_OCC,-1,-1;SQMI \"SQMI\" true true false 8 Double 0 0,First,#," + svcarea_blkgrps + ",SQMI,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0,First,#," + svcarea_blkgrps + ",Shape_Area,-1,-1", match_option="WITHIN", search_radius="", distance_field_name="")

        log_message = "Adding/Calculating Average Pop 2020 field to: {}".format(transfer_streets)
        logger.info(log_message)

        # Process: Add Field
        arcpy.AddField_management(in_table=transfer_streets, field_name="Avg_Pop20", field_type="DOUBLE", field_precision=7, field_scale=2, field_length=None, field_alias="Avg_Pop20", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        # Process: Calculate Field
        arcpy.CalculateField_management(in_table=transfer_streets, field="Avg_Pop20", expression="calcAvgPop(!POP2012!)", expression_type="PYTHON_9.3", code_block="""def calcAvgPop(pop2020):
            retVal = 99    
            if pop2020 != None:
                retVal = pop2020
            return retVal""")

        log_message = "Adding/Calculating Employment Density field to: {}".format(transfer_streets)
        logger.info(log_message)

        # Process: Add Field
        arcpy.AddField_management(in_table=transfer_streets, field_name="Emp_Density", field_type="DOUBLE", field_precision=7, field_scale=2, field_length=None, field_alias="Emp_Density", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        # Process: Calculate Field
        arcpy.CalculateField_management(in_table=transfer_streets, field="Emp_Density", expression="calcEmpDensity(!CNTY_FIPS!, !Avg_Pop20!)", expression_type="PYTHON_9.3", code_block="""def calcEmpDensity(fips_cnty, pop2020):
            retVal = 0.0
            if fips_cnty == \"001\":
                retVal = pop2020 * 0.702
            else:
                retVal = pop2020 * 0.77
            return retVal""")

        log_message = "Adding/Calculating Parking Penalty (minutes) field to: {}".format(transfer_streets)
        logger.info(log_message)

        # Process: Add Field
        arcpy.AddField_management(in_table=transfer_streets, field_name="Parking_Penalty_Mins", field_type="SHORT", field_precision=None, field_scale=None, field_length=None, field_alias="Parking_Penalty_Mins", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        # Process: Calculate Field (3) (Calculate Field) (management)
        arcpy.CalculateField_management(in_table=transfer_streets, field="Parking_Penalty_Mins", expression="assignParkPenalty(!Emp_Density!)", expression_type="PYTHON_9.3", code_block="""def assignParkPenalty(eDensity):
            retMin = 0
            blockEmp = int(round(eDensity, 0))
            if (blockEmp < 4618):
                retMin = 1
            elif (blockEmp < 6632):
                retMin = 2
            elif (blockEmp < 11563):
                retMin = 4
            elif (blockEmp < 32986):
                retMin = 6
            else:
                retMin = 8
            return retMin""")

    log_message = "Transfer Streets are ready for WGS 1984 Web Mercator Auxillary Sphere feature datasets"
    logger.info(log_message)

    if arcpy.Exists(transfer_auto_stations):
        arcpy.Delete_management(transfer_auto_stations, "FeatureClass")

    log_message = "Writing service area transfer streets in GCS NAD83 to: {}".format(transfer_auto_stations)
    logger.info(log_message)

    ### # Process: Feature Class To Feature Class (2) (Feature Class To Feature Class) (conversion)
    ### arcpy.FeatureClassToFeatureClass_conversion(in_features=transfer_streets, out_path=autoFD, out_name="Transfer_Street_Stations", where_clause="", field_mapping="LINEARID \"LINEARID\" true true false 22 Text 0 0,First,#," + transfer_streets + ",LINEARID,0,22;FULLNAME \"FULLNAME\" true true false 100 Text 0 0,First,#," + transfer_streets + ",FULLNAME,0,100;PREDIR \"PREDIR\" true true false 2 Text 0 0,First,#," + transfer_streets + ",PREDIR,0,2;PRETYP \"PRETYP\" true true false 14 Text 0 0,First,#," + transfer_streets + ",PRETYP,0,14;NAME \"NAME\" true true false 100 Text 0 0,First,#," + transfer_streets + ",NAME,0,100;SUFTYP \"SUFTYP\" true true false 14 Text 0 0,First,#," + transfer_streets + ",SUFTYP,0,14;SUFDIR \"SUFDIR\" true true false 2 Text 0 0,First,#," + transfer_streets + ",SUFDIR,0,2;SUFQUAL \"SUFQUAL\" true true false 3 Text 0 0,First,#," + transfer_streets + ",SUFQUAL,0,3;STATE_FIPS \"State FIPS\" true true false 2 Text 0 0,First,#," + transfer_streets + ",STATE_FIPS,0,2;CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0,First,#," + transfer_streets + ",CNTY_FIPS,0,3;STCOFIPS \"County FIPS\" true true false 5 Text 0 0,First,#," + transfer_streets + ",STCOFIPS,0,5;TRACT \"Tract\" true true false 6 Text 0 0,First,#," + transfer_streets + ",TRACT,0,6;BLKGRP \"Block Group\" true true false 1 Text 0 0,First,#," + transfer_streets + ",BLKGRP,0,1;FIPS \"FIPS\" true true false 12 Text 0 0,First,#," + transfer_streets + ",FIPS,0,12;POP2010 \"POP2010\" true true false 4 Long 0 0,First,#," + transfer_streets + ",POP2010,-1,-1;POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0,First,#," + transfer_streets + ",POP10_SQMI,-1,-1;POP2012 \"POP2020\" true true false 4 Long 0 0,First,#," + transfer_streets + ",POP2012,-1,-1;POP12_SQMI \"POP20_SQMI\" true true false 8 Double 0 0,First,#," + transfer_streets + ",POP12_SQMI,-1,-1;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0,First,#," + transfer_streets + ",SHAPE_Length,-1,-1;Avg_Pop20 \"Avg_Pop20\" true true false 8 Double 0 0,First,#," + transfer_streets + ",Avg_Pop20,-1,-1;Emp_Density \"Emp_Density\" true true false 8 Double 0 0,First,#," + transfer_streets + ",Emp_Density,-1,-1;Parking_Penalty_Mins \"Parking_Penalty_Mins\" true true false 2 Short 0 0,First,#," + transfer_streets + ",Parking_Penalty_Mins,-1,-1", config_keyword="")

    # Process: Project
    arcpy.Project_management(transfer_streets, transfer_auto_stations,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Transfer Streets for Parking Penalties Ready!"
    logger.info(log_message)

    return "%%%%%%% Process A4 Complete %%%%%%%"


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

    result_a1 = defineServiceArea(workspace_gdb, staging_gdb, data_dir, logger)
    logger.info(result_a1)

    result_a2 = constructAutoTripTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
    logger.info(result_a2)

    result_a3 = constructAutoTravellerTbl(cgcsrcdata, workspace_gdb, template_gdb, logger)
    logger.info(result_a3)

    result_a4 = generateTransferStreets(staging_gdb, localAutoFD, localTransitFD, logger)
    logger.info(result_a4)

