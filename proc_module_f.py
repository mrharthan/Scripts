# ---------------------------------------------------------------------------
# proc_module_f.py -- linearize all travel speed and traveller income metrics
# Author: J. S. Pedigo
# ---------------------------------------------------------------------------
import os
import sys
import arcpy
import math
import string
import cgc_logging

#----------------------------------------------------------------------

def linearizeAutoTripSpeed(proj_wkspc_gdb, logger):

    log_message = "%%%%%%% Process F1 - Linearize Automobile Travel Speed onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    auto_taz_centerline = os.path.join(proj_wkspc_gdb, "Auto_TAZ_Centerline")
    auto_metrics_temp = proj_wkspc_gdb + "\\ProjAutoTripMetrics"
    auto_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCAutoTrip")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying trip metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(auto_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=auto_metrics_temp)

    else:

        log_message = "Refreshing the Auto Trip Metrics template: {}".format(auto_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(auto_taz_centerline, proj_wkspc_gdb, "ProjAutoTripMetrics", "LINEARID IS NULL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + auto_taz_centerline + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + auto_taz_centerline + ",TARGET_FID,-1,-1;LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + auto_taz_centerline + ",LINEARID,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 18 Text 0 0 ,First,#," + auto_taz_centerline + ",ZONE_NAME,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + auto_taz_centerline + ",Shape_Length,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",TO_X,-1,-1;TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",TO_Y,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",TO_M,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=auto_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tp_list = [t.name for t in arcpy.ListFields(auto_metrics_temp)]
    trip_names = ["WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS", "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS", "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"]
    for trip_name in trip_names:
        if trip_name not in tp_list:
            arcpy.AddField_management(auto_metrics_temp, trip_name, "DOUBLE")

    log_message = "Verified {}".format(auto_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjAutoTripMetrics
    ## Search Cursor on Auto_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCAutoTrip metrics fields

    log_message = "Transposing centerline auto trip metrics into {}".format(auto_metrics_temp)
    logger.info(log_message)

    t1 = 0
    clOID = 0
    clShape = ["SHAPE@"]
    clLinearID = None
    clZoneName = None
    clShapeLength = 0.0
    clFromX = 0.0
    clFromY = 0.0
    clToX = 0.0
    clToY = 0.0
    clFromM = 0.0
    clToM = 0.0
    tpZoneStrName = None

    autoClCount = arcpy.GetCount_management(auto_taz_centerline)
    clCount = int(autoClCount[0])

    ndxAutoTrip = arcpy.da.InsertCursor(auto_metrics_temp, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "Shape_Length",
                                                            "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "WkDay_AllDay_AAS",
                                                            "WkDay_EarlyAM_AAS", "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS",
                                                            "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS", "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS",
                                                            "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"])

    rdAutoCL = arcpy.da.SearchCursor(auto_taz_centerline, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "Shape_Length",
                                                           "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"], None, None, "False", (None, None))
    for clRow in rdAutoCL:
        clOID, clShape, clLinearID, clZoneName, clShapeLength, clFromX, clFromY, clToX, clToY, clFromM, clToM = clRow[0], clRow[1], clRow[2], clRow[3], clRow[4], clRow[5], clRow[6], clRow[7], clRow[8], clRow[9], clRow[10]
        if clZoneName == None:
            pass
        else:
            log_message = "Updating Average Speed by Time-Of-Day on LINEARID {}".format(clLinearID)
            logger.info(log_message)

            wkDayAllDayAAS = 0.0
            wkDayEarlyAMAAS = 0.0
            wkDayPeakAMAAS = 0.0
            wkDayMidDayAAS = 0.0
            wkDayPeakPMAAS = 0.0
            wkDayLatePMAAS = 0.0
            wkEndAllDayAAS = 0.0
            wkEndEarlyAMAAS = 0.0
            wkEndPeakAMAAS = 0.0
            wkEndMidDayAAS = 0.0
            wkEndPeakPMAAS = 0.0
            wkEndLatePMAAS = 0.0

            exp = arcpy.AddFieldDelimiters(auto_metrics_tbl, "Zone_Name") + " = " + str(clZoneName)
            rdAutoTripM = arcpy.da.SearchCursor(auto_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualAutoSpeed"], where_clause=exp)
            for tpRow in rdAutoTripM:
                tpOID, tpZoneName, tpDayType, tpDayPart, tpKey, tpAvgAutoSpd = tpRow[0], tpRow[1], tpRow[2], tpRow[3], tpRow[4], tpRow[5]
                if tpKey == None:
                    pass
                else:
                    tpKeySfx = tpKey[-2:]
                    tpZoneStrName = str(tpZoneName)
                    if tpKeySfx == '10':
                        wkDayAllDayAAS = tpAvgAutoSpd
                    elif tpKeySfx == '11':
                        wkDayEarlyAMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '12':
                        wkDayPeakAMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '13':
                        wkDayMidDayAAS = tpAvgAutoSpd
                    elif tpKeySfx == '14':
                        wkDayPeakPMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '15':
                        wkDayLatePMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '20':
                        wkEndAllDayAAS = tpAvgAutoSpd
                    elif tpKeySfx == '21':
                        wkEndEarlyAMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '22':
                        wkEndPeakAMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '23':
                        wkEndMidDayAAS = tpAvgAutoSpd
                    elif tpKeySfx == '24':
                        wkEndPeakPMAAS = tpAvgAutoSpd
                    elif tpKeySfx == '25':
                        wkEndLatePMAAS = tpAvgAutoSpd
                    else:
                        pass

            del tpRow
            del rdAutoTripM

            ndxAutoTrip.insertRow([clOID, clShape, clLinearID, clZoneName, clShapeLength, clFromX, clFromY, clToX, clToY, clFromM, clToM,
                                   wkDayAllDayAAS, wkDayEarlyAMAAS, wkDayPeakAMAAS, wkDayMidDayAAS, wkDayPeakPMAAS, wkDayLatePMAAS,
                                   wkEndAllDayAAS, wkEndEarlyAMAAS, wkEndPeakAMAAS, wkEndMidDayAAS, wkEndPeakPMAAS, wkEndLatePMAAS])
            t1 += 1

    del clRow
    del rdAutoCL

    log_message = "Updated {} centerline records of {} totsl for {}".format(t1, clCount, auto_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    return "%%%%%%% Process F1 - Average Annual Auto Trip Speeds - Linearization Complete %%%%%%%"


def linearizeAutoTravellerIncome(proj_wkspc_gdb, logger):
    log_message = "%%%%%%% Process F2 - Linearize Automobile Traveller Household Income onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    auto_taz_centerline = os.path.join(proj_wkspc_gdb, "Auto_TAZ_Centerline")
    traveller_metrics_temp = proj_wkspc_gdb + "\\ProjAutoTravMetrics"
    traveller_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCAutoTraveller")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying traveller metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(traveller_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=traveller_metrics_temp)

    else:

        log_message = "Refreshing the Auto Traveller Metrics template: {}".format(traveller_metrics_temp)
        logger.info(log_message)

        # # Process: Feature Class to Feature Class (2)
        arcpy.FeatureClassToFeatureClass_conversion(auto_taz_centerline, proj_wkspc_gdb, "ProjAutoTravMetrics", "LINEARID IS NULL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + auto_taz_centerline + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + auto_taz_centerline + ",TARGET_FID,-1,-1;LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + auto_taz_centerline + ",LINEARID,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 18 Text 0 0 ,First,#," + auto_taz_centerline + ",ZONE_NAME,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + auto_taz_centerline + ",Shape_Length,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",TO_X,-1,-1;TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",TO_Y,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + auto_taz_centerline + ",TO_M,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=traveller_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tv_list = [v.name for v in arcpy.ListFields(traveller_metrics_temp)]
    trav_names = ["WkDay_AllDay_AAI", "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI",
                  "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI", "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI",
                  "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI", "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"]
    for trav_name in trav_names:
        if trav_name not in tv_list:
            arcpy.AddField_management(traveller_metrics_temp, trav_name, "DOUBLE")

    log_message = "Verified {}".format(traveller_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjAutoTravMetrics
    ## Search Cursor on Auto_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCAutoTrip, then CGCAutoTraveller for metrics fields

    log_message = "Transposing centerline auto traveller metrics into {}".format(traveller_metrics_temp)
    logger.info(log_message)

    t2 = 0
    clOID = 0
    clShape = ["SHAPE@"]
    clLinearID = None
    clZoneName = None
    clShapeLength = 0.0
    clFromX = 0.0
    clFromY = 0.0
    clToX = 0.0
    clToY = 0.0
    clFromM = 0.0
    clToM = 0.0
    tvZoneStrName = None
    autoClCount = arcpy.GetCount_management(auto_taz_centerline)
    clCount = int(autoClCount[0])

    ndxAutoTrav = arcpy.da.InsertCursor(traveller_metrics_temp, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "Shape_Length",
                                                                 "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "WkDay_AllDay_AAI",
                                                                 "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI",
                                                                 "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI",
                                                                 "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI",
                                                                 "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI",
                                                                 "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"])

    rdAutoCL = arcpy.da.SearchCursor(auto_taz_centerline, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "Shape_Length",
                                                           "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"], None, None, "False", (None, None))
    for clRow in rdAutoCL:
        clOID, clShape, clLinearID, clZoneName, clShapeLength, clFromX, clFromY, clToX, clToY, clFromM, clToM = clRow[0], clRow[1], clRow[2], clRow[3], clRow[4], clRow[5], clRow[6], clRow[7], clRow[8], clRow[9], clRow[10]
        if clZoneName == None:
            pass
        else:
            log_message = "Updating Average Income by Time-Of-Day on LINEARID {}".format(clLinearID)
            logger.info(log_message)

            wkDayAllDayAAI = 0.0
            wkDayEarlyAMAAI = 0.0
            wkDayPeakAMAAI = 0.0
            wkDayMidDayAAI = 0.0
            wkDayPeakPMAAI = 0.0
            wkDayLatePMAAI = 0.0
            wkEndAllDayAAI = 0.0
            wkEndEarlyAMAAI = 0.0
            wkEndPeakAMAAI = 0.0
            wkEndMidDayAAI = 0.0
            wkEndPeakPMAAI = 0.0
            wkEndLatePMAAI = 0.0

            exp = arcpy.AddFieldDelimiters(traveller_metrics_tbl, "Zone_Name") + " = " + str(clZoneName)
            rdAutoTravM = arcpy.da.SearchCursor(traveller_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualIncome"], where_clause=exp)
            for tvRow in rdAutoTravM:
                tvOID, tvZoneName, tvDayType, tvDayPart, tvKey, tvAvgTravInc = tvRow[0], tvRow[1], tvRow[2], tvRow[3], tvRow[4], tvRow[5]
                if tvKey == None:
                    pass
                else:
                    tvKeySfx = tvKey[-2:]
                    ## tvZoneStrName = str(tvZoneName)
                    if tvKeySfx == '10':
                        wkDayAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '11':
                        wkDayEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '12':
                        wkDayPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '13':
                        wkDayMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '14':
                        wkDayPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '15':
                        wkDayLatePMAAI = tvAvgTravInc
                    elif tvKeySfx == '20':
                        wkEndAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '21':
                        wkEndEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '22':
                        wkEndPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '23':
                        wkEndMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '24':
                        wkEndPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '25':
                        wkEndLatePMAAI = tvAvgTravInc
                    else:
                        pass

            del tvRow
            del rdAutoTravM

            ndxAutoTrav.insertRow([clOID, clShape, clLinearID, clZoneName, clShapeLength, clFromX, clFromY, clToX, clToY,
                                   clFromM, clToM, wkDayAllDayAAI, wkDayEarlyAMAAI, wkDayPeakAMAAI, wkDayMidDayAAI,
                                   wkDayPeakPMAAI, wkDayLatePMAAI, wkEndAllDayAAI, wkEndEarlyAMAAI, wkEndPeakAMAAI,
                                   wkEndMidDayAAI, wkEndPeakPMAAI, wkEndLatePMAAI])
            t2 += 1

    del clRow
    del rdAutoCL

    log_message = "Updated {} centerline records of {} totsl for {}".format(t2, clCount, traveller_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    return "%%%%%%% Process F2 - Average Annual Auto Traveller Income - Linearization Complete %%%%%%%"


def linearizePedestrianTripSpeed(proj_wkspc_gdb, logger):

    log_message = "%%%%%%% Process F3 - Linearize Pedestrian Travel Speed onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    ped_taz_centerline = os.path.join(proj_wkspc_gdb, "Ped_TAZ_Centerline")
    ped_metrics_temp = proj_wkspc_gdb + "\\ProjPedTripMetrics"
    ped_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCPedTrip")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying trip metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(ped_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=ped_metrics_temp)

    else:

        log_message = "Refreshing the Pedestrian Trip Metrics template: {}".format(ped_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(ped_taz_centerline, proj_wkspc_gdb, "ProjPedTripMetrics", "RouteID IS NULL", "RouteID \"RouteID\" true true false 22 Text 0 0 ,First,#," + ped_taz_centerline + ",RouteID,-1,-1;RouteName \"RouteName\" true true false 100 Text 0 0 ,First,#," + ped_taz_centerline + ",RouteName,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + ped_taz_centerline + ",RouteModeCD,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + ped_taz_centerline + ",ZONE_NAME,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + ped_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + ped_taz_centerline + ",TO_M,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + ped_taz_centerline + ",Shape_Length,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=ped_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tp_list = [t.name for t in arcpy.ListFields(ped_metrics_temp)]
    trip_names = ["WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS", "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS", "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"]
    for trip_name in trip_names:
        if trip_name not in tp_list:
            arcpy.AddField_management(ped_metrics_temp, trip_name, "DOUBLE")

    log_message = "Verified {}".format(ped_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjPedTripMetrics
    ## Search Cursor on Ped_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCPedTrip metrics fields

    log_message = "Transposing centerline pedestrian trip metrics into {}".format(ped_metrics_temp)
    logger.info(log_message)

    t3 = 0
    pOID = 0
    pShape = ["SHAPE@"]
    pRouteID = None
    pRouteName = None
    pRouteModeCD = None
    pZoneName = None
    pFromM, pToM = 0.0, 0.0
    pShapeLength = 0.0

    pedClCount = arcpy.GetCount_management(ped_taz_centerline)
    pCount = int(pedClCount[0])

    ndxPedTrip = arcpy.da.InsertCursor(ped_metrics_temp, ["OBJECTID", "SHAPE@", "RouteID", "RouteName", "RouteModeCD",
                                      "ZONE_NAME", "FROM_M", "TO_M", "Shape_Length", "WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS",
                                      "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS",
                                      "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"])

    rdPedCL = arcpy.da.SearchCursor(ped_taz_centerline, ["OBJECTID", "SHAPE@", "RouteID", "RouteName", "RouteModeCD",
                                      "ZONE_NAME", "FROM_M", "TO_M", "Shape_Length"], None, None, "False", (None, None))
    for plRow in rdPedCL:
        pOID, pShape, pRouteID, pRouteName, pRouteModeCD, pZoneName, pFromM, pToM, pShapeLength = plRow[0], plRow[1], plRow[2], plRow[3], plRow[4], plRow[5], plRow[6], plRow[7], plRow[8]
        if pZoneName == None:
            pass
        else:
            log_message = "Updating Average Speed by Time-Of-Day on Route ID {}".format(pRouteID)
            logger.info(log_message)

            wkDayAllDayAAS = 0.0
            wkDayEarlyAMAAS = 0.0
            wkDayPeakAMAAS = 0.0
            wkDayMidDayAAS = 0.0
            wkDayPeakPMAAS = 0.0
            wkDayLatePMAAS = 0.0
            wkEndAllDayAAS = 0.0
            wkEndEarlyAMAAS = 0.0
            wkEndPeakAMAAS = 0.0
            wkEndMidDayAAS = 0.0
            wkEndPeakPMAAS = 0.0
            wkEndLatePMAAS = 0.0

            exp = arcpy.AddFieldDelimiters(ped_metrics_tbl, "Zone_Name") + " = " + str(pZoneName)
            rdPedTripM = arcpy.da.SearchCursor(ped_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualPedSpeed"], where_clause=exp)
            for ipRow in rdPedTripM:
                ipOID, ipZoneName, ipDayType, ipDayPart, ipKey, ipAvgPedSpd = ipRow[0], ipRow[1], ipRow[2], ipRow[3], ipRow[4], ipRow[5]
                if ipKey == None:
                    pass
                else:
                    ipKeySfx = ipKey[-2:]
                    if ipKeySfx == '10':
                        wkDayAllDayAAS = ipAvgPedSpd
                    elif ipKeySfx == '11':
                        wkDayEarlyAMAAS = ipAvgPedSpd
                    elif ipKeySfx == '12':
                        wkDayPeakAMAAS = ipAvgPedSpd
                    elif ipKeySfx == '13':
                        wkDayMidDayAAS = ipAvgPedSpd
                    elif ipKeySfx == '14':
                        wkDayPeakPMAAS = ipAvgPedSpd
                    elif ipKeySfx == '15':
                        wkDayLatePMAAS = ipAvgPedSpd
                    elif ipKeySfx == '20':
                        wkEndAllDayAAS = ipAvgPedSpd
                    elif ipKeySfx == '21':
                        wkEndEarlyAMAAS = ipAvgPedSpd
                    elif ipKeySfx == '22':
                        wkEndPeakAMAAS = ipAvgPedSpd
                    elif ipKeySfx == '23':
                        wkEndMidDayAAS = ipAvgPedSpd
                    elif ipKeySfx == '24':
                        wkEndPeakPMAAS = ipAvgPedSpd
                    elif ipKeySfx == '25':
                        wkEndLatePMAAS = ipAvgPedSpd
                    else:
                        pass

            del ipRow
            del rdPedTripM

            ndxPedTrip.insertRow([pOID, pShape, pRouteID, pRouteName, pRouteModeCD, pZoneName, pFromM, pToM, pShapeLength,
                                  wkDayAllDayAAS, wkDayEarlyAMAAS, wkDayPeakAMAAS, wkDayMidDayAAS, wkDayPeakPMAAS, wkDayLatePMAAS,
                                  wkEndAllDayAAS, wkEndEarlyAMAAS, wkEndPeakAMAAS, wkEndMidDayAAS, wkEndPeakPMAAS, wkEndLatePMAAS])

            t3 += 1

    del plRow
    del rdPedCL

    log_message = "Updated {} centerline records of {} total for {}".format(t3, pCount, ped_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    return "%%%%%%% Process F3 - Average Annual Pedestrian Trip Speeds - Linearization Complete %%%%%%%"

def linearizePedestrianIncome(proj_wkspc_gdb, logger):
    log_message = "%%%%%%% Process F4 - Linearize Pedestrian Household Income onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    ped_taz_centerline = os.path.join(proj_wkspc_gdb, "Ped_TAZ_Centerline")
    pedestrian_metrics_temp = proj_wkspc_gdb + "\\ProjPedTravellerMetrics"
    pedestrian_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCPedTraveller")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying traveller metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(pedestrian_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=pedestrian_metrics_temp)

    else:

        log_message = "Refreshing the Pedestrian Traveller Metrics template: {}".format(pedestrian_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class (2)
        arcpy.FeatureClassToFeatureClass_conversion(ped_taz_centerline, proj_wkspc_gdb, "ProjPedTravellerMetrics", "RouteID IS NULL", "RouteID \"RouteID\" true true false 22 Text 0 0 ,First,#," + ped_taz_centerline + ",RouteID,-1,-1;RouteName \"RouteName\" true true false 100 Text 0 0 ,First,#," + ped_taz_centerline + ",RouteName,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + ped_taz_centerline + ",RouteModeCD,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + ped_taz_centerline + ",ZONE_NAME,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + ped_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + ped_taz_centerline + ",TO_M,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + ped_taz_centerline + ",Shape_Length,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=pedestrian_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tv_list = [v.name for v in arcpy.ListFields(pedestrian_metrics_temp)]
    trav_names = ["WkDay_AllDay_AAI", "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI",
                  "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI", "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI",
                  "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI", "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"]
    for trav_name in trav_names:
        if trav_name not in tv_list:
            arcpy.AddField_management(pedestrian_metrics_temp, trav_name, "DOUBLE")

    log_message = "Verified {}".format(pedestrian_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjAutoTravMetrics
    ## Search Cursor on Auto_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCAutoTrip, then CGCAutoTraveller for metrics fields

    log_message = "Transposing centerline pedestrian traveller metrics into {}".format(pedestrian_metrics_temp)
    logger.info(log_message)

    t4 = 0
    piOID = 0
    piShape = ["SHAPE@"]
    piRouteID = None
    piRouteName = None
    piRouteModeCD = None
    piZoneName = None
    piFrmDFO = 0.0
    piToDFO = 0.0
    piShapeLength = 0.0
    tvZoneStrName = None

    pedClCount = arcpy.GetCount_management(ped_taz_centerline)
    piCount = int(pedClCount[0])

    ndxPedTrav = arcpy.da.InsertCursor(pedestrian_metrics_temp, ["OBJECTID", "SHAPE@", "RouteID", "RouteName", "RouteModeCD",
                                                                 "ZONE_NAME", "FROM_M", "TO_M", "Shape_Length", "WkDay_AllDay_AAI",
                                                                 "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI",
                                                                 "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI",
                                                                 "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI",
                                                                 "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI",
                                                                 "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"])

    rdPedeCL = arcpy.da.SearchCursor(ped_taz_centerline, ["OBJECTID", "SHAPE@", "RouteID", "RouteName", "RouteModeCD",
                                                           "ZONE_NAME", "FROM_M", "TO_M", "Shape_Length"], None, None, "False", (None, None))
    for piRow in rdPedeCL:
        piOID, piShape, piRouteID, piRouteName, piRouteModeCD, piZoneName, piFrmDFO, piToDFO, piShapeLength = piRow[0], piRow[1], piRow[2], piRow[3], piRow[4], piRow[5], piRow[6], piRow[7], piRow[8]
        if piZoneName == None:
            pass
        else:
            log_message = "Updating Average Income by Time-Of-Day on Zone: {}".format(str(piZoneName))
            logger.info(log_message)

            wkDayAllDayAAI = 0.0
            wkDayEarlyAMAAI = 0.0
            wkDayPeakAMAAI = 0.0
            wkDayMidDayAAI = 0.0
            wkDayPeakPMAAI = 0.0
            wkDayLatePMAAI = 0.0
            wkEndAllDayAAI = 0.0
            wkEndEarlyAMAAI = 0.0
            wkEndPeakAMAAI = 0.0
            wkEndMidDayAAI = 0.0
            wkEndPeakPMAAI = 0.0
            wkEndLatePMAAI = 0.0

            exp = arcpy.AddFieldDelimiters(pedestrian_metrics_tbl, "Zone_Name") + " = " + str(piZoneName)
            rdPedTravM = arcpy.da.SearchCursor(pedestrian_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualIncome"], where_clause=exp)
            for tvRow in rdPedTravM:
                tvOID, tvZoneName, tvDayType, tvDayPart, tvKey, tvAvgTravInc = tvRow[0], tvRow[1], tvRow[2], tvRow[3], tvRow[4], tvRow[5]
                if tvKey == None:
                    pass
                else:
                    tvKeySfx = tvKey[-2:]
                    tvZoneStrName = str(tvZoneName)
                    if tvKeySfx == '10':
                        wkDayAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '11':
                        wkDayEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '12':
                        wkDayPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '13':
                        wkDayMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '14':
                        wkDayPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '15':
                        wkDayLatePMAAI = tvAvgTravInc
                    elif tvKeySfx == '20':
                        wkEndAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '21':
                        wkEndEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '22':
                        wkEndPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '23':
                        wkEndMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '24':
                        wkEndPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '25':
                        wkEndLatePMAAI = tvAvgTravInc
                    else:
                        pass

            del tvRow
            del rdPedTravM

            ndxPedTrav.insertRow([piOID, piShape, piRouteID, piRouteName, piRouteModeCD, piZoneName, piFrmDFO, piToDFO,
                                  piShapeLength, wkDayAllDayAAI, wkDayEarlyAMAAI, wkDayPeakAMAAI, wkDayMidDayAAI, wkDayPeakPMAAI,
                                  wkDayLatePMAAI, wkEndAllDayAAI, wkEndEarlyAMAAI, wkEndPeakAMAAI, wkEndMidDayAAI, wkEndPeakPMAAI, wkEndLatePMAAI])

            t4 += 1

    del piRow
    del rdPedeCL

    log_message = "Updated {} centerline records of {} totsl for {}".format(t4, piCount, pedestrian_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    return "%%%%%%% Process F4 - Average Annual Pedestrian Traveller Income - Linearization Complete %%%%%%%"


def linearizeBusTripSpeed(proj_wkspc_gdb, logger):

    log_message = "%%%%%%% Process F5 - Linearize Bus Travel Speed onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    bus_taz_centerline = os.path.join(proj_wkspc_gdb, "Bus_TAZ_Centerline")
    bus_metrics_temp = proj_wkspc_gdb + "\\ProjBusTripMetrics"
    bus_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCBusTrip")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying trip metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(bus_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=bus_metrics_temp)

    else:

        log_message = "Refreshing the Bus Trip Metrics template: {}".format(bus_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(bus_taz_centerline, proj_wkspc_gdb, "ProjBusTripMetrics", "BusRouteID1 IS NULL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + bus_taz_centerline + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + bus_taz_centerline + ",TARGET_FID,-1,-1;OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",OperRtNM,-1,-1; \
        stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_EarlyAM_WaitTime_WD,-1,-1; \
        Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_PeakPM_WaitTime_WD,-1,-1; \
        Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_EarlyAM_WaitTime_WE,-1,-1; \
        Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_PeakPM_WaitTime_WE,-1,-1; \
        Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",direction_id_all,-1,-1; \
        location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_centerline + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + bus_taz_centerline + ",wheelchair_boarding,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",stop_lon,-1,-1; \
        stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_centerline + ",stop_url,-1,-1;parent_station \"parent_station\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_centerline + ",parent_station,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID1,-1,-1;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID2,-1,-1; \
        BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID3,-1,-1;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID4,-1,-1;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID5,-1,-1;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID6,-1,-1; \
        BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID7,-1,-1;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID8,-1,-1;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID9,-1,-1;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID10,-1,-1; \
        ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + bus_taz_centerline + ",ZONE_NAME,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Shape_Length,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",TO_X,-1,-1; \
        TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",TO_Y,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",TO_M,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + bus_taz_centerline + ",RouteModeCD,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=bus_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tp_list = [t.name for t in arcpy.ListFields(bus_metrics_temp)]
    trip_names = ["WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS", "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS", "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"]
    for trip_name in trip_names:
        if trip_name not in tp_list:
            arcpy.AddField_management(bus_metrics_temp, trip_name, "DOUBLE")

    log_message = "Verified {}".format(bus_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjBusTripMetrics
    ## Search Cursor on Bus_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCBusTrip metrics fields

    log_message = "Transposing centerline bus trip metrics into {}".format(bus_metrics_temp)
    logger.info(log_message)

    t5 = 0
    bOID = 0
    bShape = ["SHAPE@"]
    bOpenRteNM = None
    bStopID = None
    wkDayAllDayWaitTime = 0.0
    wkDayEarlyAMWaitTime = 0.0
    wkDayPeakAMWaitTime= 0.0
    wkDayMidDayWaitTime = 0.0
    wkDayPeakPMWaitTime = 0.0
    wkDayLatePMWaitTime = 0.0
    wkEndAllDayWaitTime = 0.0
    wkEndEarlyAMWaitTime = 0.0
    wkEndPeakAMWaitTime = 0.0
    wkEndMidDayWaitTime = 0.0
    wkEndPeakPMWaitTime = 0.0
    wkEndLatePMWaitTime = 0.0
    bAgency = None
    bRouteIdAll = None
    bDirIdAll = None
    bLocationType = None
    bWhlChairBrd = 0
    bStopLat = 0.0
    bStopLon = 0.0
    bStopURL = None
    bParentStation = None
    bRouteID1 = None
    bRouteID2 = None
    bRouteID3 = None
    bRouteID4 = None
    bRouteID5 = None
    bRouteID6 = None
    bRouteID7 = None
    bRouteID8 = None
    bRouteID9 = None
    bRouteID10 = None
    bZoneName = None
    bShapeLength = 0.0
    bFromX, bFromY = 0.0, 0.0
    bToX, bToY = 0.0, 0.0
    bFromM, bToM = 0.0, 0.0
    bRouteModeCD = None
    busClCount = arcpy.GetCount_management(bus_taz_centerline)
    bCount = int(busClCount[0])

    ndxBusTrip = arcpy.da.InsertCursor(bus_metrics_temp, ["OBJECTID", "SHAPE@", "OperRtNM", "stop_id", "Avg_AllDay_WaitTime_WD", "Avg_EarlyAM_WaitTime_WD",
                                        "Avg_PeakAM_WaitTime_WD", "Avg_MidDay_WaitTime_WD", "Avg_PeakPM_WaitTime_WD", "Avg_LatePM_WaitTime_WD", "Avg_AllDay_WaitTime_WE",
                                        "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE", "Avg_MidDay_WaitTime_WE", "Avg_PeakPM_WaitTime_WE", "Avg_LatePM_WaitTime_WE",
                                        "agency", "route_id_all", "direction_id_all", "location_type", "wheelchair_boarding", "stop_lat", "stop_lon", "stop_url", "parent_station",
                                        "BusRouteID1", "BusRouteID2", "BusRouteID3", "BusRouteID4", "BusRouteID5", "BusRouteID6", "BusRouteID7", "BusRouteID8", "BusRouteID9", "BusRouteID10",
                                        "ZONE_NAME", "Shape_Length", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "RouteModeCD", "WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS",
                                        "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS",
                                        "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"])

    rdBusCL = arcpy.da.SearchCursor(bus_taz_centerline, ["OBJECTID", "SHAPE@", "OperRtNM", "stop_id", "Avg_AllDay_WaitTime_WD", "Avg_EarlyAM_WaitTime_WD",
                                    "Avg_PeakAM_WaitTime_WD", "Avg_MidDay_WaitTime_WD", "Avg_PeakPM_WaitTime_WD", "Avg_LatePM_WaitTime_WD", "Avg_AllDay_WaitTime_WE",
                                    "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE", "Avg_MidDay_WaitTime_WE", "Avg_PeakPM_WaitTime_WE", "Avg_LatePM_WaitTime_WE",
                                    "agency", "route_id_all", "direction_id_all", "location_type", "wheelchair_boarding", "stop_lat", "stop_lon", "stop_url", "parent_station",
                                    "BusRouteID1", "BusRouteID2", "BusRouteID3", "BusRouteID4", "BusRouteID5", "BusRouteID6", "BusRouteID7", "BusRouteID8", "BusRouteID9", "BusRouteID10",
                                    "ZONE_NAME", "Shape_Length", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "RouteModeCD"], None, None, "False", (None, None))
    for blRow in rdBusCL:
        bOID, bShape, bOpenRteNM, bStopID, wkDayAllDayWaitTime, wkDayEarlyAMWaitTime, wkDayPeakAMWaitTime, wkDayMidDayWaitTime, wkDayPeakPMWaitTime, wkDayLatePMWaitTime, \
        wkEndAllDayWaitTime, wkEndEarlyAMWaitTime, wkEndPeakAMWaitTime, wkEndMidDayWaitTime, wkEndPeakPMWaitTime, wkEndLatePMWaitTime, bAgency, bRouteIdAll, bDirIdAll, bLocationType, \
        bWhlChairBrd, bStopLat, bStopLon, bStopURL, bParentStation, bRouteID1, bRouteID2, bRouteID3, bRouteID4, bRouteID5, bRouteID6, bRouteID7, bRouteID8, bRouteID9, bRouteID10, \
        bZoneName, bShapeLength, bFromX, bFromY, bToX, bToY, bFromM, bToM, bRouteModeCD = blRow[0], blRow[1], blRow[2], blRow[3], blRow[4], blRow[5], blRow[6], blRow[7], blRow[8], blRow[9], blRow[10], \
        blRow[11], blRow[12], blRow[13], blRow[14], blRow[15], blRow[16], blRow[17], blRow[18], blRow[19], blRow[20], blRow[21], blRow[22], blRow[23], blRow[24], blRow[25], blRow[26], blRow[27], \
        blRow[28], blRow[29], blRow[30], blRow[31], blRow[32], blRow[33], blRow[34], blRow[35], blRow[36], blRow[37], blRow[38], blRow[39], blRow[40], blRow[41], blRow[42], blRow[43]
        if bZoneName == None:
            pass
        else:
            log_message = "Updating Average Speed by Time-Of-Day in Zone: {}".format(str(bZoneName))
            logger.info(log_message)

            wkDayAllDayAAS = 0.0
            wkDayEarlyAMAAS = 0.0
            wkDayPeakAMAAS = 0.0
            wkDayMidDayAAS = 0.0
            wkDayPeakPMAAS = 0.0
            wkDayLatePMAAS = 0.0
            wkEndAllDayAAS = 0.0
            wkEndEarlyAMAAS = 0.0
            wkEndPeakAMAAS = 0.0
            wkEndMidDayAAS = 0.0
            wkEndPeakPMAAS = 0.0
            wkEndLatePMAAS = 0.0

            exp = arcpy.AddFieldDelimiters(bus_metrics_tbl, "Zone_Name") + " = " + str(bZoneName)
            rdBusTripM = arcpy.da.SearchCursor(bus_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualBusSpeed"], where_clause=exp)
            for ibRow in rdBusTripM:
                ibOID, ibZoneName, ibDayType, ibDayPart, ibKey, ibAvgBusSpd = ibRow[0], ibRow[1], ibRow[2], ibRow[3], ibRow[4], ibRow[5]
                if ibKey == None:
                    pass
                else:
                    ibKeySfx = ibKey[-2:]
                    if ibKeySfx == '10':
                        wkDayAllDayAAS = ibAvgBusSpd
                    elif ibKeySfx == '11':
                        wkDayEarlyAMAAS = ibAvgBusSpd
                    elif ibKeySfx == '12':
                        wkDayPeakAMAAS = ibAvgBusSpd
                    elif ibKeySfx == '13':
                        wkDayMidDayAAS = ibAvgBusSpd
                    elif ibKeySfx == '14':
                        wkDayPeakPMAAS = ibAvgBusSpd
                    elif ibKeySfx == '15':
                        wkDayLatePMAAS = ibAvgBusSpd
                    elif ibKeySfx == '20':
                        wkEndAllDayAAS = ibAvgBusSpd
                    elif ibKeySfx == '21':
                        wkEndEarlyAMAAS = ibAvgBusSpd
                    elif ibKeySfx == '22':
                        wkEndPeakAMAAS = ibAvgBusSpd
                    elif ibKeySfx == '23':
                        wkEndMidDayAAS = ibAvgBusSpd
                    elif ibKeySfx == '24':
                        wkEndPeakPMAAS = ibAvgBusSpd
                    elif ibKeySfx == '25':
                        wkEndLatePMAAS = ibAvgBusSpd
                    else:
                        pass

            del ibRow
            del rdBusTripM

            ndxBusTrip.insertRow([bOID, bShape, bOpenRteNM, bStopID, wkDayAllDayWaitTime, wkDayEarlyAMWaitTime, wkDayPeakAMWaitTime, wkDayMidDayWaitTime, wkDayPeakPMWaitTime, wkDayLatePMWaitTime,
                                wkEndAllDayWaitTime, wkEndEarlyAMWaitTime, wkEndPeakAMWaitTime, wkEndMidDayWaitTime, wkEndPeakPMWaitTime, wkEndLatePMWaitTime, bAgency, bRouteIdAll, bDirIdAll, bLocationType,
                                bWhlChairBrd, bStopLat, bStopLon, bStopURL, bParentStation, bRouteID1, bRouteID2, bRouteID3, bRouteID4, bRouteID5, bRouteID6, bRouteID7, bRouteID8, bRouteID9, bRouteID10,
                                bZoneName, bShapeLength, bFromX, bFromY, bToX, bToY, bFromM, bToM, bRouteModeCD, wkDayAllDayAAS, wkDayEarlyAMAAS, wkDayPeakAMAAS, wkDayMidDayAAS, wkDayPeakPMAAS, wkDayLatePMAAS,
                                wkEndAllDayAAS, wkEndEarlyAMAAS, wkEndPeakAMAAS, wkEndMidDayAAS, wkEndPeakPMAAS, wkEndLatePMAAS])

            t5 += 1

    del blRow
    del rdBusCL

    log_message = "Updated {} centerline records of {} total for {}".format(t5, bCount, bus_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    log_message = "Adding/Calculating the MetricKey field in {}".format(bus_metrics_temp)
    logger.info(log_message)

    metric_list = [b.name for b in arcpy.ListFields(bus_metrics_temp)]
    metric_nms = ["MetricKey"]
    for metric_nm in metric_nms:
        if metric_nm not in metric_list:
            arcpy.AddField_management(bus_metrics_temp, "MetricKey", "TEXT", "", "", "250", "MetricKey", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field
    arcpy.CalculateField_management(bus_metrics_temp, "MetricKey", "!BusRouteID1! + \"-\" + !ZONE_NAME!", "PYTHON_9.3", "")

    return "%%%%%%% Process F5 - Average Annual Bus Trip Speeds - Linearization Complete %%%%%%%"


def linearizeBusTravellerIncome(proj_wkspc_gdb, logger):
    log_message = "%%%%%%% Process F6 - Linearize Bus Household Income onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    bus_taz_centerline = os.path.join(proj_wkspc_gdb, "Bus_TAZ_Centerline")
    bus_metrics_temp = proj_wkspc_gdb + "\\ProjBusTravellerMetrics"
    bus_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCBusTraveller")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying traveller metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(bus_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=bus_metrics_temp)

    else:

        log_message = "Refreshing the Bus Traveller Metrics template: {}".format(bus_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(bus_taz_centerline, proj_wkspc_gdb, "ProjBusTravellerMetrics", "BusRouteID1 IS NULL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + bus_taz_centerline + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + bus_taz_centerline + ",TARGET_FID,-1,-1;OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",OperRtNM,-1,-1; \
        stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",stop_id,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_taz_centerline + ",direction_id_all,-1,-1; \
        location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_centerline + ",location_type,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",stop_lon,-1,-1;stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_centerline + ",stop_url,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_taz_centerline + ",BusRouteID1,-1,-1; \
        ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + bus_taz_centerline + ",ZONE_NAME,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + bus_taz_centerline + ",Shape_Length,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",TO_X,-1,-1; \
        TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",TO_Y,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + bus_taz_centerline + ",TO_M,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=bus_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tv_list = [v.name for v in arcpy.ListFields(bus_metrics_temp)]
    trav_names = ["WkDay_AllDay_AAI", "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI",
                  "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI", "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI",
                  "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI", "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"]
    for trav_name in trav_names:
        if trav_name not in tv_list:
            arcpy.AddField_management(bus_metrics_temp, trav_name, "DOUBLE")

    log_message = "Verified {}".format(bus_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjABusTravMetrics
    ## Search Cursor on Bus_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCBusTraveller for metrics fields

    log_message = "Transposing centerline bus traveller metrics into {}".format(bus_metrics_temp)
    logger.info(log_message)

    t6 = 0
    biOID = 0
    biShape = ["SHAPE@"]
    biOpenRteID = None
    biStopID = None
    biAgency = None
    biRouteIdAll = None
    biDirIdall = None
    biLocationType = None
    biLat, biLon = 0.0, 0.0
    biURL = None
    biRouteID1 = None
    biZoneName = None
    biShapeLength = 0.0
    biFromX, biFromY = 0.0, 0.0
    biToX, biToY = 0.0, 0.0
    biFromM, biToM = 0.0, 0.0

    busClCount = arcpy.GetCount_management(bus_taz_centerline)
    biCount = int(busClCount[0])

    ndxBusTrav = arcpy.da.InsertCursor(bus_metrics_temp, ["OBJECTID", "SHAPE@", "OperRtNM", "stop_id", "agency", "route_id_all", "direction_id_all", "location_type", "stop_lat", "stop_lon", "stop_url",
                                                          "BusRouteID1", "ZONE_NAME", "Shape_Length", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "WkDay_AllDay_AAI", "WkDay_EarlyAM_AAI",
                                                          "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI", "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI", "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI", "WkEnd_PeakAM_AAI",
                                                          "WkEnd_MidDay_AAI", "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"])

    rdBusCL = arcpy.da.SearchCursor(bus_taz_centerline, ["OBJECTID", "SHAPE@", "OperRtNM", "stop_id", "agency", "route_id_all", "direction_id_all", "location_type", "stop_lat", "stop_lon", "stop_url",
                                                         "BusRouteID1", "ZONE_NAME", "Shape_Length", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"], None, None, "False", (None, None))
    for biRow in rdBusCL:
        biOID, biShape, biOpenRteID, biStopID, biAgency, biRouteIdAll, biDirIdall, biLocationType, biLat, biLon, biURL, biRouteID1, biZoneName, biShapeLength, biFromX, biFromY, biToX, biToY, biFromM, biToM = \
        biRow[0], biRow[1], biRow[2], biRow[3], biRow[4], biRow[5], biRow[6], biRow[7], biRow[8], biRow[9], biRow[10], biRow[11], biRow[12], biRow[13], biRow[14], biRow[15], biRow[16], biRow[17], biRow[18], biRow[19]
        if biZoneName == None:
            pass
        else:
            log_message = "Updating Average Income by Time-Of-Day on Zone {}".format(str(biZoneName))
            logger.info(log_message)

            wkDayAllDayAAI = 0.0
            wkDayEarlyAMAAI = 0.0
            wkDayPeakAMAAI = 0.0
            wkDayMidDayAAI = 0.0
            wkDayPeakPMAAI = 0.0
            wkDayLatePMAAI = 0.0
            wkEndAllDayAAI = 0.0
            wkEndEarlyAMAAI = 0.0
            wkEndPeakAMAAI = 0.0
            wkEndMidDayAAI = 0.0
            wkEndPeakPMAAI = 0.0
            wkEndLatePMAAI = 0.0

            exp = arcpy.AddFieldDelimiters(bus_metrics_tbl, "Zone_Name") + " = " + str(biZoneName)
            rdBusTravM = arcpy.da.SearchCursor(bus_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualIncome"], where_clause=exp)
            for tvRow in rdBusTravM:
                tvOID, tvZoneName, tvDayType, tvDayPart, tvKey, tvAvgTravInc = tvRow[0], tvRow[1], tvRow[2], tvRow[3], tvRow[4], tvRow[5]
                if tvKey == None:
                    pass
                else:
                    tvKeySfx = tvKey[-2:]
                    tvZoneStrName = str(tvZoneName)
                    if tvKeySfx == '10':
                        wkDayAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '11':
                        wkDayEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '12':
                        wkDayPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '13':
                        wkDayMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '14':
                        wkDayPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '15':
                        wkDayLatePMAAI = tvAvgTravInc
                    elif tvKeySfx == '20':
                        wkEndAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '21':
                        wkEndEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '22':
                        wkEndPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '23':
                        wkEndMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '24':
                        wkEndPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '25':
                        wkEndLatePMAAI = tvAvgTravInc
                    else:
                        pass

            del tvRow
            del rdBusTravM

            ndxBusTrav.insertRow([biOID, biShape, biOpenRteID, biStopID, biAgency, biRouteIdAll, biDirIdall, biLocationType,
                                  biLat, biLon, biURL, biRouteID1, biZoneName, biShapeLength, biFromX, biFromY, biToX, biToY, biFromM, biToM,
                                  wkDayAllDayAAI, wkDayEarlyAMAAI, wkDayPeakAMAAI, wkDayMidDayAAI, wkDayPeakPMAAI, wkDayLatePMAAI, wkEndAllDayAAI,
                                  wkEndEarlyAMAAI, wkEndPeakAMAAI, wkEndMidDayAAI, wkEndPeakPMAAI, wkEndLatePMAAI])

            t6 += 1

    del biRow
    del rdBusCL

    log_message = "Updated {} centerline records of {} totsl for {}".format(t6, biCount, bus_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    return "%%%%%%% Process F6 - Average Annual Bus Traveller Income - Linearization Complete %%%%%%%"


def linearizeRailTripSpeed(proj_wkspc_gdb, logger):

    log_message = "%%%%%%% Process F7 - Linearize Rail Travel Speed onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    rail_taz_centerline = os.path.join(proj_wkspc_gdb, "Rail_TAZ_Centerline")
    rail_metrics_temp = proj_wkspc_gdb + "\\ProjRailTripMetrics"
    rail_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCRailTrip")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying trip metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(rail_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=rail_metrics_temp)

    else:

        log_message = "Refreshing the Rail Trip Metrics template: {}".format(rail_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(rail_taz_centerline, proj_wkspc_gdb, "ProjRailTripMetrics", "LINEARID IS NULL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + rail_taz_centerline + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + rail_taz_centerline + ",TARGET_FID,-1,-1;LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + rail_taz_centerline + ",LINEARID,-1,-1; \
        ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + rail_taz_centerline + ",ZONE_NAME,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",TO_X,-1,-1;TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",TO_Y,-1,-1; \
        FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",TO_M,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + rail_taz_centerline + ",Shape_Length,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=rail_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tp_list = [t.name for t in arcpy.ListFields(rail_metrics_temp)]
    trip_names = ["WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS", "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS", "WkEnd_AllDay_AAS", "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"]
    for trip_name in trip_names:
        if trip_name not in tp_list:
            arcpy.AddField_management(rail_metrics_temp, trip_name, "DOUBLE")

    log_message = "Verified {}".format(rail_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjRailTripMetrics
    ## Search Cursor on Rail_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCRailTrip metrics fields

    log_message = "Transposing centerline rail trip metrics into {}".format(rail_metrics_temp)
    logger.info(log_message)

    t7 = 0
    rOID = 0
    rShape = ["SHAPE@"]
    rLinearID = None
    rZoneName = None
    rFromX, rFromY = 0.0, 0.0
    rToX, rToY = 0.0, 0.0
    rFromM, rToM = 0.0, 0.0
    rShapeLength = 0.0

    railClCount = arcpy.GetCount_management(rail_taz_centerline)
    rCount = int(railClCount[0])

    ndxRailTrip = arcpy.da.InsertCursor(rail_metrics_temp, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "Shape_Length",
                                                            "WkDay_AllDay_AAS", "WkDay_EarlyAM_AAS", "WkDay_PeakAM_AAS", "WkDay_MidDay_AAS", "WkDay_PeakPM_AAS", "WkDay_LatePM_AAS",
                                                            "WkEnd_AllDay_AAS", "WkEnd_EarlyAM_AAS", "WkEnd_PeakAM_AAS", "WkEnd_MidDay_AAS", "WkEnd_PeakPM_AAS", "WkEnd_LatePM_AAS"])

    rdRailCL = arcpy.da.SearchCursor(rail_taz_centerline, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "Shape_Length"], None, None, "False", (None, None))
    for rlRow in rdRailCL:
        rOID, rShape, rLinearID, rZoneName, rFromX, rFromY, rToX, rToY, rFromM, rToM, rShapeLength = rlRow[0], rlRow[1], rlRow[2], rlRow[3], rlRow[4], rlRow[5], rlRow[5], rlRow[7], rlRow[8], rlRow[9], rlRow[10]
        if rZoneName == None:
            pass
        else:
            log_message = "Updating Average Speed by Time-Of-Day in Zone: {}".format(str(rZoneName))
            logger.info(log_message)

            wkDayAllDayAAS = 0.0
            wkDayEarlyAMAAS = 0.0
            wkDayPeakAMAAS = 0.0
            wkDayMidDayAAS = 0.0
            wkDayPeakPMAAS = 0.0
            wkDayLatePMAAS = 0.0
            wkEndAllDayAAS = 0.0
            wkEndEarlyAMAAS = 0.0
            wkEndPeakAMAAS = 0.0
            wkEndMidDayAAS = 0.0
            wkEndPeakPMAAS = 0.0
            wkEndLatePMAAS = 0.0

            exp = arcpy.AddFieldDelimiters(rail_metrics_tbl, "Zone_Name") + " = " + str(rZoneName)
            rdRailTripM = arcpy.da.SearchCursor(rail_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualRailSpeed"], where_clause=exp)
            for irRow in rdRailTripM:
                irOID, irZoneName, irDayType, irDayPart, irKey, irAvgBusSpd = irRow[0], irRow[1], irRow[2], irRow[3], irRow[4], irRow[5]
                if irKey == None:
                    pass
                else:
                    irKeySfx = irKey[-2:]
                    if irKeySfx == '10':
                        wkDayAllDayAAS = irAvgBusSpd
                    elif irKeySfx == '11':
                        wkDayEarlyAMAAS = irAvgBusSpd
                    elif irKeySfx == '12':
                        wkDayPeakAMAAS = irAvgBusSpd
                    elif irKeySfx == '13':
                        wkDayMidDayAAS = irAvgBusSpd
                    elif irKeySfx == '14':
                        wkDayPeakPMAAS = irAvgBusSpd
                    elif irKeySfx == '15':
                        wkDayLatePMAAS = irAvgBusSpd
                    elif irKeySfx == '20':
                        wkEndAllDayAAS = irAvgBusSpd
                    elif irKeySfx == '21':
                        wkEndEarlyAMAAS = irAvgBusSpd
                    elif irKeySfx == '22':
                        wkEndPeakAMAAS = irAvgBusSpd
                    elif irKeySfx == '23':
                        wkEndMidDayAAS = irAvgBusSpd
                    elif irKeySfx == '24':
                        wkEndPeakPMAAS = irAvgBusSpd
                    elif irKeySfx == '25':
                        wkEndLatePMAAS = irAvgBusSpd
                    else:
                        pass

            del irRow
            del rdRailTripM

            ndxRailTrip.insertRow([rOID, rShape, rLinearID, rZoneName, rFromX, rFromY, rToX, rToY, rFromM, rToM, rShapeLength,
                                   wkDayAllDayAAS, wkDayEarlyAMAAS, wkDayPeakAMAAS, wkDayMidDayAAS, wkDayPeakPMAAS, wkDayLatePMAAS,
                                   wkEndAllDayAAS, wkEndEarlyAMAAS, wkEndPeakAMAAS, wkEndMidDayAAS, wkEndPeakPMAAS, wkEndLatePMAAS])

            t7 += 1

    del rlRow
    del rdRailCL

    log_message = "Updated {} centerline records of {} total for {}".format(t7, rCount, rail_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    log_message = "Adding/Calculating the MetricKey field in {}".format(rail_metrics_temp)
    logger.info(log_message)

    metric_list = [r.name for r in arcpy.ListFields(rail_metrics_temp)]
    metric_nms = ["MetricKey"]
    for metric_nm in metric_nms:
        if metric_nm not in metric_list:
            arcpy.AddField_management(rail_metrics_temp, "MetricKey", "TEXT", "", "", "50", "MetricKey", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field
    arcpy.CalculateField_management(rail_metrics_temp, "MetricKey", "!LINEARID! + \"-\" + !ZONE_NAME!", "PYTHON_9.3", "")

    return "%%%%%%% Process F7 - Average Annual Rail Trip Speeds - Linearization Complete %%%%%%%"


def linearizeRailTravellerIncome(proj_wkspc_gdb, logger):

    log_message = "%%%%%%% Process F8 - Linearize Rail Household Income onto its Metrics Centerline layer %%%%%%%"
    logger.info(log_message)

    rail_taz_centerline = os.path.join(proj_wkspc_gdb, "Rail_TAZ_Centerline")
    rail_metrics_temp = proj_wkspc_gdb + "\\ProjRailTravellerMetrics"
    rail_metrics_tbl = os.path.join(proj_wkspc_gdb, "CGCRailTraveller")

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = proj_wkspc_gdb
    arcpy.env.workspace = proj_wkspc_gdb

    log_message = "Verifying traveller metrics feature class template ..."
    logger.info(log_message)

    if arcpy.Exists(rail_metrics_temp):

        arcpy.DeleteFeatures_management(in_features=rail_metrics_temp)

    else:

        log_message = "Refreshing the Rail Traveller Metrics template: {}".format(rail_metrics_temp)
        logger.info(log_message)

        # Process: Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(rail_taz_centerline, proj_wkspc_gdb, "ProjRailTravellerMetrics", "LINEARID IS NULL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + rail_taz_centerline + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + rail_taz_centerline + ",TARGET_FID,-1,-1;LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + rail_taz_centerline + ",LINEARID,-1,-1; \
        ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + rail_taz_centerline + ",ZONE_NAME,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",TO_X,-1,-1;TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",TO_Y,-1,-1; \
        FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + rail_taz_centerline + ",TO_M,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + rail_taz_centerline + ",Shape_Length,-1,-1", "")

        arcpy.DeleteFeatures_management(in_features=rail_metrics_temp)

    log_message = "Appending measurement fields ..."
    logger.info(log_message)

    tv_list = [v.name for v in arcpy.ListFields(rail_metrics_temp)]
    trav_names = ["WkDay_AllDay_AAI", "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI",
                  "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI", "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI",
                  "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI", "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"]
    for trav_name in trav_names:
        if trav_name not in tv_list:
            arcpy.AddField_management(rail_metrics_temp, trav_name, "DOUBLE")

    log_message = "Verified {}".format(rail_metrics_temp)
    logger.info(log_message)

    edit = arcpy.da.Editor(proj_wkspc_gdb)

    log_message = "Beginning edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.startEditing()

    # Cursor Search and Insert
    log_message = "Starting edit operations ..."
    logger.info(log_message)
    edit.startOperation()

    ## Insert Cursor for ProjARailTravMetrics
    ## Search Cursor on Rail_TAZ_Centerline for geometry and key identifiers
    ## Search Cursor on CGCRailTraveller for metrics fields

    log_message = "Transposing centerline rail traveller metrics into {}".format(rail_metrics_temp)
    logger.info(log_message)

    t8 = 0
    riOID = 0
    riShape = ["SHAPE@"]
    riLinearID = None
    riZoneName = None
    riFromX, riFromY = 0.0, 0.0
    riToX, riToY = 0.0, 0.0
    riFromM, riToM = 0.0, 0.0
    riShapeLength = 0.0

    railClCount = arcpy.GetCount_management(rail_taz_centerline)
    riCount = int(railClCount[0])

    ndxRailTrav = arcpy.da.InsertCursor(rail_metrics_temp, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "Shape_Length",
                                                            "WkDay_AllDay_AAI", "WkDay_EarlyAM_AAI", "WkDay_PeakAM_AAI", "WkDay_MidDay_AAI", "WkDay_PeakPM_AAI", "WkDay_LatePM_AAI",
                                                            "WkEnd_AllDay_AAI", "WkEnd_EarlyAM_AAI", "WkEnd_PeakAM_AAI", "WkEnd_MidDay_AAI", "WkEnd_PeakPM_AAI", "WkEnd_LatePM_AAI"])

    rdRailCL = arcpy.da.SearchCursor(rail_taz_centerline, ["OBJECTID", "SHAPE@", "LINEARID", "ZONE_NAME", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M", "Shape_Length"], None, None, "False", (None, None))
    for riRow in rdRailCL:
        riOID, riShape, riLinearID, riZoneName, riFromX, riFromY, riToX, riToY, riFromM, riToM, riShapeLength = riRow[0], riRow[1], riRow[2], riRow[3], riRow[4], riRow[5], riRow[6], riRow[7], riRow[8], riRow[9], riRow[10]

        if riZoneName == None:
            pass
        else:
            log_message = "Updating Average Income by Time-Of-Day on Zone {}".format(str(riZoneName))
            logger.info(log_message)

            wkDayAllDayAAI = 0.0
            wkDayEarlyAMAAI = 0.0
            wkDayPeakAMAAI = 0.0
            wkDayMidDayAAI = 0.0
            wkDayPeakPMAAI = 0.0
            wkDayLatePMAAI = 0.0
            wkEndAllDayAAI = 0.0
            wkEndEarlyAMAAI = 0.0
            wkEndPeakAMAAI = 0.0
            wkEndMidDayAAI = 0.0
            wkEndPeakPMAAI = 0.0
            wkEndLatePMAAI = 0.0

            exp = arcpy.AddFieldDelimiters(rail_metrics_tbl, "Zone_Name") + " = " + str(riZoneName)
            rdRailTravM = arcpy.da.SearchCursor(rail_metrics_tbl, ["OBJECTID", "Zone_Name", "Day_Type", "Day_Part", "TripKey", "AvgAnnualIncome"], where_clause=exp)
            for tvRow in rdRailTravM:
                tvOID, tvZoneName, tvDayType, tvDayPart, tvKey, tvAvgTravInc = tvRow[0], tvRow[1], tvRow[2], tvRow[3], tvRow[4], tvRow[5]
                if tvKey == None:
                    pass
                else:
                    tvKeySfx = tvKey[-2:]
                    tvZoneStrName = str(tvZoneName)
                    if tvKeySfx == '10':
                        wkDayAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '11':
                        wkDayEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '12':
                        wkDayPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '13':
                        wkDayMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '14':
                        wkDayPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '15':
                        wkDayLatePMAAI = tvAvgTravInc
                    elif tvKeySfx == '20':
                        wkEndAllDayAAI = tvAvgTravInc
                    elif tvKeySfx == '21':
                        wkEndEarlyAMAAI = tvAvgTravInc
                    elif tvKeySfx == '22':
                        wkEndPeakAMAAI = tvAvgTravInc
                    elif tvKeySfx == '23':
                        wkEndMidDayAAI = tvAvgTravInc
                    elif tvKeySfx == '24':
                        wkEndPeakPMAAI = tvAvgTravInc
                    elif tvKeySfx == '25':
                        wkEndLatePMAAI = tvAvgTravInc
                    else:
                        pass

            del tvRow
            del rdRailTravM

            ndxRailTrav.insertRow([riOID, riShape, riLinearID, riZoneName, riFromX, riFromY, riToX, riToY, riFromM, riToM, riShapeLength,
                                  wkDayAllDayAAI, wkDayEarlyAMAAI, wkDayPeakAMAAI, wkDayMidDayAAI, wkDayPeakPMAAI, wkDayLatePMAAI, wkEndAllDayAAI,
                                  wkEndEarlyAMAAI, wkEndPeakAMAAI, wkEndMidDayAAI, wkEndPeakPMAAI, wkEndLatePMAAI])

            t8 += 1

    del riRow
    del rdRailCL

    log_message = "Updated {} centerline records of {} totsl for {}".format(t8, riCount, rail_metrics_temp)
    logger.info(log_message)

    log_message = "Stopping edit operations ..."
    logger.info(log_message)
    edit.stopOperation()

    log_message = "Ending edit session in {}".format(proj_wkspc_gdb)
    logger.info(log_message)
    edit.stopEditing(True)

    return "%%%%%%% Process F8 - Average Annual Rail Traveller Income - Linearization Complete %%%%%%%"



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

    result_f1 = linearizeAutoTripSpeed(workspace_gdb, logger)
    logger.info(result_f1)

    result_f2 = linearizeAutoTravellerIncome(workspace_gdb, logger)
    logger.info(result_f2)

    result_f3 = linearizePedestrianTripSpeed(workspace_gdb, logger)
    logger.info(result_f3)

    result_f4 = linearizePedestrianIncome(workspace_gdb, logger)
    logger.info(result_f4)

    result_f5 = linearizeBusTripSpeed(workspace_gdb, logger)
    logger.info(result_f5)

    result_f6 = linearizeBusTravellerIncome(workspace_gdb, logger)
    logger.info(result_f6)

    result_f7 = linearizeRailTripSpeed(workspace_gdb, logger)
    logger.info(result_f7)

    result_f8 = linearizeRailTravellerIncome(workspace_gdb, logger)
    logger.info(result_f8)