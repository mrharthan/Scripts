# ---------------------------------------------------------------------------
# proc_module_e.py  -- Transform prepared point and centerline data into network inputs
# Author: J. S. Pedigo
# ---------------------------------------------------------------------------
import os
import sys
import arcpy
import math
import string
import cgc_logging

#----------------------------------------------------------------------

def constructAutoNetwork(mstaging_gdb, wkspcdata_gdb, autonet_fd, logger):

    log_message = "%%%%%%% Process E1 - Construct the Link-Point Centerline for the Auto Network Dataset Build %%%%%%%"
    logger.info(log_message)

    # Local variables:
    taz_studyarea = os.path.join(mstaging_gdb, "WDC_TAZ_StudyArea")
    taz_studyarea_proj = wkspcdata_gdb + "\\WDC_TAZ_StudyArea"
    ucb_road_cl = os.path.join(mstaging_gdb, "UCB_Roads")
    ucb_road_proj = wkspcdata_gdb + "\\UCB_Roads"

    ucb_road_points = wkspcdata_gdb + "\\UCB_RoadPoints"
    ucb_taz_roadpoints = wkspcdata_gdb + "\\UCB_TAZ_RoadPoints"
    ucb_roadlines = wkspcdata_gdb + "\\UCB_RoadLines"
    ucb_taz_roadlines = wkspcdata_gdb + "\\UCB_TAZ_RoadLines"
    auto_taz_centerline = wkspcdata_gdb + "\\Auto_TAZ_Centerline"
    auto_taz_routesM = wkspcdata_gdb + "\\Auto_TAZ_RoutesM"
    auto_taz_network = autonet_fd + "\\Auto_TAZ_Network"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    ## Automobile Network Dataset Content
    automobile_nd = autonet_fd + "\\AutoNetwork_ND"
    automobile_junctions = autonet_fd + "\\AutoNetwork_ND_Junctions"

    if arcpy.Exists(taz_studyarea_proj):
        arcpy.Delete_management(taz_studyarea_proj, "FeatureClass")

    log_message = "Projecting the Study Area to the CGC Workspace: {}".format(taz_studyarea_proj)
    logger.info(log_message)

    # Process: Project
    arcpy.Project_management(taz_studyarea, taz_studyarea_proj, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',"
                                                                "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',"
                                                                "SPHEROID['WGS_1984',6378137.0,298.257223563]],"
                                                                "PRIMEM['Greenwich',0.0],UNIT['Degree',"
                                                                "0.0174532925199433]],PROJECTION["
                                                                "'Mercator_Auxiliary_Sphere'],PARAMETER["
                                                                "'False_Easting',0.0],PARAMETER['False_Northing',"
                                                                "0.0],PARAMETER['Central_Meridian',0.0],"
                                                                "PARAMETER['Standard_Parallel_1',0.0],"
                                                                "PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',"
                                                                "1.0]]", "", "GEOGCS['GCS_WGS_1984',"
                                                                "DATUM['D_WGS_1984',SPHEROID['WGS_1984',"
                                                                "6378137.0,298.257223563]],"
                                                                "PRIMEM['Greenwich',0.0],UNIT['Degree',"
                                                                "0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    if arcpy.Exists(ucb_road_proj):
        arcpy.Delete_management(ucb_road_proj, "FeatureClass")

    log_message = "Projecting the US Census TIGER/Line Roads to the CGC Workspace: {}".format(ucb_road_proj)
    logger.info(log_message)

    # Process: Project (2)
    arcpy.Project_management(ucb_road_cl, ucb_road_proj, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS["
                                                         "'GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',"
                                                         "6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],"
                                                         "UNIT['Degree',0.0174532925199433]],PROJECTION["
                                                         "'Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',"
                                                         "0.0],PARAMETER['False_Northing',0.0],PARAMETER["
                                                         "'Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',"
                                                         "0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',"
                                                         "1.0]]", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',"
                                                         "SPHEROID['WGS_1984',6378137.0,298.257223563]],"
                                                         "PRIMEM['Greenwich',0.0],UNIT['Degree',"
                                                         "0.0174532925199433]]", "NO_PRESERVE_SHAPE",
                                                         "", "NO_VERTICAL")

    if arcpy.Exists(auto_taz_routesM):
        arcpy.Delete_management(auto_taz_routesM, "FeatureClass")

    log_message = "Creating Auto TAZ Newtork routes from the attributed Road Links for {}".format(auto_taz_routesM)
    logger.info(log_message)

    # Process: Create Routes
    arcpy.CreateRoutes_lr(ucb_road_proj, "LINEARID", auto_taz_routesM, "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    log_message = "Extending Line (5 meters) in : " + auto_taz_routesM
    logger.info(log_message)

    # Process: Extend Line - Reset intersections of segments up to 5.0 meters
    arcpy.ExtendLine_edit(auto_taz_routesM, "5 Meters", "EXTENSION")

    if arcpy.Exists(ucb_roadlines):
        arcpy.Delete_management(ucb_roadlines, "FeatureClass")

    log_message = "Splitting features into line segments by intersection to: " + ucb_roadlines
    logger.info(log_message)

    # Process: Feature To Line - Cycle 1 - Initial Segmentation
    arcpy.FeatureToLine_management(auto_taz_routesM, ucb_roadlines, "", "ATTRIBUTES")

    if arcpy.Exists(ucb_taz_roadlines):
        arcpy.Delete_management(ucb_taz_roadlines, "FeatureClass")

    log_message = "Clipping Road Links to the Study Area for {}".format(ucb_taz_roadlines)
    logger.info(log_message)

    # Process: Clip
    arcpy.Clip_analysis(ucb_roadlines, taz_studyarea_proj, ucb_taz_roadlines, "0.001 Miles")

    if arcpy.Exists(auto_taz_centerline):
        arcpy.Delete_management(auto_taz_centerline, "FeatureClass")

    log_message = "Running Spatial Join between Road Links and TAZ Polygons for the Zone Name identifier ..."
    logger.info(log_message)

    # Process: Spatial Join
    arcpy.SpatialJoin_analysis(ucb_taz_roadlines, taz_studyarea_proj, auto_taz_centerline, "JOIN_ONE_TO_ONE", "KEEP_ALL", "LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + ucb_taz_roadlines + ",LINEARID,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 18 Text 0 0 ,First,#," + taz_studyarea_proj + ",name,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#," + taz_studyarea_proj + ",Shape_Area,-1,-1", "HAVE_THEIR_CENTER_IN", "", "")

    log_message = "Repairing Geometry in: " + auto_taz_centerline
    logger.info(log_message)

    arcpy.RepairGeometry_management(in_features=auto_taz_centerline, delete_null="DELETE_NULL")

    log_message = "Extracting First & Last X, Y, M from Intersection Segments in: " + auto_taz_centerline + " ..."
    logger.info(log_message)

    fc_list = [f.name for f in arcpy.ListFields(auto_taz_centerline)]
    field_names = ["FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"]
    for field_name in field_names:
        if field_name not in fc_list:
            arcpy.AddField_management(auto_taz_centerline, field_name, "DOUBLE")

    field_names = ["SHAPE@"] + field_names

    with arcpy.da.UpdateCursor(auto_taz_centerline, field_names) as cursor:
        for row in cursor:
            line_geom = row[0]

            start = arcpy.PointGeometry(line_geom.firstPoint)
            start_xy = start.WKT.strip("POINT (").strip(")").split(" ")
            row[1] = start_xy[0]  # FROM_X
            row[2] = start_xy[1]  # FROM_Y

            end = arcpy.PointGeometry(line_geom.lastPoint)
            end_xy = end.WKT.strip("POINT (").strip(")").split(" ")
            row[3] = end_xy[0]  # TO_X
            row[4] = end_xy[1]  # TO_Y

            row[5] = round(line_geom.firstPoint.M, 3)
            to_dfo = round(line_geom.lastPoint.M, 3)
            if to_dfo != 0:
                row[6] = to_dfo
                cursor.updateRow(row)

    del row
    del cursor

    log_message = "Converting Meters to Miles in From_M and To_M fields ..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(auto_taz_centerline, "FROM_M", "convertAutoFrmM( !FROM_M! )", "PYTHON_9.3",
                                    "def convertAutoFrmM(fromM):\\n  inFDFO = 0  \\n  outFDFO = 0\\n  if fromM == None or fromM == 0:\\n    pass\\n  else:       \\n    inFDFO = fromM/1609.344\\n    outFDFO = str((inFDFO * 1000)/1000)\\n  return round(float(outFDFO), 3)\\n  ")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(auto_taz_centerline, "TO_M", "convertAutoToM( !TO_M! )", "PYTHON_9.3",
                                    "def convertAutoToM(toM):\\n  inTDFO = 0  \\n  outTDFO = 0\\n  if toM == None or toM == 0:\\n    pass\\n  else:       \\n    inTDFO = toM/1609.344\\n    outTDFO = str((inTDFO * 1000)/1000)\\n  return round(float(outTDFO), 3)")

    log_message = "Clearing intermediate tables..."
    logger.info(log_message)

    if arcpy.Exists(ucb_road_proj):
        arcpy.Delete_management(ucb_road_proj, "FeatureClass")

    ### if arcpy.Exists(ucb_road_points):
    ###     arcpy.Delete_management(ucb_road_points, "FeatureClass")

    if arcpy.Exists(ucb_roadlines):
        arcpy.Delete_management(ucb_roadlines, "FeatureClass")

    if arcpy.Exists(ucb_taz_roadlines):
        arcpy.Delete_management(ucb_taz_roadlines, "FeatureClass")

    if arcpy.Exists(auto_taz_routesM):
        arcpy.Delete_management(auto_taz_routesM, "FeatureClass")

    if arcpy.Exists(auto_taz_network):
        arcpy.Delete_management(auto_taz_network, "FeatureClass")

    log_message = "Unprojecting Auto TAZ Features to GCS NAD83: {}".format(auto_taz_network)
    logger.info(log_message)

    # Process: Project (7)
    arcpy.Project_management(auto_taz_centerline, auto_taz_network,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Auto_TAZ_Network Input is ready for the ND Build manual process !!!"
    logger.info(log_message)

    return "%%%%%%% Process E1 Complete %%%%%%%"


def segmentPedestrianPaths(mstaging_gdb, wkspcdata_gdb, cgctemp_gdb, logger):

    log_message = "%%%%%%% Process E2 - Segment and Synthesize Pedestrian Paths for the Multimodal Transit Network Dataset Build %%%%%%%"
    logger.info(log_message)

    taz_studyarea_proj = os.path.join(wkspcdata_gdb, "WDC_TAZ_StudyArea")
    auto_taz_centerline = os.path.join(wkspcdata_gdb, "Auto_TAZ_Centerline")
    mwcog_pedestrian_paths = os.path.join(mstaging_gdb, "MWCOG_PedestrianPaths")
    multimodal_trans_temp = os.path.join(cgctemp_gdb, "MultiModalTransitTemp")
    ped_paths_proj = wkspcdata_gdb + "\\SRC_PedestrianPaths"
    ped_taz_routesM = wkspcdata_gdb + "\\SRC_Ped_TAZ_RoutesM"
    ped_path_points = wkspcdata_gdb + "\\SRC_PedPathPoints"
    ped_taz_points = wkspcdata_gdb + "\\SRC_PedTAZPoints"
    ped_path_lines = wkspcdata_gdb + "\\SRC_PedPathLines"
    ped_taz_lines = wkspcdata_gdb + "\\SRC_PedTAZLines"
    ped_taz_path = wkspcdata_gdb + "\\Ped_TAZ_Path"
    ped_auto_taz_path = wkspcdata_gdb + "\\Ped_Auto_TAZ_Path"
    ped_taz_centerline = wkspcdata_gdb + "\\Ped_TAZ_Centerline"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    if arcpy.Exists(ped_paths_proj):
        arcpy.Delete_management(ped_paths_proj, "FeatureClass")

    log_message = "Projecting the area Pedestrian Paths to the CGC Workspace: {}".format(ped_paths_proj)
    logger.info(log_message)

    # Process: Project (2)
    arcpy.Project_management(mwcog_pedestrian_paths, ped_paths_proj, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    if arcpy.Exists(ped_path_points):
        arcpy.Delete_management(ped_path_points, "FeatureClass")

    log_message = "Running Intersect Tool on Pedestrian Paths for Intersection Points: {}".format(ped_path_points)
    logger.info(log_message)

    # Process: Intersect
    arcpy.Intersect_analysis(ped_paths_proj + " #", ped_path_points, "ALL", "0.003 Miles", "POINT")

    if arcpy.Exists(ped_taz_points):
        arcpy.Delete_management(ped_taz_points, "FeatureClass")

    log_message = "Clipping Pedestrian Intersection Points to the Study Area for {}".format(ped_taz_points)
    logger.info(log_message)

    # Process: Clip (2)
    arcpy.Clip_analysis(ped_path_points, taz_studyarea_proj, ped_taz_points, "0.001 Miles")

    log_message = "Reducing fields in Pedestrian Path intersection points for network usage: {}".format(ped_taz_points)
    logger.info(log_message)

    # Process: Delete Field
    arcpy.DeleteField_management(ped_taz_points, "To;From_;Status;Jurisdicti;State;Descriptio;Bikeway;BikeFacili;Trail_Widt;Surface;Length_Mi")

    log_message = "Creating Auto TAZ Newtork routes from the attributed Road Links for {}".format(ped_taz_routesM)
    logger.info(log_message)

    # Process: Create Routes
    arcpy.CreateRoutes_lr(ped_paths_proj, "TrailName", ped_taz_routesM, "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    log_message = "Extending Line (5 meters) in : " + ped_taz_routesM
    logger.info(log_message)

    # Process: Extend Line - Reset intersections of segments up to 5.0 meters
    arcpy.ExtendLine_edit(ped_taz_routesM, "5 Meters", "EXTENSION")

    if arcpy.Exists(ped_path_lines):
        arcpy.Delete_management(ped_path_lines, "FeatureClass")

    log_message = "Splitting features into line segments by intersection to: " + ped_path_lines
    logger.info(log_message)

    # Process: Feature To Line - Cycle 1 - Initial Segmentation
    arcpy.FeatureToLine_management(ped_taz_routesM, ped_path_lines, "", "ATTRIBUTES")

    if arcpy.Exists(ped_taz_lines):
        arcpy.Delete_management(ped_taz_lines, "FeatureClass")

    log_message = "Clipping Pedestrian Links to the Study Area for {}".format(ped_taz_lines)
    logger.info(log_message)

    # Process: Clip
    arcpy.Clip_analysis(ped_path_lines, taz_studyarea_proj, ped_taz_lines, "0.001 Miles")

    if arcpy.Exists(ped_taz_path):
        arcpy.Delete_management(ped_taz_path, "FeatureClass")

    log_message = "Running Spatial Join between Pedestrian Paths and TAZ Polygons for the Zone Name identifier ..."
    logger.info(log_message)

    # Process: Spatial Join
    arcpy.SpatialJoin_analysis(ped_taz_lines, taz_studyarea_proj, ped_taz_path, "JOIN_ONE_TO_ONE", "KEEP_ALL", "Street_Nam \"Street Name\" true true false 100 Text 0 0 ,First,#," + ped_taz_lines + ",Street_Nam,-1,-1;TrailName \"Trail Name\" true true false 254 Text 0 0 ,First,#," + ped_taz_lines + ",TrailName,-1,-1;Length_Mi \"Length in Miles\" true true false 8 Double 0 0 ,First,#," + ped_taz_lines + ",Length_Mi,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + ped_taz_lines + ",Shape_Length,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + taz_studyarea_proj + ",name,-1,-1", "HAVE_THEIR_CENTER_IN", "", "")

    log_message = "Repairing Geometry in: " + ped_taz_path
    logger.info(log_message)

    arcpy.RepairGeometry_management(in_features=ped_taz_path, delete_null="DELETE_NULL")

    log_message = "Extracting First & Last X, Y, M from Intersection Segments in: " + ped_taz_path + " ..."
    logger.info(log_message)

    fc_list = [f.name for f in arcpy.ListFields(ped_taz_path)]
    field_names = ["FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"]
    for field_name in field_names:
        if field_name not in fc_list:
            arcpy.AddField_management(ped_taz_path, field_name, "DOUBLE")

    field_names = ["SHAPE@"] + field_names

    with arcpy.da.UpdateCursor(ped_taz_path, field_names) as cursor:
        for row in cursor:
            line_geom = row[0]

            start = arcpy.PointGeometry(line_geom.firstPoint)
            start_xy = start.WKT.strip("POINT (").strip(")").split(" ")
            row[1] = start_xy[0]  # FROM_X
            row[2] = start_xy[1]  # FROM_Y

            end = arcpy.PointGeometry(line_geom.lastPoint)
            end_xy = end.WKT.strip("POINT (").strip(")").split(" ")
            row[3] = end_xy[0]  # TO_X
            row[4] = end_xy[1]  # TO_Y

            from_dfo = line_geom.firstPoint.M  ## row[5]
            to_dfo = line_geom.lastPoint.M
            if to_dfo > from_dfo:
                row[5] = from_dfo
                row[6] = to_dfo
            elif to_dfo != 0:
                row[5] = to_dfo
                row[6] = from_dfo
            cursor.updateRow(row)

    del row
    del cursor

    if arcpy.Exists(ped_auto_taz_path):
        arcpy.Delete_management(ped_auto_taz_path, "FeatureClass")

    log_message = "Merging {} with the Auto TAZ Centerline ...".format(ped_taz_path)
    logger.info(log_message)

    # Process: Merge
    arcpy.Merge_management(ped_taz_path + ";" + auto_taz_centerline, ped_auto_taz_path, "Street_Nam \"Street Name\" true true false 100 Text 0 0 ,First,#," + ped_taz_path + ",Street_Nam,-1,-1;TrailName \"Trail Name\" true true false 254 Text 0 0 ,First,#," + ped_taz_path + ",TrailName,-1,-1;Length_Mi \"Length in Miles\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",Length_Mi,-1,-1;LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + auto_taz_centerline + ",LINEARID,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + ped_taz_path + ",ZONE_NAME,-1,-1," + auto_taz_centerline + ",ZONE_NAME,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + ped_taz_path + ",Shape_Length,-1,-1," + auto_taz_centerline + ",Shape_Length,-1,-1;FROM_X \"FROM_X\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",FROM_X,-1,-1," + auto_taz_centerline + ",FROM_X,-1,-1;FROM_Y \"FROM_Y\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",FROM_Y,-1,-1," + auto_taz_centerline + ",FROM_Y,-1,-1;TO_X \"TO_X\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",TO_X,-1,-1," + auto_taz_centerline + ",TO_X,-1,-1;TO_Y \"TO_Y\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",TO_Y,-1,-1," + auto_taz_centerline + ",TO_Y,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",FROM_M,-1,-1," + auto_taz_centerline + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + ped_taz_path + ",TO_M,-1,-1," + auto_taz_centerline + ",TO_M,-1,-1")

    log_message = "Regional Pedestrian Path geo-data is problematic -- repairing by brute force in {}".format(ped_auto_taz_path)
    logger.info(log_message)

    log_message = "Add/Calculate RouteID"
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(ped_auto_taz_path, "RouteID", "TEXT", "", "", "22", "RouteID", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field
    arcpy.CalculateField_management(ped_auto_taz_path, "RouteID", "forceRouteID( !OBJECTID! , !TrailName! , !LINEARID! )", "PYTHON_9.3", "def forceRouteID(oid, tName, lineID):\\n  pedID = 3000000000 + int(oid)\\n  outID = None\\n  if tName == None:\\n    outID = str(lineID)\\n  else:    \\n    outID = pedID\\n  return outID")

    log_message = "Add/Calculate RouteName"
    logger.info(log_message)

    # Process: Add Field (2)
    arcpy.AddField_management(ped_auto_taz_path, "RouteName", "TEXT", "", "", "100", "RouteName", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(ped_auto_taz_path, "RouteName", "forceRouteName( !TrailName! )", "PYTHON_9.3", "def forceRouteName(tName):\\n  outName = None\\n  if tName == None:\\n    outName = \"NA\"\\n  else:\\n    outName = str(tName)\\n  return outName")

    log_message = "Add/Calculate RouteModeCD"
    logger.info(log_message)

    # Process: Add Field (3)
    arcpy.AddField_management(ped_auto_taz_path, "RouteModeCD", "TEXT", "", "", "3", "RouteModeCD", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (3)
    arcpy.CalculateField_management(ped_auto_taz_path, "RouteModeCD", "\"3\"", "PYTHON_9.3", "")

    log_message = "Repairing negative M values"
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(ped_auto_taz_path, "FROM_M", "fixFrmM( !FROM_M! )", "PYTHON_9.3", "def fixFrmM(fdfo):\\n  retDbl = 9999.0\\n  if fdfo < 0.0:\\n    retDbl = 0.0\\n  else:\\n    retDbl = fdfo\\n  return retDbl\\n")

    # Process: Calculate Field
    arcpy.CalculateField_management(ped_auto_taz_path, "TO_M", "fixToM( !TO_M! )", "PYTHON_9.3", "def fixToM(tdfo):\\n  retDbl = 9999.0\\n  if tdfo < 0.0:\\n    retDbl = 0.0\\n  else:\\n    retDbl = tdfo\\n  return retDbl\\n")

    log_message = "Converting Meters to Miles in From_M and To_M fields ..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(ped_auto_taz_path, "FROM_M", "convertAutoFrmM( !FROM_M! )", "PYTHON_9.3",
                                    "def convertAutoFrmM(fromM):\\n  inFDFO = 0  \\n  outFDFO = 0\\n  if fromM == None or fromM == 0:\\n    pass\\n  else:       \\n    inFDFO = fromM/1609.344\\n    outFDFO = str((inFDFO * 1000)/1000)\\n  return round(float(outFDFO), 3)\\n  ")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(ped_auto_taz_path, "TO_M", "convertAutoToM( !TO_M! )", "PYTHON_9.3",
                                    "def convertAutoToM(toM):\\n  inTDFO = 0  \\n  outTDFO = 0\\n  if toM == None or toM == 0:\\n    pass\\n  else:       \\n    inTDFO = toM/1609.344\\n    outTDFO = str((inTDFO * 1000)/1000)\\n  return round(float(outTDFO), 3)")

    log_message = "Clearing intermediate tables..."
    logger.info(log_message)

    if arcpy.Exists(ped_path_points):
        arcpy.Delete_management(ped_path_points, "FeatureClass")

    if arcpy.Exists(ped_path_lines):
        arcpy.Delete_management(ped_path_lines, "FeatureClass")

    if arcpy.Exists(ped_taz_lines):
        arcpy.Delete_management(ped_taz_lines, "FeatureClass")

    if arcpy.Exists(ped_taz_path):
        arcpy.Delete_management(ped_taz_path, "FeatureClass")

    log_message = "Writing QC reults to: {}".format(ped_taz_centerline)
    logger.info(log_message)

    if arcpy.Exists(ped_taz_centerline):
        arcpy.Delete_management(ped_taz_centerline, "FeatureClass")

    # Process: Feature Class to Feature Class (3) -- Alt. Routing Filter --- TO_M > 0
    arcpy.FeatureClassToFeatureClass_conversion(ped_auto_taz_path, wkspcdata_gdb, "Ped_TAZ_Centerline", "", "RouteID \"RouteID\" true true false 22 Text 0 0 ,First,#," + ped_auto_taz_path + ",RouteID,-1,-1;RouteName \"RouteName\" true true false 100 Text 0 0 ,First,#," + ped_auto_taz_path + ",RouteName,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + ped_auto_taz_path + ",RouteModeCD,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + ped_auto_taz_path + ",ZONE_NAME,-1,-1;FROM_M \"FROM_M\" true true false 8 Double 0 0 ,First,#," + ped_auto_taz_path + ",FROM_M,-1,-1;TO_M \"TO_M\" true true false 8 Double 0 0 ,First,#," + ped_auto_taz_path + ",TO_M,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + ped_auto_taz_path + ",Shape_Length,-1,-1", "")

    if arcpy.Exists(ped_auto_taz_path):
        arcpy.Delete_management(ped_auto_taz_path, "FeatureClass")

    return "%%%%%%% Process E2 Complete %%%%%%%"


def segmentBusRoutes(srcdata_gdb, mstaging_gdb, wkspcdata_gdb, cgctemp_gdb, logger):

    log_message = "%%%%%%% Process E3 - Segment Bus Routes and Bus Transfer Data for the Multimodal Transit Network Dataset %%%%%%%"
    logger.info(log_message)

    taz_studyarea_proj = os.path.join(wkspcdata_gdb, "WDC_TAZ_StudyArea")
    proxy_route_temp = wkspcdata_gdb + "\\ProxyRouteTemp"
    bus_route_temp = wkspcdata_gdb + "\\BusRouteTemp"
    bus_route = wkspcdata_gdb + "\\BusRoute"
    bus_route_m = wkspcdata_gdb + "\\BusRouteM"
    bus_route_m_links = wkspcdata_gdb + "\\BusRouteMLinks"
    bus_route_link_data = wkspcdata_gdb + "\\BusRouteMLinkData"
    bus_route_stop_temp = wkspcdata_gdb + "\\BusRouteStopsTemp"
    bus_route_select_temp = wkspcdata_gdb + "\\BusRouteSelectTemp"
    mwcog_bus_stops = os.path.join(mstaging_gdb, "MWCOG_Bus_Stops")
    mwcog_bus_lines = os.path.join(mstaging_gdb, "MWCOG_Bus_Lines")
    src_ncrtpb_bus_stops = wkspcdata_gdb + "\\SRC_NCRTPB_BusStops"
    src_ncrtpb_bus_lines = wkspcdata_gdb + "\\SRC_NCRTPB_BusLines"
    src_ncrtpb_bus_lines_m = wkspcdata_gdb + "\\SRC_NCRTPB_BusLinesM"
    gtfs_busTemp = cgctemp_gdb + "\\GTFS_BusTemplate"
    gtfs_busProj = wkspcdata_gdb + "\\GTFS_BusPntsProjected"
    src_gtfs_bus_stops = wkspcdata_gdb + "\\SRC_GTFS_BusStops"
    src_all_bus_stops = wkspcdata_gdb + "\\SRC_All_BusStops"
    bus_taz_stops = wkspcdata_gdb + "\\Bus_TAZ_StopPoints"
    bus_taz_rte_listLyr = wkspcdata_gdb + "\\Bus_TAZ_StopPoints_Dissolve"
    bus_taz_rteList = wkspcdata_gdb + "\\Bus_TAZ_RouteList"
    bus_data_centerline = wkspcdata_gdb + "\\Bus_Data_Centerline"
    bus_data_centerline_clip = wkspcdata_gdb + "\\Bus_Data_Centerline_Clip"
    src_bus_centerline = wkspcdata_gdb + "\\SRC_Bus_Centerline"
    src_bus_centerline_clip = wkspcdata_gdb + "\\SRC_Bus_Centerline_Clip"
    merge_bus_centerline = wkspcdata_gdb + "\\Merge_Bus_Centerline"
    bus_taz_centerline = wkspcdata_gdb + "\\Bus_TAZ_Centerline"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace
    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% DATA PREP - SATRT %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if arcpy.Exists(src_ncrtpb_bus_stops):
        arcpy.Delete_management(src_ncrtpb_bus_stops, "FeatureClass")

    log_message = "Projecting the area NCRTPB Bus Stops to the CGC Workspace: {}".format(src_ncrtpb_bus_stops)
    logger.info(log_message)

    # Process: Project
    arcpy.Project_management(mwcog_bus_stops, src_ncrtpb_bus_stops, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "WGS_1984_(ITRF08)_To_NAD_1983_2011", "PROJCS['NAD_1983_2011_StatePlane_Virginia_North_FIPS_4501_Ft_US',GEOGCS['GCS_NAD_1983_2011',DATUM['D_NAD_1983_2011',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',11482916.66666666],PARAMETER['False_Northing',6561666.666666666],PARAMETER['Central_Meridian',-78.5],PARAMETER['Standard_Parallel_1',38.03333333333333],PARAMETER['Standard_Parallel_2',39.2],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Foot_US',0.3048006096012192]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    if arcpy.Exists(src_ncrtpb_bus_lines):
        arcpy.Delete_management(src_ncrtpb_bus_lines, "FeatureClass")

    log_message = "Projecting the area NCRTPB Bus Route Lines to the CGC Workspace: {}".format(src_ncrtpb_bus_lines)
    logger.info(log_message)

    # Process: Project (3)
    arcpy.Project_management(mwcog_bus_lines, src_ncrtpb_bus_lines, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['NAD_1983_StatePlane_Maryland_FIPS_1900_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1312333.333333333],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.0],PARAMETER['Standard_Parallel_1',38.3],PARAMETER['Standard_Parallel_2',39.45],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Foot_US',0.3048006096012192]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Preparing the GTFS bus stop extraction and XY plot ..."
    logger.info(log_message)

    if arcpy.Exists(src_gtfs_bus_stops):
        arcpy.DeleteFeatures_management(src_gtfs_bus_stops)
    else:
        # Process: Project (Project)
        arcpy.Project_management(in_dataset=gtfs_busTemp, out_dataset=src_gtfs_bus_stops, out_coor_system="PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", transform_method=[], in_coor_system="GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

        arcpy.DeleteFeatures_management(src_gtfs_bus_stops)

    busStopNmList = ["GTFSAlexandriaBusStopsWD", "GTFSArlingtonBusStopsWD", "GTFSArlingtonBusStopsWE",
                     "GTFSFairfaxConnectorBusStopsWD", "GTFSMetroMarylandBusStopsWD", "GTFSMontgomeryBusStopsWD",
                     "GTFSPrinceGeorgeBusStopsWD", "GTFSWMATACirculatorBusStopsWD"]
    ## Add later:  "GTFSFairfaxCueBusStopsWD", "GTFSRegionalMarylandBusStopsWD", "GTFSRegionalMarylandBusStopsWE", "GTFSWoodbridgeBusStopsWD"
    busStopTbl = cgctemp_gdb + "\\GTFS_Bus_Stops"
    busStopLyr = "in_memory\\GTFS_Bus_Stops_Layer"

    for bStopNm in busStopNmList:
        bStopTbl = os.path.join(srcdata_gdb, bStopNm)

        log_message = "Geolocating: {}".format(bStopNm)
        logger.info(log_message)

        if arcpy.Exists(busStopTbl):
            arcpy.Delete_management(busStopTbl, "Table")

        # Process: Table To Table (Table To Table)
        arcpy.TableToTable_conversion(in_rows=bStopTbl, out_path=cgctemp_gdb, out_name="GTFS_Bus_Stops", where_clause="", field_mapping="stop_id \"stop_id\" true true false 4 Long 0 10,First,#," + bStopTbl + ",stop_id,-1,-1;stop_code \"stop_code\" true true false 4 Long 0 10,First,#," + bStopTbl + ",stop_code,-1,-1;stop_name \"stop_name\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",stop_name,0,2147483647;stop_desc \"stop_desc\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",stop_desc,0,2147483647;stop_lat \"stop_lat\" true true false 8 Double 8 12,First,#," + bStopTbl + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 8 12,First,#," + bStopTbl + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",zone_id,0,2147483647;stop_url \"stop_url\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",stop_url,0,2147483647;location_type \"location_type\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",location_type,0,2147483647;parent_station \"parent_station\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",parent_station,0,2147483647;stop_timezone \"stop_timezone\" true true false 2147483647 Text 0 0,First,#," + bStopTbl + ",stop_timezone,0,2147483647;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 10,First,#," + bStopTbl + ",wheelchair_boarding,-1,-1", config_keyword="")

        if arcpy.Exists(busStopLyr):
            arcpy.Delete_management(busStopLyr, "FeatureLayer")

        # Process: Make XY Event Layer (Make XY Event Layer)
        arcpy.MakeXYEventLayer_management(table=busStopTbl, in_x_field="stop_lon", in_y_field="stop_lat", out_layer=busStopLyr, spatial_reference="GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision", in_z_field="")

        if arcpy.Exists(gtfs_busTemp):
            arcpy.Delete_management(gtfs_busTemp, "FeatureClass")

        # Process: Copy Features (Copy Features)
        arcpy.CopyFeatures_management(in_features=busStopLyr, out_feature_class=gtfs_busTemp, config_keyword="", spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None)

        if arcpy.Exists(gtfs_busProj):
            arcpy.Delete_management(gtfs_busProj, "FeatureClass")

        # Process: Project (Project)
        arcpy.Project_management(in_dataset=gtfs_busTemp, out_dataset=gtfs_busProj, out_coor_system="PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", transform_method=[], in_coor_system="GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

        # Process: Append (Append)
        arcpy.Append_management(inputs=[gtfs_busProj], target=src_gtfs_bus_stops, schema_type="NO_TEST", field_mapping="stop_id \"stop_id\" true true false 4 Long 0 0,First,#," + gtfs_busProj + ",stop_id,-1,-1;stop_code \"stop_code\" true true false 4 Long 0 0,First,#," + gtfs_busProj + ",stop_code,-1,-1;stop_name \"stop_name\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",stop_name,0,2147483647;stop_desc \"stop_desc\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",stop_desc,0,2147483647;stop_lat \"stop_lat\" true true false 8 Double 0 0,First,#," + gtfs_busProj + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0,First,#," + gtfs_busProj + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",zone_id,0,2147483647;stop_url \"stop_url\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",stop_url,0,2147483647;location_type \"location_type\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",location_type,0,2147483647;parent_station \"parent_station\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",parent_station,0,2147483647;stop_timezone \"stop_timezone\" true true false 2147483647 Text 0 0,First,#," + gtfs_busProj + ",stop_timezone,0,2147483647;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0,First,#," + gtfs_busProj + ",wheelchair_boarding,-1,-1", subtype="")

    log_message = "Finalized GTFS bus stop extraction and XY plot - Preparing for Bus Stop location calibration"
    logger.info(log_message)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Spatially joining GTFS bus stop point data to {}".format(src_ncrtpb_bus_stops)
    logger.info(log_message)

    if arcpy.Exists(src_all_bus_stops):
        arcpy.Delete_management(src_all_bus_stops, "FeatureClass")

    # Process: Spatial Join (Spatial Join)
    arcpy.SpatialJoin_analysis(target_features=src_ncrtpb_bus_stops, join_features=src_gtfs_bus_stops,
                               out_feature_class=src_all_bus_stops, join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL", field_mapping="stop_id \"stop_id\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",stop_id,0,8000," + src_gtfs_bus_stops + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Friday_AmPeak_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Friday_AmPeak_hwy,-1,-1;Avg_EarlyAM_WaitTime_WD \"Friday_Midday_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Friday_Midday_hwy,-1,-1;Avg_PeakAM_WaitTime_WD \"Friday_PmPeak_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Friday_PmPeak_hwy,-1,-1;Avg_MidDay_WaitTime_WD \"Friday_Evening_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Friday_Evening_hwy,-1,-1;Avg_PeakPM_WaitTime_WD \"Mon_AmPeak_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Mon_AmPeak_hwy,-1,-1;Avg_LatePM_WaitTime_WD \"Mon_Midday_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Mon_Midday_hwy,-1,-1;Avg_AllDay_WaitTime_WE \"Mon_PmPeak_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Mon_PmPeak_hwy,-1,-1;Avg_EarlyAM_WaitTime_WE \"Mon_Evening_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Mon_Evening_hwy,-1,-1;Avg_PeakAM_WaitTime_WE \"Saturday_AmPeak_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Saturday_AmPeak_hwy,-1,-1;Avg_MidDay_WaitTime_WE \"Saturday_Midday_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Saturday_Midday_hwy,-1,-1;Avg_PeakPM_WaitTime_WE \"Saturday_PmPeak_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Saturday_PmPeak_hwy,-1,-1;Avg_LatePM_WaitTime_WE \"Saturday_Evening_hwy\" true true false 8 Double 0 0,First,#," + src_ncrtpb_bus_stops + ",Saturday_Evening_hwy,-1,-1;agency \"agency\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",agency,0,8000;route_id_all \"route_id_all\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",route_id_all,0,8000;route_short_name_all \"route_short_name_all\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",route_short_name_all,0,8000;route_long_name_all \"route_long_name_all\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",route_long_name_all,0,8000;trip_headsign_all \"trip_headsign_all\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",trip_headsign_all,0,8000;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",direction_id_all,0,8000;stop_name \"stop_name\" true true false 2147483647 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",stop_name,0,2147483647," + src_gtfs_bus_stops + ",stop_name,0,2147483647;location_type \"location_type\" true true false 2147483647 Text 0 0,First,#," + src_ncrtpb_bus_stops + ",location_type,0,2147483647," + src_gtfs_bus_stops + ",location_type,0,2147483647;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0,First,#," + src_ncrtpb_bus_stops + ",wheelchair_boarding,-1,-1," + src_gtfs_bus_stops + ",wheelchair_boarding,-1,-1;stop_code \"stop_code\" true true false 4 Long 0 0,First,#," + src_gtfs_bus_stops + ",stop_code,-1,-1;stop_desc \"stop_desc\" true true false 2147483647 Text 0 0,First,#," + src_gtfs_bus_stops + ",stop_desc,0,2147483647;stop_lat \"stop_lat\" true true false 8 Double 0 0,First,#," + src_gtfs_bus_stops + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0,First,#," + src_gtfs_bus_stops + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 2147483647 Text 0 0,First,#," + src_gtfs_bus_stops + ",zone_id,0,2147483647;stop_url \"stop_url\" true true false 2147483647 Text 0 0,First,#," + src_gtfs_bus_stops + ",stop_url,0,2147483647;parent_station \"parent_station\" true true false 2147483647 Text 0 0,First,#," + src_gtfs_bus_stops + ",parent_station,0,2147483647;stop_timezone \"stop_timezone\" true true false 2147483647 Text 0 0,First,#," + src_gtfs_bus_stops + ",stop_timezone,0,2147483647;stop_id_txt \"stop_id_txt\" true true false 255 Text 0 0,First,#," + src_gtfs_bus_stops + ",stop_id_txt,0,255",
                               match_option="INTERSECT", search_radius="0.003 Miles", distance_field_name="")

    log_message = "Setting up Bus Transfer Wait Time fields by Day type and Day Part in {}".format(src_all_bus_stops)
    logger.info(log_message)

    # Process: Alter Field (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_AllDay_WaitTime_WD",
                                                      new_field_name="Avg_AllDay_WaitTime_WD",
                                                      new_field_alias="Avg_AllDay_WaitTime_WD", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (2) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_EarlyAM_WaitTime_WD",
                                                      new_field_name="Avg_EarlyAM_WaitTime_WD",
                                                      new_field_alias="Avg_EarlyAM_WaitTime_WD", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (3) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_PeakAM_WaitTime_WD",
                                                      new_field_name="Avg_PeakAM_WaitTime_WD",
                                                      new_field_alias="Avg_PeakAM_WaitTime_WD", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (4) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_MidDay_WaitTime_WD",
                                                      new_field_name="Avg_MidDay_WaitTime_WD",
                                                      new_field_alias="Avg_MidDay_WaitTime_WD", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (5) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_PeakPM_WaitTime_WD",
                                                      new_field_name="Avg_PeakPM_WaitTime_WD",
                                                      new_field_alias="Avg_PeakPM_WaitTime_WD", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (6) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_LatePM_WaitTime_WD",
                                                      new_field_name="Avg_LatePM_WaitTime_WD",
                                                      new_field_alias="Avg_LatePM_WaitTime_WD", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (7) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_AllDay_WaitTime_WE",
                                                      new_field_name="Avg_AllDay_WaitTime_WE",
                                                      new_field_alias="Avg_AllDay_WaitTime_WE", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (8) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_EarlyAM_WaitTime_WE",
                                                      new_field_name="Avg_EarlyAM_WaitTime_WE",
                                                      new_field_alias="Avg_EarlyAM_WaitTime_WE", field_type="DOUBLE",
                                                      field_length=8, field_is_nullable="NULLABLE",
                                                      clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (9) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_PeakAM_WaitTime_WE",
                                                       new_field_name="Avg_PeakAM_WaitTime_WE",
                                                       new_field_alias="Avg_PeakAM_WaitTime_WE", field_type="DOUBLE",
                                                       field_length=8, field_is_nullable="NULLABLE",
                                                       clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (10) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_MidDay_WaitTime_WE",
                                                       new_field_name="Avg_MidDay_WaitTime_WE",
                                                       new_field_alias="Avg_MidDay_WaitTime_WE", field_type="DOUBLE",
                                                       field_length=8, field_is_nullable="NULLABLE",
                                                       clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (11) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_PeakPM_WaitTime_WE",
                                                       new_field_name="Avg_PeakPM_WaitTime_WE",
                                                       new_field_alias="Avg_PeakPM_WaitTime_WE", field_type="DOUBLE",
                                                       field_length=8, field_is_nullable="NULLABLE",
                                                       clear_field_alias="DO_NOT_CLEAR")

    # Process: Alter Field (12) (Alter Field)
    arcpy.AlterField_management(in_table=src_all_bus_stops, field="Avg_LatePM_WaitTime_WE",
                                                       new_field_name="Avg_LatePM_WaitTime_WE",
                                                       new_field_alias="Avg_LatePM_WaitTime_WE", field_type="DOUBLE",
                                                       field_length=8, field_is_nullable="NULLABLE",
                                                       clear_field_alias="DO_NOT_CLEAR")

    log_message = "Performing Housekeeping Tasks ..."
    logger.info(log_message)

    if arcpy.Exists(gtfs_busProj):
        arcpy.Delete_management(gtfs_busProj, "FeatureClass")

    log_message = "Clipping Bus Points by the Study Area ..."
    logger.info(log_message)

    if arcpy.Exists(bus_taz_stops):
        arcpy.Delete_management(bus_taz_stops, "FeatureClass")

    # Process: Clip
    arcpy.Clip_analysis(in_features=src_all_bus_stops, clip_features=taz_studyarea_proj, out_feature_class=bus_taz_stops, cluster_tolerance="")
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    GTFSAlexandriaBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSAlexandriaBusStopTimesWD")
    GTFSArlingtonBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSArlingtonBusStopTimesWD")
    GTFSArlingtonBusStopTimesWE = os.path.join(srcdata_gdb, "GTFSArlingtonBusStopTimesWE")
    GTFSFairfaxConnectorBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSFairfaxConnectorBusStopTimesWD")
    ## TEXT in StopID -- GTFSFairfaxCueBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSFairfaxCueBusStopTimesWD")
    GTFSMetroMarylandBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSMetroMarylandBusStopTimesWD")
    GTFSMontgomeryBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSMontgomeryBusStopTimesWD")
    GTFSPrinceGeorgeBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSPrinceGeorgeBusStopTimesWD")
    ## TEXT in StopID -- GTFSRegionalMarylandBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSRegionalMarylandBusStopTimesWD")
    ## TEXT in StopID -- GTFSRegionalMarylandBusStopTimesWE = os.path.join(srcdata_gdb, "GTFSRegionalMarylandBusStopTimesWE")
    GTFSWMATACirculatorBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSWMATACirculatorBusStopTimesWD")
    ## TEXT in StopID -- GTFSWoodbridgeBusStopTimesWD = os.path.join(srcdata_gdb, "GTFSWoodbridgeBusStopTimesWD")

    busTimesTbl = wkspcdata_gdb + "\\GTFS_Bus_Times"

    log_message = "Merging all GTFS Bus Times in the Study Area ..."
    logger.info(log_message)

    if arcpy.Exists(busTimesTbl):
        arcpy.Delete_management(busTimesTbl, "Table")

    # Bad Data in trip_id --- trip_id \"trip_id\" true true false 4 Long 0 10
    arcpy.Merge_management(inputs=[GTFSAlexandriaBusStopTimesWD, GTFSArlingtonBusStopTimesWD, GTFSArlingtonBusStopTimesWE,
                GTFSFairfaxConnectorBusStopTimesWD, GTFSMetroMarylandBusStopTimesWD, GTFSMontgomeryBusStopTimesWD, GTFSPrinceGeorgeBusStopTimesWD,
                GTFSWMATACirculatorBusStopTimesWD], output=busTimesTbl, field_mappings="trip_id \"trip_id\" true true false 2147483647 Text 0 0,First,#," + GTFSAlexandriaBusStopTimesWD + ",trip_id,0,2147483647," + GTFSArlingtonBusStopTimesWD + ",trip_id,0,2147483647," + GTFSArlingtonBusStopTimesWE + ",trip_id,0,2147483647," + GTFSFairfaxConnectorBusStopTimesWD + ",trip_id,0,2147483647," + GTFSMetroMarylandBusStopTimesWD + ",trip_id,0,2147483647," + GTFSMontgomeryBusStopTimesWD + ",trip_id,0,2147483647," + GTFSPrinceGeorgeBusStopTimesWD + ",trip_id,0,2147483647," + GTFSWMATACirculatorBusStopTimesWD + ",trip_id,0,2147483647; \
                arrival_time \"arrival_time\" true true false 2147483647 Text 0 0,First,#," + GTFSAlexandriaBusStopTimesWD + ",arrival_time,0,2147483647," + GTFSArlingtonBusStopTimesWD + ",arrival_time,0,2147483647," + GTFSArlingtonBusStopTimesWE + ",arrival_time,0,2147483647," + GTFSFairfaxConnectorBusStopTimesWD + ",arrival_time,0,2147483647," + GTFSMetroMarylandBusStopTimesWD + ",arrival_time,0,2147483647," + GTFSMontgomeryBusStopTimesWD + ",arrival_time,0,2147483647," + GTFSPrinceGeorgeBusStopTimesWD + ",arrival_time,0,2147483647," + GTFSWMATACirculatorBusStopTimesWD + ",arrival_time,0,2147483647; \
                departure_time \"departure_time\" true true false 2147483647 Text 0 0,First,#," + GTFSAlexandriaBusStopTimesWD + ",departure_time,0,2147483647," + GTFSArlingtonBusStopTimesWD + ",departure_time,0,2147483647," + GTFSArlingtonBusStopTimesWE + ",departure_time,0,2147483647," + GTFSFairfaxConnectorBusStopTimesWD + ",departure_time,0,2147483647," + GTFSMetroMarylandBusStopTimesWD + ",departure_time,0,2147483647," + GTFSMontgomeryBusStopTimesWD + ",departure_time,0,2147483647," + GTFSPrinceGeorgeBusStopTimesWD + ",departure_time,0,2147483647," + GTFSWMATACirculatorBusStopTimesWD + ",departure_time,0,2147483647; \
                stop_id \"stop_id\" true true false 4 Long 0 10,First,#," + GTFSAlexandriaBusStopTimesWD + ",stop_id,-1,-1," + GTFSArlingtonBusStopTimesWD + ",stop_id,-1,-1," + GTFSArlingtonBusStopTimesWE + ",stop_id,-1,-1," + GTFSFairfaxConnectorBusStopTimesWD + ",stop_id,-1,-1," + GTFSMetroMarylandBusStopTimesWD + ",stop_id,-1,-1," + GTFSMontgomeryBusStopTimesWD + ",stop_id,-1,-1," + GTFSPrinceGeorgeBusStopTimesWD + ",stop_id,-1,-1," + GTFSWMATACirculatorBusStopTimesWD + ",stop_id,-1,-1")  ## , add_source="NO_SOURCE_INFO"

    ## Merge the Bus Trips tables then join Route Identifier fields to busTimesTbl
    GTFSAlexandriaBusTripsWD = os.path.join(srcdata_gdb, "GTFSAlexandriaBusTripsWD")
    GTFSArlingtonBusTripsWD = os.path.join(srcdata_gdb, "GTFSArlingtonBusTripsWD")
    GTFSArlingtonBusTripsWE = os.path.join(srcdata_gdb, "GTFSArlingtonBusTripsWE")
    GTFSFairfaxConnectorBusTripsWD = os.path.join(srcdata_gdb, "GTFSFairfaxConnectorBusTripsWD")
    ## TEXT in StopID --GTFSFairfaxCueBusTripsWE = os.path.join(srcdata_gdb, "GTFSFairfaxCueBusTripsWE")
    GTFSMetroMarylandBusTripsWD = os.path.join(srcdata_gdb, "GTFSMetroMarylandBusTripsWD")
    GTFSMontgomeryBusTripsWD = os.path.join(srcdata_gdb, "GTFSMontgomeryBusTripsWD")
    GTFSPrinceGeorgeBusTripsWD = os.path.join(srcdata_gdb, "GTFSPrinceGeorgeBusTripsWD")
    ## TEXT in StopID --GTFSRegionalMarylandBusTripsWD = os.path.join(srcdata_gdb, "GTFSRegionalMarylandBusTripsWD")
    ## TEXT in StopID --GTFSRegionalMarylandBusTripsWE = os.path.join(srcdata_gdb, "GTFSRegionalMarylandBusTripsWE")
    GTFSWMATACirculatorBusTripsWD = os.path.join(srcdata_gdb, "GTFSWMATACirculatorBusTripsWD")
    ## TEXT in StopID --GTFSWoodbridgeBusTripsWD = os.path.join(srcdata_gdb, "GTFSWoodbridgeBusTripsWD")

    busTripsTbl = wkspcdata_gdb + "\\GTFS_Bus_Trips"

    log_message = "Merging all GTFS Bus Trips in the Study Area ..."
    logger.info(log_message)

    if arcpy.Exists(busTripsTbl):
        arcpy.Delete_management(busTripsTbl, "Table")

    # Bad Data in trip_id --- trip_id \"trip_id\" true true false 4 Long 0 10
    arcpy.Merge_management(inputs=[GTFSAlexandriaBusTripsWD, GTFSArlingtonBusTripsWD, GTFSArlingtonBusTripsWE,
                GTFSFairfaxConnectorBusTripsWD, GTFSMetroMarylandBusTripsWD, GTFSMontgomeryBusTripsWD, GTFSPrinceGeorgeBusTripsWD, GTFSWMATACirculatorBusTripsWD], output=busTripsTbl, field_mappings="trip_id \"trip_id\" true true false 2147483647 Text 0 0,First,#," + GTFSAlexandriaBusTripsWD + ",trip_id,0,2147483647," + GTFSArlingtonBusTripsWD + ",trip_id,0,2147483647," + GTFSArlingtonBusTripsWE + ",trip_id,0,2147483647," + GTFSFairfaxConnectorBusTripsWD + ",trip_id,0,2147483647," + GTFSMetroMarylandBusTripsWD + ",trip_id,0,2147483647," + GTFSMontgomeryBusTripsWD + ",trip_id,0,2147483647," + GTFSPrinceGeorgeBusTripsWD + ",trip_id,0,2147483647," + GTFSWMATACirculatorBusTripsWD + ",trip_id,0,2147483647; \
                route_id \"route_id\" true true false 2147483647 Text 0 0,First,#," + GTFSAlexandriaBusTripsWD + ",route_id,0,2147483647," + GTFSArlingtonBusTripsWD + ",route_id,0,2147483647," + GTFSArlingtonBusTripsWE + ",route_id,0,2147483647," + GTFSFairfaxConnectorBusTripsWD + ",route_id,0,2147483647," + GTFSMetroMarylandBusTripsWD + ",route_id,0,2147483647," + GTFSMontgomeryBusTripsWD + ",route_id,0,2147483647," + GTFSPrinceGeorgeBusTripsWD + ",route_id,0,2147483647," + GTFSWMATACirculatorBusTripsWD + ",route_id,0,2147483647; \
                trip_headsign \"trip_headsign\" true true false 2147483647 Text 0 0,First,#," + GTFSAlexandriaBusTripsWD + ",trip_headsign,0,2147483647," + GTFSArlingtonBusTripsWD + ",trip_headsign,0,2147483647," + GTFSArlingtonBusTripsWE + ",trip_headsign,0,2147483647," + GTFSFairfaxConnectorBusTripsWD + ",trip_headsign,0,2147483647," + GTFSMetroMarylandBusTripsWD + ",trip_headsign,0,2147483647," + GTFSMontgomeryBusTripsWD + ",trip_headsign,0,2147483647," + GTFSPrinceGeorgeBusTripsWD + ",trip_headsign,0,2147483647," + GTFSWMATACirculatorBusTripsWD + ",trip_headsign,0,2147483647; \
                direction_id \"direction_id\" true true false 4 Long 0 10,First,#," + GTFSAlexandriaBusTripsWD + ",direction_id,-1,-1," + GTFSArlingtonBusTripsWD + ",direction_id,-1,-1," + GTFSArlingtonBusTripsWE + ",direction_id,-1,-1," + GTFSFairfaxConnectorBusTripsWD + ",direction_id,-1,-1," + GTFSMetroMarylandBusTripsWD + ",direction_id,-1,-1," + GTFSMontgomeryBusTripsWD + ",direction_id,-1,-1," + GTFSPrinceGeorgeBusTripsWD + ",direction_id,-1,-1," + GTFSWMATACirculatorBusTripsWD + ",direction_id,-1,-1; \
                bikes_allowed \"bikes_allowed\" true true false 4 Long 0 10,First,#," + GTFSAlexandriaBusTripsWD + ",bikes_allowed,-1,-1," + GTFSFairfaxConnectorBusTripsWD + ",bikes_allowed,-1,-1," + GTFSMetroMarylandBusTripsWD + ",bikes_allowed,-1,-1," + GTFSMontgomeryBusTripsWD + ",bikes_allowed,-1,-1," + GTFSPrinceGeorgeBusTripsWD + ",bikes_allowed,-1,-1," + GTFSWMATACirculatorBusTripsWD + ",bikes_allowed,-1,-1;")  ## , add_source="NO_SOURCE_INFO"

    log_message = "Adding/Verifying Bus Route ID fields to {}".format(bus_taz_stops)
    logger.info(log_message)

    fc_list = [f.name for f in arcpy.ListFields(bus_taz_stops)]
    field_names = ["BusRouteID1", "BusRouteID2", "BusRouteID3", "BusRouteID4", "BusRouteID5", "BusRouteID6", "BusRouteID7", "BusRouteID8", "BusRouteID9", "BusRouteID10"]
    for field_name in field_names:
        if field_name not in fc_list:
            arcpy.AddField_management(bus_taz_stops, field_name, "TEXT")

    stopCount = arcpy.GetCount_management(bus_taz_stops)
    sCount = int(stopCount[0])

    log_message = "Writing Bus Route IDs out to each allocated identifier field ..."
    logger.info(log_message)

    bOID = None
    bStopID = None
    bAgency = None
    bRouteIDAll = None
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
    rteIDStrList = []
    rteIDStr = None

    busRouteNDX = arcpy.da.UpdateCursor(bus_taz_stops, ["OBJECTID", "stop_id", "agency", "route_id_all", "BusRouteID1", "BusRouteID2", "BusRouteID3", "BusRouteID4", "BusRouteID5", "BusRouteID6", "BusRouteID7", "BusRouteID8", "BusRouteID9", "BusRouteID10"], None, None, "False", (None, None))
    for bRow in busRouteNDX:
        bOID, bStopID, bAgency, bRouteIDAll, bRouteID1, bRouteID2, bRouteID3, bRouteID4, bRouteID5, bRouteID6, bRouteID7, bRouteID8, bRouteID9, bRouteID10 = bRow[0], bRow[1], bRow[2], bRow[3], bRow[4], bRow[5], bRow[6], bRow[7], bRow[8], bRow[9], bRow[10], bRow[11], bRow[12], bRow[13]
        x = 0
        n = 4
        strRouteID = str(bRouteIDAll)
        rteIDStrList = strRouteID.split(";")
        while x < len(rteIDStrList):
            if x < 10:
                rteIDStr = str(rteIDStrList[x])
                bRow[n] = rteIDStr.strip(" ")
                busRouteNDX.updateRow(bRow)
                x += 1
                n += 1
            else:
                break

        log_message = "Route ID is ready on Stop {} of {}".format(bStopID, bAgency)
        logger.info(log_message)

    del bRow
    del busRouteNDX
    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% DATA PREP - END %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% BUS TAZ CENTERLINE BUILD - SATRT %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Bus Stops are ready for route centerline segmentation"
    logger.info(log_message)

    if arcpy.Exists(bus_route_select_temp):
        # Process: Delete Features
        arcpy.DeleteFeatures_management(in_features=bus_route_select_temp)
    else:
        log_message = "Recreating the Bus Route Selection template ..."
        logger.info(log_message)

        createBusRteSelectTemplate(wkspcdata_gdb, bus_taz_stops, logger)

    if arcpy.Exists(bus_route_stop_temp):
        # Process: Delete Features
        arcpy.DeleteFeatures_management(in_features=bus_route_stop_temp)
    else:
        log_message = "Recreating the Bus Route Stop template ..."
        logger.info(log_message)

        createBusRteStopTemplate(wkspcdata_gdb, bus_taz_stops, logger)

    if arcpy.Exists(bus_taz_rte_listLyr):
        arcpy.Delete_management(bus_taz_rte_listLyr, "FeatureClass")

    if arcpy.Exists(bus_route_temp):
        log_message = "Clearing Bus Route Line template ..."
        logger.info(log_message)

        arcpy.DeleteFeatures_management(in_features=bus_route_temp)

    if arcpy.Exists(bus_data_centerline):
        log_message = "Clearing Bus TAZ Centerline ..."
        logger.info(log_message)

        arcpy.DeleteFeatures_management(in_features=bus_data_centerline)

    log_message = "Dissolving Bus Stops by Route ID ..."
    logger.info(log_message)

    # Process: Dissolve (Dissolve)
    arcpy.Dissolve_management(in_features=bus_taz_stops, out_feature_class=bus_taz_rte_listLyr,
                              dissolve_field=["BusRouteID1"], statistics_fields=[], multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")

    if arcpy.Exists(bus_taz_rteList):
        arcpy.Delete_management(bus_taz_rteList, "Table")

    log_message = "Creating the Route ID List: {}".format(bus_taz_rteList)
    logger.info(log_message)

    # CONTROL Process: where_clause="BusRouteID1 = '77'"  Table To Table -- BusRouteID1 = '77'
    arcpy.TableToTable_conversion(in_rows=bus_taz_rte_listLyr, out_path=wkspcdata_gdb, out_name="Bus_TAZ_RouteList", where_clause="", field_mapping="BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0,First,#," + bus_taz_rte_listLyr + ",BusRouteID1,0,255", config_keyword="")

    log_message = "Housekeeping on dissolve layer ..."
    logger.info(log_message)

    # Process: Delete (Delete)
    arcpy.Delete_management(bus_taz_rte_listLyr, "FeatureClass")

    log_message = "Clarifying bus operator route identifiers in {}".format(src_ncrtpb_bus_lines)
    logger.info(log_message)

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(src_ncrtpb_bus_lines, "OperRtNM", "clarifyRoutes( !OperRtNM! )", "PYTHON_9.3", "def clarifyRoutes(lazyName):\\n  i = 0\\n  n = 0\\n  listLen = 0\\n  routeChar = \"\"\\n  fullRoutes = \"\"\\n  n = lazyName.find(\",\")\\n  if n == -1:\\n    fullRoutes = lazyName\\n  else:\\n    routesStr = str(lazyName)\\n    routeList = routesStr.split(\",\")\\n    routeLead = routeList[0]\\n    routeAlpha = routeLead[0]\\n    if routeAlpha == \"A\" or routeAlpha == \"B\" or routeAlpha == \"C\" or routeAlpha == \"D\" or routeAlpha == \"E\" or routeAlpha == \"F\" or routeAlpha == \"G\" or routeAlpha == \"H\" or routeAlpha == \"J\" or routeAlpha == \"P\" or routeAlpha == \"N\" or routeAlpha == \"Q\" or routeAlpha == \"L\" or routeAlpha == \"S\" or routeAlpha == \"V\" or routeAlpha == \"Y\":\\n      listLen = len(routeList)\\n      fullRoutes = routeLead\\n      if listLen > 1:\\n        while i < listLen - 1:\\n          routeLead = routeList[i + 1]\\n          if routeLead == \"1\" or routeLead == \"2\" or routeLead == \"3\" or routeLead == \"4\" or routeLead == \"5\" or routeLead == \"6\" or routeLead == \"7\" or routeLead == \"8\" or routeLead == \"9\" or routeLead == \"10\" or routeLead == \"11\" or routeLead == \"12\" or routeLead == \"13\" or routeLead == \"14\" or routeLead == \"15\" or routeLead == \"20\" or routeLead == \"21\" or routeLead == \"22\" or routeLead == \"23\" or routeLead == \"24\" or routeLead == \"25\" or routeLead == \"26\":\\n            fullRoutes = fullRoutes + \",\" + routeAlpha + routeLead\\n          else:\\n            fullRoutes = routesStr\\n          i += 1\\n      else:\\n        fullRoutes = routesStr\\n    else:\\n      fullRoutes = routesStr\\n  return fullRoutes\\n\\n        \\n      \\n  ")

    routeCount = arcpy.GetCount_management(bus_taz_rteList)
    rCount = int(routeCount[0])

    bRouteDir = None
    bSelectOID = None
    bSelectShape = ["SHAPE@"]
    bSelectID = None
    bSelectDirID = None
    bSelectID1 = None
    bSelectID2 = None

    bOID = None
    bRouteID = None
    bStopOID = None
    bStopShape = ["SHAPE@"]
    bStopID = None
    avgAllDayTimeWD = 0.0
    avgEarlyAMTimeWD = 0.0
    avgPeakAMTimeWD = 0.0
    avgMidDayTimeWD = 0.0
    avgPeakPMTimeWD = 0.0
    avgLatePMTimeWD = 0.0
    avgAllDayTimeWE = 0.0
    avgEarlyAMTimeWE = 0.0
    avgPeakAMTimeWE = 0.0
    avgMidDayTimeWE = 0.0
    avgPeakPMTimeWE = 0.0
    avgLatePMTimeWE = 0.0
    bAgency = None
    bRouteIDAll = None
    bRouteShrtNM = None
    bRouteDirID = None
    bRouteLocType = None
    bWheelChairLoad = 0
    bStopDesc = None
    bLat = 0.0
    bLon = 0.0
    bZoneID = None
    bStopURL = None
    bParentStation = None
    rteStopCount = 0
    totalCount = 0
    b = 0

    log_message = "All layers ready for Bus Route centerline segmentation !!!"
    logger.info(log_message)

    bStopCount = arcpy.GetCount_management(bus_taz_stops)
    bCount = int(bStopCount[0])

    log_message = "Linearizing Bus Routes from Bus Stops on the full Pedestrian-Street Network ..."
    logger.info(log_message)

    rBusRouteNDX = arcpy.da.SearchCursor(bus_taz_rteList, ["OBJECTID", "BusRouteID1"], None, None, "False", (None, None))
    for bRte in rBusRouteNDX:
        bOID, bRouteID = bRte[0], bRte[1]

        edit1 = arcpy.da.Editor(wkspcdata_gdb)

        log_message = "Beginning edit session 1 in {}".format(wkspcdata_gdb)
        logger.info(log_message)
        edit1.startEditing()

        # Cursor Search and Insert
        log_message = "Starting edit operations ..."
        logger.info(log_message)
        edit1.startOperation()

        wSelectPointNDX = arcpy.da.InsertCursor(bus_route_select_temp, ["OBJECTID", "SHAPE@", "stop_id", "direction_id_all", "BusRouteID1", "BusRouteID2"])

        rteStopCount = 0
        ### Use just primary bus stops to spatially extract the full bus route geometry
        rBusSelectNDX = arcpy.da.SearchCursor(bus_taz_stops, ["OBJECTID", "SHAPE@", "stop_id", "direction_id_all", "BusRouteID1", "BusRouteID2"], None, None, "False", (None, None))
        for bSelect in rBusSelectNDX:
            bSelectOID, bSelectShape, bSelectID, bSelectDirID, bSelectID1, bSelectID2 = bSelect[0], bSelect[1], bSelect[2], bSelect[3], bSelect[4], bSelect[5]
            if bSelectID1 == None:
                pass
            else:
                bRouteDir = ""
                if bRouteID == str(bSelectID1):
                    wSelectPointNDX.insertRow([bSelectOID, bSelectShape, bSelectID, bSelectDirID, bSelectID1, bSelectID2])

        del rBusSelectNDX
        del wSelectPointNDX

        selectCount = arcpy.GetCount_management(bus_route_select_temp)
        sCount = int(selectCount[0])

        if sCount > 0:
            ### Use all bus stops for the route to spatially assign transfer/wait times to each route segment in each TAZ
            wBusRouteNDX = arcpy.da.InsertCursor(bus_route_stop_temp, ["OBJECTID", "SHAPE@", "stop_id", "Avg_AllDay_WaitTime_WD",
                                                  "Avg_EarlyAM_WaitTime_WD", "Avg_PeakAM_WaitTime_WD", "Avg_MidDay_WaitTime_WD",
                                                  "Avg_PeakPM_WaitTime_WD", "Avg_LatePM_WaitTime_WD", "Avg_AllDay_WaitTime_WE",
                                                  "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE", "Avg_MidDay_WaitTime_WE",
                                                  "Avg_PeakPM_WaitTime_WE", "Avg_LatePM_WaitTime_WE", "agency",
                                                  "route_id_all", "route_short_name_all", "direction_id_all", "location_type",
                                                  "wheelchair_boarding", "stop_desc", "stop_lat", "stop_lon", "zone_id", "stop_url",
                                                  "parent_station", "BusRouteID1", "BusRouteID2", "BusRouteID3", "BusRouteID4",
                                                  "BusRouteID5", "BusRouteID6", "BusRouteID7", "BusRouteID8", "BusRouteID9", "BusRouteID10"])

            rBusStopsNDX = arcpy.da.SearchCursor(bus_taz_stops, ["OBJECTID", "SHAPE@", "stop_id", "Avg_AllDay_WaitTime_WD",
                                                  "Avg_EarlyAM_WaitTime_WD", "Avg_PeakAM_WaitTime_WD", "Avg_MidDay_WaitTime_WD",
                                                  "Avg_PeakPM_WaitTime_WD", "Avg_LatePM_WaitTime_WD", "Avg_AllDay_WaitTime_WE",
                                                  "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE", "Avg_MidDay_WaitTime_WE",
                                                  "Avg_PeakPM_WaitTime_WE", "Avg_LatePM_WaitTime_WE", "agency", "route_id_all",
                                                  "route_short_name_all", "direction_id_all", "location_type", "wheelchair_boarding",
                                                  "stop_desc", "stop_lat", "stop_lon", "zone_id", "stop_url", "parent_station",
                                                  "BusRouteID1", "BusRouteID2", "BusRouteID3", "BusRouteID4", "BusRouteID5",
                                                  "BusRouteID6", "BusRouteID7", "BusRouteID8", "BusRouteID9", "BusRouteID10"],
                                                  None, None, "False", (None, None))
            for bStop in rBusStopsNDX:
                bStopOID, bStopShape, bStopID, avgAllDayTimeWD, avgEarlyAMTimeWD, avgPeakAMTimeWD, avgMidDayTimeWD, avgPeakPMTimeWD,\
                avgLatePMTimeWD, avgAllDayTimeWE, avgEarlyAMTimeWE, avgPeakAMTimeWE, avgMidDayTimeWE, avgPeakPMTimeWE, avgLatePMTimeWE,\
                bAgency, bRouteIDAll, bRouteShrtNM, bRouteDirID, bRouteLocType, bWheelChairLoad, bStopDesc, bLat, bLon, bZoneID, bStopURL,\
                bParentStation, bRouteID1, bRouteID2, bRouteID3, bRouteID4, bRouteID5, bRouteID6, bRouteID7, bRouteID8, bRouteID9, bRouteID10 = \
                bStop[0], bStop[1], bStop[2], bStop[3], bStop[4], bStop[5], bStop[6], bStop[7], bStop[8], bStop[9], bStop[10], bStop[11], bStop[12],\
                bStop[13], bStop[14], bStop[15], bStop[16], bStop[17], bStop[18], bStop[19], bStop[20], bStop[21], bStop[22], bStop[23], bStop[24], \
                bStop[25], bStop[26], bStop[27], bStop[28], bStop[29], bStop[30], bStop[31], bStop[32], bStop[33], bStop[34], bStop[35], bStop[36]
                if bRouteID == None:
                    pass
                else:
                    bRouteLocType = ""
                    if bRouteID == str(bRouteID1) or bRouteID == str(bRouteID2) or bRouteID == str(bRouteID3) or bRouteID == str(bRouteID4) or bRouteID == str(bRouteID5) or bRouteID == str(bRouteID6) or bRouteID == str(bRouteID7) or bRouteID == str(bRouteID8) or bRouteID == str(bRouteID9) or bRouteID == str(bRouteID10):
                        rteStopCount += 1
                        if bRouteID2 != None:
                            ## Need GTFS overlay values completed here...
                            bRouteLocType = "transfer"
                            avgAllDayTimeWD = avgAllDayTimeWD/3
                            avgEarlyAMTimeWD = avgEarlyAMTimeWD/3
                            avgPeakAMTimeWD = avgPeakAMTimeWD/3
                            avgMidDayTimeWD = avgMidDayTimeWD/3
                            avgPeakPMTimeWD = avgPeakPMTimeWD/3
                            avgLatePMTimeWD = avgLatePMTimeWD/3
                            avgAllDayTimeWE = avgAllDayTimeWE/3
                            avgEarlyAMTimeWE = avgEarlyAMTimeWE/3
                            avgPeakAMTimeWE = avgPeakAMTimeWE/3
                            avgMidDayTimeWE = avgMidDayTimeWE/3
                            avgPeakPMTimeWE = avgPeakPMTimeWE/3
                            avgLatePMTimeWE = avgLatePMTimeWE/3
                        else:
                            avgAllDayTimeWD = 0.0
                            avgEarlyAMTimeWD = 0.0
                            avgPeakAMTimeWD = 0.0
                            avgMidDayTimeWD = 0.0
                            avgPeakPMTimeWD = 0.0
                            avgLatePMTimeWD = 0.0
                            avgAllDayTimeWE = 0.0
                            avgEarlyAMTimeWE = 0.0
                            avgPeakAMTimeWE = 0.0
                            avgMidDayTimeWE = 0.0
                            avgPeakPMTimeWE = 0.0
                            avgLatePMTimeWE = 0.0

                        wBusRouteNDX.insertRow([bStopOID, bStopShape, bStopID, avgAllDayTimeWD, avgEarlyAMTimeWD, avgPeakAMTimeWD, avgMidDayTimeWD, avgPeakPMTimeWD,
                                                avgLatePMTimeWD, avgAllDayTimeWE, avgEarlyAMTimeWE, avgPeakAMTimeWE, avgMidDayTimeWE, avgPeakPMTimeWE, avgLatePMTimeWE,
                                                bAgency, bRouteIDAll, bRouteShrtNM, bRouteDirID, bRouteLocType, bWheelChairLoad, bStopDesc, bLat, bLon, bZoneID, bStopURL,
                                                bParentStation, bRouteID1, bRouteID2, bRouteID3, bRouteID4, bRouteID5, bRouteID6, bRouteID7, bRouteID8, bRouteID9, bRouteID10])

            del rBusStopsNDX
            del wBusRouteNDX

            log_message = "Stopping edit operations ..."
            logger.info(log_message)
            edit1.stopOperation()

            log_message = "Ending edit session 1 in {}".format(wkspcdata_gdb)
            logger.info(log_message)
            edit1.stopEditing(True)

            log_message = "Isolating Route {} by proximity to {} Bus Stops".format(bRouteID, rteStopCount)
            logger.info(log_message)

            if arcpy.Exists(proxy_route_temp):
                arcpy.Delete_management(proxy_route_temp, "FeatureClass")

            ## Process: Spatial Join -- Use just primary bus stops to spatially extract the full bus route geometry
            arcpy.SpatialJoin_analysis(src_ncrtpb_bus_lines, bus_route_select_temp, proxy_route_temp, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "TransitRouteID \"Transit Route ID\" true true false 4 Long 0 0 ,First,#," + src_ncrtpb_bus_lines + ",TransitRouteID,-1,-1;TransitRoute \"Transit Route Number\" true true false 254 Text 0 0 ,First,#," + src_ncrtpb_bus_lines + ",TransitRoute,-1,-1;OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + src_ncrtpb_bus_lines + ",OperRtNM,-1,-1;FullRtName \"Full Route Name\" true true false 75 Text 0 0 ,First,#," + src_ncrtpb_bus_lines + ",FullRtName,-1,-1;Operator \"Operator\" true true false 254 Text 0 0 ,First,#," + src_ncrtpb_bus_lines + ",Operator,-1,-1;Headyway \"Headway\" true true false 4 Long 0 0 ,First,#," + src_ncrtpb_bus_lines + ",Headyway,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + src_ncrtpb_bus_lines + ",Shape_Length,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_route_select_temp + ",direction_id_all,-1,-1", "INTERSECT", "0.005 Miles", "")

            if arcpy.Exists(bus_route_temp):
                pass
            else:
                log_message = "Recreating the Bus Routes template ..."
                logger.info(log_message)

                createBusRouteLnTemplate(wkspcdata_gdb, proxy_route_temp, logger)

                log_message = "Clearing template ..."
                logger.info(log_message)

                arcpy.DeleteFeatures_management(in_features=bus_route_temp)

            edit2 = arcpy.da.Editor(wkspcdata_gdb)

            log_message = "Beginning edit session 2 in {}".format(wkspcdata_gdb)
            logger.info(log_message)
            edit2.startEditing()

            # Cursor Search and Insert
            log_message = "Starting edit operations ..."
            logger.info(log_message)
            edit2.startOperation()

            log_message = "Filtering by Agency Route Name..."
            logger.info(log_message)

            bLnOID = None
            bLnShape = ["SHAPE@"]
            bLnRteID = None
            bLnTransitRte = None
            bLnRteNM = None
            bLnRteFullNM = None
            bLnOperator = None
            bLnHeadway = None
            bLnDirection = None
            bLnShapeLength = 0.0
            opLnRteNM = None
            opLnRteNdx = 0

            wSelectRouteNDX = arcpy.da.InsertCursor(bus_route_temp, ["OBJECTID", "SHAPE@", "TransitRouteID", "TransitRoute", "OperRtNM", "FullRtName", "Operator", "Headyway", "direction_id_all", "Shape_Length"])

            rBusSelectLN = arcpy.da.SearchCursor(proxy_route_temp, ["OBJECTID", "SHAPE@", "TransitRouteID", "TransitRoute", "OperRtNM", "FullRtName", "Operator", "Headyway", "direction_id_all", "Shape_Length"], None, None, "False", (None, None))
            for bLN in rBusSelectLN:
                bLnOID, bLnShape, bLnRteID, bLnTransitRte, bLnRteNM, bLnRteFullNM, bLnOperator, bLnHeadway, bLnDirection, bLnShapeLength = bLN[0], bLN[1], bLN[2], bLN[3], bLN[4], bLN[5], bLN[6], bLN[7], bLN[8], bLN[9]
                opLnRteNM = str(bLnRteNM)
                opLnRteNdx = opLnRteNM.find(bRouteID)
                if opLnRteNdx == -1:
                    pass
                else:
                    wSelectRouteNDX.insertRow([bLnOID, bLnShape, bLnRteID, bLnTransitRte, bLnRteNM, bLnRteFullNM, bLnOperator, bLnHeadway, bLnDirection, bLnShapeLength])

            del rBusSelectLN
            del wSelectRouteNDX

            # # Process: Segment one Bus Route of data at a time
            log_message = "Starting segmentation of Bus Route {} for attribution".format(str(bRouteID))
            logger.info(log_message)

            log_message = "Stopping edit operations ..."
            logger.info(log_message)
            edit2.stopOperation()

            log_message = "Ending edit session 2 in {}".format(wkspcdata_gdb)
            logger.info(log_message)
            edit2.stopEditing(True)

            if arcpy.Exists(bus_route):
                arcpy.Delete_management(bus_route, "FeatureClass")

            log_message = "Dissolving route lines ..."
            logger.info(log_message)

            # Process: Dissolve
            arcpy.Dissolve_management(bus_route_temp, bus_route, "OBJECTID;OperRtNM;Operator", "direction_id_all FIRST", "MULTI_PART", "DISSOLVE_LINES")

            if arcpy.Exists(bus_route_m):
                arcpy.Delete_management(bus_route_m, "FeatureClass")

            log_message = "Creating M-Enabled Bus Route {} traversal...".format(str(bRouteID))
            logger.info(log_message)

            # Process: Create Routes
            arcpy.CreateRoutes_lr(bus_route, "OperRtNM", bus_route_m, "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

            ## %%%%%%%%%%%%%%%%%%%%%%%%%%%% NEW CODE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            log_message = "Extending Line (5 meters) in : " + bus_route_m
            logger.info(log_message)

            # Process: Extend Line - Reset intersections of segments up to 5.0 meters
            arcpy.ExtendLine_edit(bus_route_m, "5 Meters", "EXTENSION")

            if arcpy.Exists(bus_route_m_links):
                arcpy.Delete_management(bus_route_m_links, "FeatureClass")

            log_message = "Splitting traversal at Bus Stops ..."
            logger.info(log_message)

            # Process: Split Line at Point
            arcpy.SplitLineAtPoint_management(bus_route_m, bus_route_stop_temp, bus_route_m_links, "0.015 Miles")
            ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            if arcpy.Exists(bus_route_link_data):
                arcpy.Delete_management(bus_route_link_data, "FeatureClass")

            log_message = "Joining Bus Stop Transfer Data in: {}".format(bus_route_link_data)
            logger.info(log_message)

            # Process: Spatial Join
            arcpy.SpatialJoin_analysis(bus_route_m_links, bus_route_stop_temp, bus_route_link_data, "JOIN_ONE_TO_ONE", "KEEP_ALL", "OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + bus_route_m_links + ",OperRtNM,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + bus_route_m_links + ",Shape_Length,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_route_stop_temp + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_PeakPM_WaitTime_WD,-1,-1;Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_PeakPM_WaitTime_WE,-1,-1;Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_route_stop_temp + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_route_stop_temp + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_route_stop_temp + ",direction_id_all,-1,-1;location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_route_stop_temp + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + bus_route_stop_temp + ",wheelchair_boarding,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_route_stop_temp + ",stop_lon,-1,-1;stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_route_stop_temp + ",stop_url,-1,-1;parent_station \"parent_station\" true true false 2147483647 Text 0 0 ,First,#," + bus_route_stop_temp + ",parent_station,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID1,-1,-1;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID2,-1,-1;BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID3,-1,-1;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID4,-1,-1;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID5,-1,-1;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID6,-1,-1;BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID7,-1,-1;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID8,-1,-1;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID9,-1,-1;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + bus_route_stop_temp + ",BusRouteID10,-1,-1", "INTERSECT", "0.015 Miles", "")

            if arcpy.Exists(bus_data_centerline):
                pass
            else:
                log_message = "Recreating the Bus Data Centerline ..."
                logger.info(log_message)

                createBusCenterlineTemplate(wkspcdata_gdb, bus_route_link_data, logger)

                log_message = "Clearing template ..."
                logger.info(log_message)

                arcpy.DeleteFeatures_management(in_features=bus_data_centerline)

            log_message = "Appending Route {} Data to the BUS Data Centerline".format(str(bRouteID))
            logger.info(log_message)

            # Process: Append
            arcpy.Append_management(bus_route_link_data, bus_data_centerline, "NO_TEST", "OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + bus_route_link_data + ",OperRtNM,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_route_link_data + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_PeakPM_WaitTime_WD,-1,-1;Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_PeakPM_WaitTime_WE,-1,-1;Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_route_link_data + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_route_link_data + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_route_link_data + ",direction_id_all,-1,-1;location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_route_link_data + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + bus_route_link_data + ",wheelchair_boarding,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_route_link_data + ",stop_lon,-1,-1;stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_route_link_data + ",stop_url,-1,-1;parent_station \"parent_station\" true true false 2147483647 Text 0 0 ,First,#," + bus_route_link_data + ",parent_station,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID1,-1,-1;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID2,-1,-1;BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID3,-1,-1;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID4,-1,-1;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID5,-1,-1;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID6,-1,-1;BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID7,-1,-1;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID8,-1,-1;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID9,-1,-1;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + bus_route_link_data + ",BusRouteID10,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + bus_route_link_data + ",Shape_Length,-1,-1", "")

            log_message = "Route {} Centerline complete".format(str(bRouteID))
            logger.info(log_message)

            arcpy.DeleteFeatures_management(in_features=bus_route_select_temp)
            arcpy.DeleteFeatures_management(in_features=bus_route_stop_temp)

        else:
            ## bRouteID bus stops not found
            log_message = "No Bus Stops found on Route {}".format(str(bRouteID))
            logger.info(log_message)

            log_message = "Stopping edit operations ..."
            logger.info(log_message)
            edit1.stopOperation()

            log_message = "Ending edit session 1 in {}".format(wkspcdata_gdb)
            logger.info(log_message)
            edit1.stopEditing(True)

        totalCount += rteStopCount

    del rBusRouteNDX

    log_message = "Processed {} bus stops for {} distinct bus routes".format(totalCount, rCount)
    logger.info(log_message)

    log_message = "Performing Housekeeping Tasks ..."
    logger.info(log_message)

    if arcpy.Exists(bus_route):
        arcpy.Delete_management(bus_route, "FeatureClass")

    if arcpy.Exists(bus_route_m):
        arcpy.Delete_management(bus_route_m, "FeatureClass")

    if arcpy.Exists(bus_route_temp):
        arcpy.Delete_management(bus_route_temp, "FeatureClass")

    if arcpy.Exists(bus_route_link_data):
        arcpy.Delete_management(bus_route_link_data, "FeatureClass")

    if arcpy.Exists(bus_route_m_links):
        arcpy.Delete_management(bus_route_m_links, "FeatureClass")

    dataCount = arcpy.GetCount_management(bus_data_centerline)
    dCount = int(dataCount[0])

    log_message = "Filtering {}".format(bus_data_centerline)
    logger.info(log_message)

    bOID = None
    bShape = ["SHAPE@"]
    agency = None
    x = 0
    xRecNDX = arcpy.da.UpdateCursor(bus_data_centerline, ["OBJECTID", "SHAPE@", "agency"], None, None, "False", (None, None))
    for xRow in xRecNDX:
        bOID, bShape, agency = xRow[0], xRow[1], xRow[2]
        if agency == None:
            x += 1
            xRecNDX.deleteRow()
        else:
            pass

    del xRow
    del xRecNDX

    log_message = "Cleared {} null records of {} in {}".format(str(x), dCount, bus_data_centerline)
    logger.info(log_message)

    if arcpy.Exists(bus_data_centerline_clip):
        arcpy.Delete_management(bus_data_centerline_clip, "FeatureClass")

    log_message = "Clipping Bus_Data_Centerline by TAZ Polygons for: {}".format(bus_data_centerline_clip)
    logger.info(log_message)

    # Process: Clip
    arcpy.Clip_analysis(bus_data_centerline, taz_studyarea_proj, bus_data_centerline_clip, "")

    ## Shift back to the regional express bus route source, to clip and merge for creation of the Bus_TAZ_Centerline %%%%%%%%%%%
    if arcpy.Exists(src_ncrtpb_bus_lines_m):
        arcpy.Delete_management(src_ncrtpb_bus_lines_m, "FeatureClass")

    log_message = "Creating M-Enabled Express Bus Routes from {}".format(src_ncrtpb_bus_lines)
    logger.info(log_message)

    # Process: Create Routes
    arcpy.CreateRoutes_lr(src_ncrtpb_bus_lines, "OperRtNM", src_ncrtpb_bus_lines_m, "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    log_message = "Extending Line (5 meters) in : " + src_ncrtpb_bus_lines_m
    logger.info(log_message)

    # Process: Extend Line - Reset intersections of segments up to 5.0 meters
    arcpy.ExtendLine_edit(src_ncrtpb_bus_lines_m, "5 Meters", "EXTENSION")

    if arcpy.Exists(src_bus_centerline):
        arcpy.Delete_management(src_bus_centerline, "FeatureClass")

    log_message = "Splitting traversal at Bus Stops to create {}".format(src_bus_centerline)
    logger.info(log_message)

    # Process: Split Line at Point
    arcpy.SplitLineAtPoint_management(src_ncrtpb_bus_lines_m, bus_route_stop_temp, src_bus_centerline, "0.015 Miles")

    if arcpy.Exists(src_bus_centerline_clip):
        arcpy.Delete_management(src_bus_centerline_clip, "FeatureClass")

    log_message = "Clipping Express Bus_Data_Centerline by TAZ Polygons for: {}".format(src_bus_centerline_clip)
    logger.info(log_message)

    # Process: Clip (2)
    arcpy.Clip_analysis(src_bus_centerline, taz_studyarea_proj, src_bus_centerline_clip, "")

    ## Merge clipped layers for merge_bus_centerline %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if arcpy.Exists(merge_bus_centerline):
        arcpy.Delete_management(merge_bus_centerline, "FeatureClass")

    log_message = "Merging Express and GTFS Metro Bus Routes for: {}".format(merge_bus_centerline)
    logger.info(log_message)

    # Process: Merge
    arcpy.Merge_management(bus_data_centerline_clip + ";" + src_bus_centerline_clip, merge_bus_centerline, "OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + bus_data_centerline_clip + ",OperRtNM,-1,-1," + src_bus_centerline_clip + ",OperRtNM,-1,-1; \
    stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_data_centerline_clip + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_AllDay_WaitTime_WD,-1,-1; \
    Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_PeakAM_WaitTime_WD,-1,-1; \
    Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_PeakPM_WaitTime_WD,-1,-1; \
    Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_AllDay_WaitTime_WE,-1,-1; \
    Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_PeakAM_WaitTime_WE,-1,-1; \
    Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_PeakPM_WaitTime_WE,-1,-1; \
    Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_data_centerline_clip + ",agency,-1,-1; \
    route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_data_centerline_clip + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_data_centerline_clip + ",direction_id_all,-1,-1; \
    location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_data_centerline_clip + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + bus_data_centerline_clip + ",wheelchair_boarding,-1,-1; \
    stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",stop_lon,-1,-1; \
    stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_data_centerline_clip + ",stop_url,-1,-1;parent_station \"parent_station\" true true false 2147483647 Text 0 0 ,First,#," + bus_data_centerline_clip + ",parent_station,-1,-1; \
    BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID1,-1,-1;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID2,-1,-1; \
    BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID3,-1,-1;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID4,-1,-1; \
    BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID5,-1,-1;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID6,-1,-1; \
    BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID7,-1,-1;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID8,-1,-1; \
    BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID9,-1,-1;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + bus_data_centerline_clip + ",BusRouteID10,-1,-1; \
    Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + bus_data_centerline_clip + ",Shape_Length,-1,-1," + src_bus_centerline_clip + ",Shape_Length,-1,-1")

    if arcpy.Exists(bus_taz_centerline):
        arcpy.Delete_management(bus_taz_centerline, "FeatureClass")

    log_message = "Running Spatial Join between Merged Bus Routes and TAZ Polygons for the Zone Name identifier in {}".format(bus_taz_centerline)
    logger.info(log_message)

    # Process: Spatial Join (3)
    arcpy.SpatialJoin_analysis(merge_bus_centerline, taz_studyarea_proj, bus_taz_centerline, "JOIN_ONE_TO_ONE", "KEEP_ALL", "OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + merge_bus_centerline + ",OperRtNM,-1,-1; \
    stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + merge_bus_centerline + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_AllDay_WaitTime_WD,-1,-1; \
    Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_PeakAM_WaitTime_WD,-1,-1; \
    Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_PeakPM_WaitTime_WD,-1,-1; \
    Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_AllDay_WaitTime_WE,-1,-1; \
    Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_PeakAM_WaitTime_WE,-1,-1; \
    Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_PeakPM_WaitTime_WE,-1,-1; \
    Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + merge_bus_centerline + ",agency,-1,-1; \
    route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + merge_bus_centerline + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + merge_bus_centerline + ",direction_id_all,-1,-1; \
    location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + merge_bus_centerline + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + merge_bus_centerline + ",wheelchair_boarding,-1,-1; \
    stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + merge_bus_centerline + ",stop_lon,-1,-1;stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + merge_bus_centerline + ",stop_url,-1,-1; \
    parent_station \"parent_station\" true true false 2147483647 Text 0 0 ,First,#," + merge_bus_centerline + ",parent_station,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID1,-1,-1; \
    BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID2,-1,-1;BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID3,-1,-1; \
    BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID4,-1,-1;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID5,-1,-1; \
    BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID6,-1,-1;BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID7,-1,-1; \
    BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID8,-1,-1;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID9,-1,-1; \
    BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + merge_bus_centerline + ",BusRouteID10,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + merge_bus_centerline + ",Shape_Length,-1,-1; \
    ZONE_NAME \"ZONE_NAME\" true true false 13 Text 0 0 ,First,#," + taz_studyarea_proj + ",name,-1,-1", "HAVE_THEIR_CENTER_IN", "", "")

    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    allBusCount = arcpy.GetCount_management(bus_taz_centerline)
    allCount = int(allBusCount[0])

    log_message = "Resolving Null fields in: {}".format(bus_taz_centerline)
    logger.info(log_message)

    busOID = None
    busOperName = None
    busAllDayXferWD = 0.0
    busEarlyAMXferWD = 0.0
    busPeakAMXferWD = 0.0
    busMidDayXferWD = 0.0
    busPeakPMXferWD = 0.0
    busLatePMXferWD = 0.0
    busAllDayXferWE = 0.0
    busEarlyAMXferWE = 0.0
    busPeakAMXferWE = 0.0
    busMidDayXferWE = 0.0
    busPeakPMXferWE = 0.0
    busLatePMXferWE = 0.0
    busAgency = None
    busRouteMain = None
    busRoutesNbr = 0
    busRouteList = []
    b = 0
    allBusNDX = arcpy.da.UpdateCursor(bus_taz_centerline, ["OBJECTID", "OperRtNM", "Avg_AllDay_WaitTime_WD",
                                                           "Avg_EarlyAM_WaitTime_WD", "Avg_PeakAM_WaitTime_WD",
                                                           "Avg_MidDay_WaitTime_WD", "Avg_PeakPM_WaitTime_WD",
                                                           "Avg_LatePM_WaitTime_WD", "Avg_AllDay_WaitTime_WE",
                                                           "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE",
                                                           "Avg_MidDay_WaitTime_WE", "Avg_PeakPM_WaitTime_WE",
                                                           "Avg_LatePM_WaitTime_WE", "agency", "BusRouteID1"], None, None, "False", (None, None))
    for abRow in allBusNDX:
        busOID, busOperName, busAllDayXferWD, busEarlyAMXferWD, busPeakAMXferWD, busMidDayXferWD, busPeakPMXferWD, \
        busLatePMXferWD, busAllDayXferWE, busEarlyAMXferWE, busPeakAMXferWE, busMidDayXferWE, busPeakPMXferWE, \
        busLatePMXferWE, busAgency, busRouteMain = abRow[0], abRow[1], abRow[2], abRow[3], abRow[4], abRow[5], \
                                                   abRow[6], abRow[7], abRow[8], abRow[9], abRow[10], abRow[11], \
                                                   abRow[12], abRow[13], abRow[14], abRow[15]
        if busAgency == None:
            b += 1
            abRow[2] = 0.0
            abRow[3] = 0.0
            abRow[4] = 0.0
            abRow[5] = 0.0
            abRow[6] = 0.0
            abRow[7] = 0.0
            abRow[8] = 0.0
            abRow[9] = 0.0
            abRow[10] = 0.0
            abRow[11] = 0.0
            abRow[12] = 0.0
            abRow[13] = 0.0

            busRoutesNbr = busOperName.find(",")

            if busRoutesNbr != -1:
                busRouteList = busOperName.split(",")
                busRouteMain = busRouteList[0]
                abRow[15] = busRouteMain
            else:
                abRow[15] = busOperName

            allBusNDX.updateRow(abRow)
        else:
            pass

    del abRow
    del allBusNDX

    log_message = "Updated {} null records of {} in {}".format(str(b), allCount, bus_taz_centerline)
    logger.info(log_message)

    log_message = "Repairing Geometry in: " + bus_taz_centerline
    logger.info(log_message)

    arcpy.RepairGeometry_management(in_features=bus_taz_centerline, delete_null="DELETE_NULL")

    log_message = "Extracting First & Last X, Y, M from Intersection Segments in: " + bus_taz_centerline + " ..."
    logger.info(log_message)

    fc_list = [f.name for f in arcpy.ListFields(bus_taz_centerline)]
    field_names = ["FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"]
    for field_name in field_names:
        if field_name not in fc_list:
            arcpy.AddField_management(bus_taz_centerline, field_name, "DOUBLE")

    field_names = ["SHAPE@"] + field_names

    with arcpy.da.UpdateCursor(bus_taz_centerline, field_names) as cursor:
        for row in cursor:
            line_geom = row[0]

            start = arcpy.PointGeometry(line_geom.firstPoint)
            start_xy = start.WKT.strip("POINT (").strip(")").split(" ")
            row[1] = start_xy[0]  # FROM_X
            row[2] = start_xy[1]  # FROM_Y

            end = arcpy.PointGeometry(line_geom.lastPoint)
            end_xy = end.WKT.strip("POINT (").strip(")").split(" ")
            row[3] = end_xy[0]  # TO_X
            row[4] = end_xy[1]  # TO_Y

            from_dfo = line_geom.firstPoint.M  ## row[5]
            to_dfo = line_geom.lastPoint.M
            if to_dfo > from_dfo:
                row[5] = from_dfo
                row[6] = to_dfo
            elif to_dfo != 0:
                row[5] = to_dfo
                row[6] = from_dfo
            cursor.updateRow(row)

    del row
    del cursor

    log_message = "Converting Meters to Miles in From_M and To_M fields ..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(bus_taz_centerline, "FROM_M", "convertAutoFrmM( !FROM_M! )", "PYTHON_9.3",
                                    "def convertAutoFrmM(fromM):\\n  inFDFO = 0  \\n  outFDFO = 0\\n  if fromM == None or fromM == 0:\\n    pass\\n  else:       \\n    inFDFO = fromM/1609.344\\n    outFDFO = str((inFDFO * 1000)/1000)\\n  return round(float(outFDFO), 3)\\n  ")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(bus_taz_centerline, "TO_M", "convertAutoToM( !TO_M! )", "PYTHON_9.3",
                                    "def convertAutoToM(toM):\\n  inTDFO = 0  \\n  outTDFO = 0\\n  if toM == None or toM == 0:\\n    pass\\n  else:       \\n    inTDFO = toM/1609.344\\n    outTDFO = str((inTDFO * 1000)/1000)\\n  return round(float(outTDFO), 3)")

    log_message = "Performing Final Housekeeping Tasks ..."
    logger.info(log_message)

    if arcpy.Exists(bus_route_stop_temp):
        arcpy.Delete_management(bus_route_stop_temp, "FeatureClass")

    if arcpy.Exists(bus_data_centerline):
        arcpy.Delete_management(bus_data_centerline, "FeatureClass")

    if arcpy.Exists(src_ncrtpb_bus_lines_m):
        arcpy.Delete_management(src_ncrtpb_bus_lines_m, "FeatureClass")

    if arcpy.Exists(bus_route_select_temp):
        arcpy.Delete_management(bus_route_select_temp, "FeatureClass")

    if arcpy.Exists(src_bus_centerline):
        arcpy.Delete_management(src_bus_centerline, "FeatureClass")

    if arcpy.Exists(bus_data_centerline_clip):
        arcpy.Delete_management(bus_data_centerline_clip, "FeatureClass")

    if arcpy.Exists(src_bus_centerline_clip):
        arcpy.Delete_management(src_bus_centerline_clip, "FeatureClass")

    if arcpy.Exists(merge_bus_centerline):
        arcpy.Delete_management(merge_bus_centerline, "FeatureClass")

    log_message = "Adding/Updating Bus Route Mode Code ..."
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(bus_taz_centerline, "RouteModeCD", "TEXT", "", "", "3", "RouteModeCD", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (3)
    arcpy.CalculateField_management(bus_taz_centerline, "RouteModeCD", "\"2\"", "PYTHON_9.3", "")

    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Repairing Geometry in: {}".format(bus_taz_stops)
    logger.info(log_message)

    arcpy.RepairGeometry_management(in_features=bus_taz_stops, delete_null="DELETE_NULL")

    spatial_ref = arcpy.Describe(bus_taz_stops).spatialReference

    log_message = "Extracting X, Y Coordinates from: {}".format(bus_taz_stops)
    logger.info(log_message)

    pnt_list = [p.name for p in arcpy.ListFields(bus_taz_stops)]
    field_nms = ["STOP_X", "STOP_Y"]
    for field_nm in field_nms:
        if field_nm not in pnt_list:
            arcpy.AddField_management(bus_taz_stops, field_nm, "DOUBLE")

    field_nms = ["SHAPE@"] + field_nms

    with arcpy.da.UpdateCursor(bus_taz_stops, field_nms) as pCursor:
        for pRow in pCursor:
            pnt_geom = pRow[0]

            pStop = arcpy.PointGeometry(pnt_geom.firstPoint, spatial_ref)
            pStop_XY = pStop.WKT.strip("POINT (").strip(")").split(" ")
            pRow[1] = pStop_XY[0]  # STOP_X
            pRow[2] = pStop_XY[1]  # STOP_Y

            pCursor.updateRow(pRow)

    del pRow
    del pCursor

    log_message = "Adding/Updating Bus Stop GeoID in {}".format(bus_taz_stops)
    logger.info(log_message)

    geoid_list = [g.name for g in arcpy.ListFields(bus_taz_stops)]
    geoid_nms = ["GeoID"]
    for geoid_nm in geoid_nms:
        if geoid_nm not in geoid_list:
            arcpy.AddField_management(bus_taz_stops, "GeoID", "TEXT", "", "", "30", "GeoID", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (3)
    arcpy.CalculateField_management(bus_taz_stops, "GeoID", "createGeoID( !STOP_Y! , !STOP_X! )", "PYTHON_9.3",
                                    "def createGeoID(stop_y, stop_x):\\n  retID = \"\"\\n  if stop_y == None or stop_x == None:\\n    pass\\n  else:\\n    retID = str(round(stop_y, 8)) + \",\" + str(round(stop_x, 8))\\n  return retID")
    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    log_message = "Bus Route Centerline is complete -- Ready for the ND Build and Linear Metrics"
    logger.info(log_message)

    return "%%%%%%% Process E3 Complete %%%%%%%"

def segmentRailLines(srcdata_gdb, mstaging_gdb, wkspcdata_gdb, cgctemp_gdb, logger):

    log_message = "%%%%%%% Process E4 - Segment and Synthesize Rail Lines for the Multimodal Transit Network Dataset Build %%%%%%%"
    logger.info(log_message)

    taz_studyarea_proj = os.path.join(wkspcdata_gdb, "WDC_TAZ_StudyArea")
    mwcog_rail_stops = os.path.join(mstaging_gdb, "MWCOG_Rail_Stations")
    mwcog_rail_lines = os.path.join(mstaging_gdb, "MWCOG_Rail_Lines")
    ucb_rail_lines = os.path.join(mstaging_gdb, "UCB_Rails")
    src_ncrtpb_rail_stops = wkspcdata_gdb + "\\SRC_NCRTPB_RailStops"
    src_ncrtpb_rail_lines = wkspcdata_gdb + "\\SRC_NCRTPB_RailLines"
    src_ucb_rail_lines = wkspcdata_gdb + "\\SRC_UCB_RailLines"
    src_all_rail_lines = wkspcdata_gdb + "\\SRC_All_RailLines"
    rail_service_lines = wkspcdata_gdb + "\\Rail_Service_Lines"
    rail_service_lineM = wkspcdata_gdb + "\\Rail_Service_LineM"
    rail_service_sortM = wkspcdata_gdb + "\\Rail_Service_SortM"
    rail_taz_sortM = wkspcdata_gdb + "\\Rail_TAZ_SortM"
    rail_taz_path = wkspcdata_gdb + "\\Rail_TAZ_Path"
    rail_taz_centerline = wkspcdata_gdb + "\\Rail_TAZ_Centerline"
    gtfs_railTemp = cgctemp_gdb + "\\GTFS_RailTemplate"
    gtfs_railProj = wkspcdata_gdb + "\\GTFS_RailPntsProjected"
    src_gtfs_rail_stops = wkspcdata_gdb + "\\SRC_GTFS_RailStops"
    src_all_rail_stops = wkspcdata_gdb + "\\SRC_All_RailStops"
    rail_taz_stops = wkspcdata_gdb + "\\Rail_TAZ_StopPoints"
    bus_taz_stops = wkspcdata_gdb + "\\Bus_TAZ_StopPoints"
    rail_taz_transferpnt = wkspcdata_gdb + "\\Rail_TAZ_TransferPoints"
    transit_taz_pointdiff = wkspcdata_gdb + "\\Transit_TAZ_PointDiff"
    transit_transfer_stations = wkspcdata_gdb + "\\Transit_Transfer_Stations"
    rail_taz_stops_temp = wkspcdata_gdb + "\\Rail_TAZ_Stops_Temp"
    rail_taz_stations = wkspcdata_gdb + "\\Rail_TAZ_Stations"
    rail_taz_stoplist = wkspcdata_gdb + "\\Rail_TAZ_StopList"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% DATA PREP - SATRT %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if arcpy.Exists(src_ncrtpb_rail_stops):
        arcpy.Delete_management(src_ncrtpb_rail_stops, "FeatureClass")

    log_message = "Projecting the area NCRTPB Rail Stops to the CGC Workspace: {}".format(src_ncrtpb_rail_stops)
    logger.info(log_message)

    # Process: Project
    arcpy.Project_management(mwcog_rail_stops, src_ncrtpb_rail_stops,
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['NAD_1983_StatePlane_Maryland_FIPS_1900_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1312333.333333333],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.0],PARAMETER['Standard_Parallel_1',38.3],PARAMETER['Standard_Parallel_2',39.45],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Foot_US',0.3048006096012192]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    if arcpy.Exists(src_ncrtpb_rail_lines):
        arcpy.Delete_management(src_ncrtpb_rail_lines, "FeatureClass")

    log_message = "Projecting the area NCRTPB Rail Lines to the CGC Workspace: {}".format(src_ncrtpb_rail_lines)
    logger.info(log_message)

    # Process: Project (2)
    arcpy.Project_management(mwcog_rail_lines, src_ncrtpb_rail_lines,
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983",
                             "PROJCS['NAD_1983_StatePlane_Maryland_FIPS_1900_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1312333.333333333],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.0],PARAMETER['Standard_Parallel_1',38.3],PARAMETER['Standard_Parallel_2',39.45],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Foot_US',0.3048006096012192]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    if arcpy.Exists(src_ucb_rail_lines):
        arcpy.Delete_management(src_ucb_rail_lines, "FeatureClass")

    log_message = "Projecting the area US Census Rail Lines to the CGC Workspace: {}".format(src_ucb_rail_lines)
    logger.info(log_message)

    # Process: Project (3)
    arcpy.Project_management(ucb_rail_lines, src_ucb_rail_lines,
                             "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")


    log_message = "Merging rail lines from the US Census and the regional authority into {}".format(src_all_rail_lines)
    logger.info(log_message)

    if arcpy.Exists(src_all_rail_lines):
        arcpy.Delete_management(src_all_rail_lines, "FeatureClass")

    # Process: Merge (3)
    arcpy.Merge_management(src_ucb_rail_lines + ";" + src_ncrtpb_rail_lines, src_all_rail_lines, "LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + src_ucb_rail_lines + ",LINEARID,-1,-1;FULLNAME \"FULLNAME\" true true false 100 Text 0 0 ,First,#," + src_ucb_rail_lines + ",FULLNAME,-1,-1; \
    MTFCC \"MTFCC\" true true false 5 Text 0 0 ,First,#," + src_ucb_rail_lines + ",MTFCC,-1,-1;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#," + src_ucb_rail_lines + ",SHAPE_Length,-1,-1," + src_ncrtpb_rail_lines + ",Shape_Length,-1,-1; \
    LINE \"Line\" true true false 15 Text 0 0 ,First,#," + src_ncrtpb_rail_lines + ",LINE,-1,-1;YEAR \"Year Opened\" true true false 8 Double 0 0 ,First,#," + src_ncrtpb_rail_lines + ",YEAR,-1,-1;FROM_ \"From\" true true false 90 Text 0 0 ,First,#," + src_ncrtpb_rail_lines + ",FROM_,-1,-1; \
    TO_ \"To\" true true false 90 Text 0 0 ,First,#," + src_ncrtpb_rail_lines + ",TO_,-1,-1;Display \"Display\" true true false 50 Text 0 0 ,First,#," + src_ncrtpb_rail_lines + ",Display,-1,-1;ANode \"ANode\" true true false 4 Long 0 0 ,First,#," + src_ncrtpb_rail_lines + ",ANode,-1,-1; \
    BNode \"BNode\" true true false 4 Long 0 0 ,First,#," + src_ncrtpb_rail_lines + ",BNode,-1,-1;GlobalID \"GlobalID\" false false false 38 GlobalID 0 0 ,First,#," + src_ncrtpb_rail_lines + ",GlobalID,-1,-1;JUR \"Jurisdiction\" true true false 50 Text 0 0 ,First,#," + src_ncrtpb_rail_lines + ",JUR,-1,-1; \
    State \"State\" true true false 50 Text 0 0 ,First,#," + src_ncrtpb_rail_lines + ",State,-1,-1")

    log_message = "Performing Housekeeping Tasks ..."
    logger.info(log_message)

    log_message = "Preparing the GTFS rail stop extraction and XY plot ..."
    logger.info(log_message)

    if arcpy.Exists(src_gtfs_rail_stops):
        arcpy.DeleteFeatures_management(src_gtfs_rail_stops)
    else:
        # Process: Project (5)
        arcpy.Project_management(gtfs_railTemp, src_gtfs_rail_stops, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                                 "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                                 "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

        arcpy.DeleteFeatures_management(src_gtfs_rail_stops)

    railStopNmList = ["GTFSVirginiaExpressRailStopsWD", "GTFSVirginiaExpressRailStopsWE", "GTFSWMATARailStopsWD", "GTFSWMATARailStopsWE", "GTFSWMATAStreetcarRailStopsWD"]

    railStopTbl = cgctemp_gdb + "\\GTFS_Rail_Stops"
    railStopLyr = "in_memory\\GTFS_Rail_Stops_Layer"

    for rStopNm in railStopNmList:

        rStopTbl = os.path.join(srcdata_gdb, rStopNm)

        log_message = "Geolocating: {}".format(rStopNm)
        logger.info(log_message)

        if arcpy.Exists(railStopTbl):
            arcpy.Delete_management(railStopTbl, "Table")

        # Process: Table to Table
        arcpy.TableToTable_conversion(rStopTbl, cgctemp_gdb, "GTFS_Rail_Stops", "", "stop_id \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",stop_id,-1,-1;stop_code \"stop_code\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",stop_code,-1,-1;stop_name \"stop_name\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",stop_name,-1,-1;stop_desc \"stop_desc\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",stop_desc,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 8 38 ,First,#," + rStopTbl + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 8 38 ,First,#," + rStopTbl + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",zone_id,-1,-1;stop_url \"stop_url\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",stop_url,-1,-1;location_type \"location_type\" true true false 4 Long 0 10 ,First,#," + rStopTbl + ",location_type,-1,-1;parent_station \"parent_station\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",parent_station,-1,-1;stop_timezone \"stop_timezone\" true true false 1073741822 Text 0 0 ,First,#," + rStopTbl + ",stop_timezone,-1,-1", "")

        if arcpy.Exists(railStopLyr):
            arcpy.Delete_management(railStopLyr, "FeatureLayer")

        # Process: Make XY Event Layer (Make XY Event Layer)
        arcpy.MakeXYEventLayer_management(table=railStopTbl, in_x_field="stop_lon", in_y_field="stop_lat", out_layer=railStopLyr, spatial_reference="GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision", in_z_field="")

        if arcpy.Exists(gtfs_railTemp):
            arcpy.Delete_management(gtfs_railTemp, "FeatureClass")

        # Process: Copy Features (Copy Features)
        arcpy.CopyFeatures_management(in_features=railStopLyr, out_feature_class=gtfs_railTemp, config_keyword="", spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None)

        if arcpy.Exists(gtfs_railProj):
            arcpy.Delete_management(gtfs_railProj, "FeatureClass")

        # Process: Project (4)
        arcpy.Project_management(gtfs_railTemp, gtfs_railProj, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                                 "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                                 "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

        # Process: Append
        arcpy.Append_management(gtfs_railProj, src_gtfs_rail_stops, "NO_TEST", "stop_id \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",stop_id,-1,-1;stop_code \"stop_code\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",stop_code,-1,-1;stop_name \"stop_name\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",stop_name,-1,-1;stop_desc \"stop_desc\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",stop_desc,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + gtfs_railProj + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + gtfs_railProj + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",zone_id,-1,-1;stop_url \"stop_url\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",stop_url,-1,-1;location_type \"location_type\" true true false 4 Long 0 0 ,First,#," + gtfs_railProj + ",location_type,-1,-1;parent_station \"parent_station\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",parent_station,-1,-1;stop_timezone \"stop_timezone\" true true false 1073741822 Text 0 0 ,First,#," + gtfs_railProj + ",stop_timezone,-1,-1", "")

    log_message = "Finalized GTFS rail stop extraction and XY plot - Preparing for Rail Stop location calibration"
    logger.info(log_message)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Spatially joining GTFS rail stop point data to {}".format(src_ncrtpb_rail_stops)
    logger.info(log_message)

    if arcpy.Exists(src_all_rail_stops):
        arcpy.Delete_management(src_all_rail_stops, "FeatureClass")

    # Process: Merge
    arcpy.Merge_management(src_ncrtpb_rail_stops + ";" + src_gtfs_rail_stops, src_all_rail_stops, "NAME \"Name\" true true false 80 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",NAME,-1,-1;WEB_URL \"Web URL\" true true false 80 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",WEB_URL,-1,-1;LINE \"Line\" true true false 80 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",LINE,-1,-1;SEQNO \"SEQNO\" true true false 8 Double 0 0 ,First,#," + src_ncrtpb_rail_stops + ",SEQNO,-1,-1;Parking \"Parking Availbility\" true true false 15 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Parking,-1,-1;Network_Node \"Network Node\" true true false 4 Long 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Network_Node,-1,-1;XCoord \"X Coordinate\" true true false 8 Double 0 0 ,First,#," + src_ncrtpb_rail_stops + ",XCoord,-1,-1;YCoord \"Y Coordinate\" true true false 8 Double 0 0 ,First,#," + src_ncrtpb_rail_stops + ",YCoord,-1,-1;State \"State\" true true false 25 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",State,-1,-1;Jurisdiction \"Jurisdiction\" true true false 2 Short 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Jurisdiction,-1,-1;FIPS \"FIPS code\" true true false 5 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",FIPS,-1,-1;Line2 \"2nd Line\" true true false 50 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Line2,-1,-1;Line3 \"3rd Line\" true true false 50 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Line3,-1,-1;Line4 \"4th Line\" true true false 50 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Line4,-1,-1;Year \"Year Opened\" true true false 2 Short 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Year,-1,-1;Station_Number \"Station Number\" true true false 2 Short 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Station_Number,-1,-1;Station_Name \"Station Name\" true true false 60 Text 0 0 ,First,#," + src_ncrtpb_rail_stops + ",Station_Name,-1,-1;stop_id \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_id,-1,-1;stop_code \"stop_code\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_code,-1,-1;stop_name \"stop_name\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_name,-1,-1;stop_desc \"stop_desc\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_desc,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",zone_id,-1,-1;stop_url \"stop_url\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_url,-1,-1;location_type \"location_type\" true true false 4 Long 0 0 ,First,#," + src_gtfs_rail_stops + ",location_type,-1,-1;parent_station \"parent_station\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",parent_station,-1,-1;stop_timezone \"stop_timezone\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_timezone,-1,-1")

    log_message = "Removing extra fields from {}".format(src_all_rail_stops)
    logger.info(log_message)

    # Process: Delete Field
    arcpy.DeleteField_management(src_all_rail_stops, "stop_code;stop_desc;stop_url;location_type;parent_station")

    log_message = "Adding/Calculating the location_type field ..."
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(src_all_rail_stops, "location_type", "TEXT", "", "", "", "location_type", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field -- Bus Transfers to Rail Staions are coded as Location_Type == "transfer" and RouteModeCD == "1"  -- Rail Transfers at Rail Staions are coded as Location_Type == "transfer" and RouteModeCD == "0"
    arcpy.CalculateField_management(src_all_rail_stops, "location_type", "markTransferPnts( !NAME!, !LINE! )", "PYTHON_9.3", "def markTransferPnts(name, line):\\n  locType = \"\"\\n  lineList = 0\\n  if name == None:\\n    locType = \"transfer\"\\n  elif line != None:\\n    lineList = line.find(\",\")\\n    if lineList != -1:\\n      locType = \"transfer\"\\n  else:\\n    pass\\n  return locType")

    log_message = "Adding/Calculating the RouteModeCD field ..."
    logger.info(log_message)

    # Process: Add Field (2)
    arcpy.AddField_management(src_all_rail_stops, "RouteModeCD", "TEXT", "", "", "3", "RouteModeCD", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(src_all_rail_stops, "RouteModeCD", "markRteModeCD( !NAME! )", "PYTHON_9.3", "def markRteModeCD(name):\\n  retCD = \"1\"\\n  if name != None:\\n    retCD = \"0\"\\n  return retCD")

    log_message = "Calculating the merged stop name ..."
    logger.info(log_message)

    # Process: Calculate Field (3)
    arcpy.CalculateField_management(src_all_rail_stops, "NAME", "mergeNameDef( !NAME! , !stop_name! )", "PYTHON_9.3", "def mergeNameDef(primeNM, gtfsNM):\\n  retNM = \"\"\\n  if primeNM == None:\\n    retNM = gtfsNM\\n  else:\\n    retNM = primeNM\\n  return retNM\\n")

    log_message = "Clipping Rail Points by the Study Area ..."
    logger.info(log_message)

    if arcpy.Exists(rail_taz_stops):
        arcpy.Delete_management(rail_taz_stops, "FeatureClass")

    # Process: Clip
    arcpy.Clip_analysis(in_features=src_all_rail_stops, clip_features=taz_studyarea_proj, out_feature_class=rail_taz_stops, cluster_tolerance="")

    log_message = "Spatially joining GTFS bus-to-rail transfer times to {}".format(rail_taz_stops)
    logger.info(log_message)

    if arcpy.Exists(rail_taz_transferpnt):
        arcpy.Delete_management(rail_taz_transferpnt, "FeatureClass")

    # Process: Spatial Join
    arcpy.SpatialJoin_analysis(rail_taz_stops, bus_taz_stops, rail_taz_transferpnt, "JOIN_ONE_TO_ONE", "KEEP_ALL", "NAME \"Name\" true true false 80 Text 0 0 ,First,#," + rail_taz_stops + ",NAME,-1,-1; \
    WEB_URL \"Web URL\" true true false 80 Text 0 0 ,First,#," + rail_taz_stops + ",WEB_URL,-1,-1;LINE \"Line\" true true false 80 Text 0 0 ,First,#," + rail_taz_stops + ",LINE,-1,-1; \
    SEQNO \"SEQNO\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops + ",SEQNO,-1,-1;Parking \"Parking Availbility\" true true false 15 Text 0 0 ,First,#," + rail_taz_stops + ",Parking,-1,-1; \
    Network_Node \"Network Node\" true true false 4 Long 0 0 ,First,#," + rail_taz_stops + ",Network_Node,-1,-1;XCoord \"X Coordinate\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops + ",XCoord,-1,-1; \
    YCoord \"Y Coordinate\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops + ",YCoord,-1,-1;State \"State\" true true false 25 Text 0 0 ,First,#," + rail_taz_stops + ",State,-1,-1; \
    Jurisdiction \"Jurisdiction\" true true false 2 Short 0 0 ,First,#," + rail_taz_stops + ",Jurisdiction,-1,-1;FIPS \"FIPS code\" true true false 5 Text 0 0 ,First,#," + rail_taz_stops + ",FIPS,-1,-1; \
    Line2 \"2nd Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_stops + ",Line2,-1,-1;Line3 \"3rd Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_stops + ",Line3,-1,-1; \
    Line4 \"4th Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_stops + ",Line4,-1,-1;Year \"Year Opened\" true true false 2 Short 0 0 ,First,#," + rail_taz_stops + ",Year,-1,-1; \
    Station_Number \"Station Number\" true true false 2 Short 0 0 ,First,#," + rail_taz_stops + ",Station_Number,-1,-1;Station_Name \"Station Name\" true true false 60 Text 0 0 ,First,#," + rail_taz_stops + ",Station_Name,-1,-1; \
    RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + rail_taz_stops + ",RouteModeCD,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_taz_stops + ",stop_id,-1,-1; \
    Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_EarlyAM_WaitTime_WD,-1,-1; \
    Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_MidDay_WaitTime_WD,-1,-1; \
    Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_PeakPM_WaitTime_WD,-1,-1;Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_LatePM_WaitTime_WD,-1,-1; \
    Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_EarlyAM_WaitTime_WE,-1,-1; \
    Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_MidDay_WaitTime_WE,-1,-1; \
    Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_PeakPM_WaitTime_WE,-1,-1;Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",Avg_LatePM_WaitTime_WE,-1,-1; \
    agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_taz_stops + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_taz_stops + ",route_id_all,-1,-1; \
    direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_taz_stops + ",direction_id_all,-1,-1;stop_name \"stop_name\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_stops + ",stop_name,-1,-1; \
    location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_stops + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + bus_taz_stops + ",wheelchair_boarding,-1,-1; \
    stop_code \"stop_code\" true true false 4 Long 0 0 ,First,#," + bus_taz_stops + ",stop_code,-1,-1;stop_desc \"stop_desc\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_stops + ",stop_desc,-1,-1; \
    stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_taz_stops + ",stop_lon,-1,-1; \
    zone_id \"zone_id\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_stops + ",zone_id,-1,-1;stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_taz_stops + ",stop_url,-1,-1; \
    BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID1,-1,-1;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID2,-1,-1; \
    BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID3,-1,-1;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID4,-1,-1; \
    BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID5,-1,-1;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID6,-1,-1; \
    BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID7,-1,-1;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID8,-1,-1; \
    BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID9,-1,-1;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + bus_taz_stops + ",BusRouteID10,-1,-1", "INTERSECT", "0.005 Miles", "")

    log_message = "Performing GTFS calibration on Bus-to-Rail Transfer Wait Times in {}".format(rail_taz_transferpnt)
    logger.info(log_message)

    fc_list = [f.name for f in arcpy.ListFields(rail_taz_transferpnt)]
    field_names = ["Avg_AllDay_WaitTime_WD", "Avg_EarlyAM_WaitTime_WD", "Avg_PeakAM_WaitTime_WD", "Avg_MidDay_WaitTime_WD", "Avg_PeakPM_WaitTime_WD", "Avg_LatePM_WaitTime_WD",
                   "Avg_AllDay_WaitTime_WE", "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE", "Avg_MidDay_WaitTime_WE", "Avg_PeakPM_WaitTime_WE", "Avg_LatePM_WaitTime_WE"]
    for field_name in field_names:
        log_message = "Applying GTFS transfer time to {}".format(field_name)
        logger.info(log_message)
        if field_name in fc_list:
            arcpy.CalculateField_management(rail_taz_transferpnt, field_name,
                                            "runGTFSUpdate( !stop_id! , !" + field_name + "! )", "PYTHON_9.3",
                                            "def runGTFSUpdate(stopID2, currVal):\\n  retVal = 0.0\\n  if stopID2 != None:\\n    retVal = currVal/3\\n  return retVal")

    log_message = "Isolating non-transfer-to-rail Bus Stops... "
    logger.info(log_message)

    if arcpy.Exists(transit_taz_pointdiff):
        arcpy.Delete_management(transit_taz_pointdiff, "FeatureClass")

    # Process: Symmetrical Difference
    arcpy.SymDiff_analysis(bus_taz_stops, rail_taz_transferpnt, transit_taz_pointdiff, "ALL", "0.005 Miles")

    log_message = "Removing unused fields... "
    logger.info(log_message)

    # Process: Delete Field (2)
    arcpy.DeleteField_management(transit_taz_pointdiff, "FID_Bus_TAZ_StopPoints;Join_Count;TARGET_FID;route_short_name_all;route_long_name_all;trip_headsign_all;stop_code;stop_desc;parent_station;stop_timezone;stop_id_txt;FID_Rail_TAZ_TransferPoints;Join_Count_1;TARGET_FID_1;NAME;WDB_URL;LINE;SEQNO;Parking;Network_Node;XCoord;YCoord;State;Jurisdiction;FIPS;Line2;Line3;Line4;Year;Station_Number;Station_Name;RouteModeCD;stop_id_1;Avg_AllDay_WaitTime_WD_1;Avg_EarlyAM_WaitTime_WD_1;Avg_PeakAM_WaitTime_WD_1;Avg_MidDay_WaitTime_WD_1;Avg_PeakPM_WaitTime_WD_1;Avg_LatePM_WaitTime_WD_1;Avg_AllDay_WaitTime_WE_1;Avg_EarlyAM_WaitTime_WE_1;Avg_PeakAM_WaitTime_WE_1;Avg_MidDay_WaitTime_WE_1;Avg_PeakPM_WaitTime_WE_1;Avg_LatePM_WaitTime_WE_1;agency_1;route_id_all_1;direction_id_all_1;stop_name_1;location_type_1;wheelchair_boarding_1;stop_code_1;stop_desc_1;stop_lat_1;stop_lon_1;zone_id_1;stop_url_1;BusRouteID1_1;BusRouteID2_1;BusRouteID3_1;BusRouteID4_1;BusRouteID5_1;BusRouteID6_1;BusRouteID7_1;BusRouteID8_1;BusRouteID9_1;BusRouteID10_1;stop_timezone_1;stop_id_12;stop_name_12")

    log_message = "Merging transfer and non-transfer results into {}".format(transit_transfer_stations)
    logger.info(log_message)

    if arcpy.Exists(transit_transfer_stations):
        arcpy.Delete_management(transit_transfer_stations, "FeatureClass")

    # Process: Merge (2)
    arcpy.Merge_management(rail_taz_transferpnt + ";" + transit_taz_pointdiff, transit_transfer_stations, "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + rail_taz_transferpnt + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + rail_taz_transferpnt + ",TARGET_FID,-1,-1; \
    NAME \"Name\" true true false 80 Text 0 0 ,First,#," + rail_taz_transferpnt + ",NAME,-1,-1;WEB_URL \"Web URL\" true true false 80 Text 0 0 ,First,#," + rail_taz_transferpnt + ",WEB_URL,-1,-1;LINE \"Line\" true true false 80 Text 0 0 ,First,#," + rail_taz_transferpnt + ",LINE,-1,-1; \
    SEQNO \"SEQNO\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",SEQNO,-1,-1;Parking \"Parking Availbility\" true true false 15 Text 0 0 ,First,#," + rail_taz_transferpnt + ",Parking,-1,-1;Network_Node \"Network Node\" true true false 4 Long 0 0 ,First,#," + rail_taz_transferpnt + ",Network_Node,-1,-1; \
    XCoord \"X Coordinate\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",XCoord,-1,-1;YCoord \"Y Coordinate\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",YCoord,-1,-1;State \"State\" true true false 25 Text 0 0 ,First,#," + rail_taz_transferpnt + ",State,-1,-1; \
    Jurisdiction \"Jurisdiction\" true true false 2 Short 0 0 ,First,#," + rail_taz_transferpnt + ",Jurisdiction,-1,-1;FIPS \"FIPS code\" true true false 5 Text 0 0 ,First,#," + rail_taz_transferpnt + ",FIPS,-1,-1;Line2 \"2nd Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_transferpnt + ",Line2,-1,-1; \
    Line3 \"3rd Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_transferpnt + ",Line3,-1,-1;Line4 \"4th Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_transferpnt + ",Line4,-1,-1;Year \"Year Opened\" true true false 2 Short 0 0 ,First,#," + rail_taz_transferpnt + ",Year,-1,-1; \
    Station_Number \"Station Number\" true true false 2 Short 0 0 ,First,#," + rail_taz_transferpnt + ",Station_Number,-1,-1;Station_Name \"Station Name\" true true false 60 Text 0 0 ,First,#," + rail_taz_transferpnt + ",Station_Name,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + rail_taz_transferpnt + ",RouteModeCD,-1,-1; \
    stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + rail_taz_transferpnt + ",stop_id,-1,-1," + transit_taz_pointdiff + ",stop_id,-1,-1; \
    Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_AllDay_WaitTime_WD,-1,-1," + transit_taz_pointdiff + ",Avg_AllDay_WaitTime_WD,-1,-1; \
    Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_EarlyAM_WaitTime_WD,-1,-1," + transit_taz_pointdiff + ",Avg_EarlyAM_WaitTime_WD,-1,-1; \
    Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_PeakAM_WaitTime_WD,-1,-1," + transit_taz_pointdiff + ",Avg_PeakAM_WaitTime_WD,-1,-1; \
    Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_MidDay_WaitTime_WD,-1,-1," + transit_taz_pointdiff + ",Avg_MidDay_WaitTime_WD,-1,-1; \
    Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_PeakPM_WaitTime_WD,-1,-1," + transit_taz_pointdiff + ",Avg_PeakPM_WaitTime_WD,-1,-1; \
    Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_LatePM_WaitTime_WD,-1,-1," + transit_taz_pointdiff + ",Avg_LatePM_WaitTime_WD,-1,-1; \
    Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_AllDay_WaitTime_WE,-1,-1," + transit_taz_pointdiff + ",Avg_AllDay_WaitTime_WE,-1,-1; \
    Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_EarlyAM_WaitTime_WE,-1,-1," + transit_taz_pointdiff + ",Avg_EarlyAM_WaitTime_WE,-1,-1; \
    Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_PeakAM_WaitTime_WE,-1,-1," + transit_taz_pointdiff + ",Avg_PeakAM_WaitTime_WE,-1,-1; \
    Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_MidDay_WaitTime_WE,-1,-1," + transit_taz_pointdiff + ",Avg_MidDay_WaitTime_WE,-1,-1; \
    Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_PeakPM_WaitTime_WE,-1,-1," + transit_taz_pointdiff + ",Avg_PeakPM_WaitTime_WE,-1,-1; \
    Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",Avg_LatePM_WaitTime_WE,-1,-1," + transit_taz_pointdiff + ",Avg_LatePM_WaitTime_WE,-1,-1; \
    agency \"agency\" true true false 8000 Text 0 0 ,First,#," + rail_taz_transferpnt + ",agency,-1,-1," + transit_taz_pointdiff + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + rail_taz_transferpnt + ",route_id_all,-1,-1," + transit_taz_pointdiff + ",route_id_all,-1,-1; \
    direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + rail_taz_transferpnt + ",direction_id_all,-1,-1," + transit_taz_pointdiff + ",direction_id_all,-1,-1;stop_name \"stop_name\" true true false 2147483647 Text 0 0 ,First,#," + rail_taz_transferpnt + ",stop_name,-1,-1," + transit_taz_pointdiff + ",stop_name,-1,-1; \
    location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + rail_taz_transferpnt + ",location_type,-1,-1," + transit_taz_pointdiff + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + rail_taz_transferpnt + ",wheelchair_boarding,-1,-1," + transit_taz_pointdiff + ",wheelchair_boarding,-1,-1; \
    stop_code \"stop_code\" true true false 4 Long 0 0 ,First,#," + rail_taz_transferpnt + ",stop_code,-1,-1;stop_desc \"stop_desc\" true true false 2147483647 Text 0 0 ,First,#," + rail_taz_transferpnt + ",stop_desc,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",stop_lat,-1,-1," + transit_taz_pointdiff + ",stop_lat,-1,-1; \
    stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + rail_taz_transferpnt + ",stop_lon,-1,-1," + transit_taz_pointdiff + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 2147483647 Text 0 0 ,First,#," + rail_taz_transferpnt + ",zone_id,-1,-1," + transit_taz_pointdiff + ",zone_id,-1,-1; \
    stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + rail_taz_transferpnt + ",stop_url,-1,-1," + transit_taz_pointdiff + ",stop_url,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID1,-1,-1," + transit_taz_pointdiff + ",BusRouteID1,-1,-1; \
    BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID2,-1,-1," + transit_taz_pointdiff + ",BusRouteID2,-1,-1;BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID3,-1,-1," + transit_taz_pointdiff + ",BusRouteID3,-1,-1; \
    BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID4,-1,-1," + transit_taz_pointdiff + ",BusRouteID4,-1,-1;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID5,-1,-1," + transit_taz_pointdiff + ",BusRouteID5,-1,-1; \
    BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID6,-1,-1," + transit_taz_pointdiff + ",BusRouteID6,-1,-1;BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID7,-1,-1," + transit_taz_pointdiff + ",BusRouteID7,-1,-1; \
    BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID8,-1,-1," + transit_taz_pointdiff + ",BusRouteID8,-1,-1;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID9,-1,-1," + transit_taz_pointdiff + ",BusRouteID9,-1,-1; \
    BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + rail_taz_transferpnt + ",BusRouteID10,-1,-1," + transit_taz_pointdiff + ",BusRouteID10,-1,-1")

    log_message = "Updating Route Mode Code -- '2': Bus Stop Only, '1': Bus-to-Rail Transfer Stop, '0': Rail Sation Only"
    logger.info(log_message)

    # Process: Calculate Field (5)
    arcpy.CalculateField_management(transit_transfer_stations, "RouteModeCD", "setEmptyModeCD( !RouteModeCD! )", "PYTHON_9.3", "def setEmptyModeCD(mode):\\n  retCD = \"\"\\n  if mode == None:\\n    retCD = \"2\"\\n  else:\\n    retCD = mode\\n  return retCD")

    log_message = "Reformatting all NULL Transfer Wait Times in {}".format(transit_transfer_stations)
    logger.info(log_message)

    fc_list2 = [f.name for f in arcpy.ListFields(transit_transfer_stations)]
    field_names2 = ["Avg_AllDay_WaitTime_WD", "Avg_EarlyAM_WaitTime_WD", "Avg_PeakAM_WaitTime_WD",
                   "Avg_MidDay_WaitTime_WD", "Avg_PeakPM_WaitTime_WD", "Avg_LatePM_WaitTime_WD",
                   "Avg_AllDay_WaitTime_WE", "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE",
                   "Avg_MidDay_WaitTime_WE", "Avg_PeakPM_WaitTime_WE", "Avg_LatePM_WaitTime_WE"]
    for field_name in field_names2:
        log_message = "Zeroing Null GTFS transfer time in {}".format(field_name)
        logger.info(log_message)
        if field_name in fc_list2:
            arcpy.CalculateField_management(transit_transfer_stations, field_name,
                                            "runGTFSZero( !" + field_name + "! )", "PYTHON_9.3",
                                            "def runGTFSZero(currVal):\\n  retVal = currVal\\n  if currVal == None:\\n    retVal = 0.0\\n  return retVal")

    ### BREAKPOINT %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Extracting Rail Staions in the study area: {}".format(rail_taz_stops_temp)
    logger.info(log_message)

    if arcpy.Exists(rail_taz_stops_temp):
        arcpy.Delete_management(rail_taz_stops_temp, "FeatureClass")

    # Process: Feature Class to Feature Class
    arcpy.FeatureClassToFeatureClass_conversion(transit_transfer_stations, wkspcdata_gdb, "Rail_TAZ_Stops_Temp", "RouteModeCD = '0'", "NAME \"Name\" true true false 80 Text 0 0 ,First,#," + transit_transfer_stations + ",NAME,-1,-1;WEB_URL \"Web URL\" true true false 80 Text 0 0 ,First,#," + transit_transfer_stations + ",WEB_URL,-1,-1; \
    LINE \"Line\" true true false 80 Text 0 0 ,First,#," + transit_transfer_stations + ",LINE,-1,-1;SEQNO \"SEQNO\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",SEQNO,-1,-1;Parking \"Parking Availbility\" true true false 15 Text 0 0 ,First,#," + transit_transfer_stations + ",Parking,-1,-1; \
    Network_Node \"Network Node\" true true false 4 Long 0 0 ,First,#," + transit_transfer_stations + ",Network_Node,-1,-1;XCoord \"X Coordinate\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",XCoord,-1,-1;YCoord \"Y Coordinate\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",YCoord,-1,-1; \
    State \"State\" true true false 25 Text 0 0 ,First,#," + transit_transfer_stations + ",State,-1,-1;Jurisdiction \"Jurisdiction\" true true false 2 Short 0 0 ,First,#," + transit_transfer_stations + ",Jurisdiction,-1,-1;FIPS \"FIPS code\" true true false 5 Text 0 0 ,First,#," + transit_transfer_stations + ",FIPS,-1,-1; \
    Line2 \"2nd Line\" true true false 50 Text 0 0 ,First,#," + transit_transfer_stations + ",Line2,-1,-1;Line3 \"3rd Line\" true true false 50 Text 0 0 ,First,#," + transit_transfer_stations + ",Line3,-1,-1;Line4 \"4th Line\" true true false 50 Text 0 0 ,First,#," + transit_transfer_stations + ",Line4,-1,-1; \
    Year \"Year Opened\" true true false 2 Short 0 0 ,First,#," + transit_transfer_stations + ",Year,-1,-1;Station_Number \"Station Number\" true true false 2 Short 0 0 ,First,#," + transit_transfer_stations + ",Station_Number,-1,-1;Station_Name \"Station Name\" true true false 60 Text 0 0 ,First,#," + transit_transfer_stations + ",Station_Name,-1,-1; \
    RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + transit_transfer_stations + ",RouteModeCD,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + transit_transfer_stations + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_AllDay_WaitTime_WD,-1,-1; \
    Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_PeakAM_WaitTime_WD,-1,-1; \
    Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_PeakPM_WaitTime_WD,-1,-1; \
    Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_AllDay_WaitTime_WE,-1,-1; \
    Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_PeakAM_WaitTime_WE,-1,-1; \
    Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_PeakPM_WaitTime_WE,-1,-1; \
    Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + transit_transfer_stations + ",Avg_LatePM_WaitTime_WE,-1,-1", "")

    log_message = "Performing Housekeeping Tasks ..."
    logger.info(log_message)

    if arcpy.Exists(gtfs_railProj):
        arcpy.Delete_management(gtfs_railProj, "FeatureClass")

    if arcpy.Exists(transit_taz_pointdiff):
        arcpy.Delete_management(transit_taz_pointdiff, "FeatureClass")

    if arcpy.Exists(src_all_rail_stops):
        arcpy.Delete_management(src_all_rail_stops, "FeatureClass")

    if arcpy.Exists(rail_taz_stops):
        arcpy.Delete_management(rail_taz_stops, "FeatureClass")

    if arcpy.Exists(rail_taz_transferpnt):
        arcpy.Delete_management(rail_taz_transferpnt, "FeatureClass")

    log_message = "Geolocating all stop identifiers in {}".format(rail_taz_stations)
    logger.info(log_message)

    if arcpy.Exists(rail_taz_stations):
        arcpy.Delete_management(rail_taz_stations, "FeatureClass")

    # Process: Spatial Join
    arcpy.SpatialJoin_analysis(rail_taz_stops_temp, src_gtfs_rail_stops, rail_taz_stations, "JOIN_ONE_TO_ONE", "KEEP_ALL", "Join_Count \"Join_Count\" true true false 4 Long 0 0 ,First,#," + rail_taz_stops_temp + ",Join_Count,-1,-1;TARGET_FID \"TARGET_FID\" true true false 4 Long 0 0 ,First,#," + rail_taz_stops_temp + ",TARGET_FID,-1,-1;NAME \"Name\" true true false 80 Text 0 0 ,First,#," + rail_taz_stops_temp + ",NAME,-1,-1;WEB_URL \"Web URL\" true true false 80 Text 0 0 ,First,#," + rail_taz_stops_temp + ",WEB_URL,-1,-1;LINE \"Line\" true true false 80 Text 0 0 ,First,#," + rail_taz_stops_temp + ",LINE,-1,-1;SEQNO \"SEQNO\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",SEQNO,-1,-1;Parking \"Parking Availbility\" true true false 15 Text 0 0 ,First,#," + rail_taz_stops_temp + ",Parking,-1,-1;Network_Node \"Network Node\" true true false 4 Long 0 0 ,First,#," + rail_taz_stops_temp + ",Network_Node,-1,-1;XCoord \"X Coordinate\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",XCoord,-1,-1;YCoord \"Y Coordinate\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",YCoord,-1,-1;State \"State\" true true false 25 Text 0 0 ,First,#," + rail_taz_stops_temp + ",State,-1,-1;Jurisdiction \"Jurisdiction\" true true false 2 Short 0 0 ,First,#," + rail_taz_stops_temp + ",Jurisdiction,-1,-1;FIPS \"FIPS code\" true true false 5 Text 0 0 ,First,#," + rail_taz_stops_temp + ",FIPS,-1,-1;Line2 \"2nd Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_stops_temp + ",Line2,-1,-1;Line3 \"3rd Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_stops_temp + ",Line3,-1,-1;Line4 \"4th Line\" true true false 50 Text 0 0 ,First,#," + rail_taz_stops_temp + ",Line4,-1,-1;Year \"Year Opened\" true true false 2 Short 0 0 ,First,#," + rail_taz_stops_temp + ",Year,-1,-1;Station_Number \"Station Number\" true true false 2 Short 0 0 ,First,#," + rail_taz_stops_temp + ",Station_Number,-1,-1;Station_Name \"Station Name\" true true false 60 Text 0 0 ,First,#," + rail_taz_stops_temp + ",Station_Name,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + rail_taz_stops_temp + ",RouteModeCD,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + rail_taz_stops_temp + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_PeakPM_WaitTime_WD,-1,-1;Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_PeakPM_WaitTime_WE,-1,-1;Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + rail_taz_stops_temp + ",Avg_LatePM_WaitTime_WE,-1,-1;stop_id_12 \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + src_gtfs_rail_stops + ",stop_id,-1,-1", "CLOSEST", "0.1 Miles", "")

    # Process: Calculate Field
    arcpy.CalculateField_management(rail_taz_stations, "stop_id", "fillStopID( !stop_id_12! )", "PYTHON_9.3", "def fillStopID(joinStop):\\n  retStop = \"\"\\n  if joinStop == None:\\n    pass\\n  else:\\n    retStop = joinStop\\n  return retStop")

    # Process: Delete Field (2)
    arcpy.DeleteField_management(rail_taz_stations, "stop_id_12")

    log_message = "Setting the location type for each Rail Stop"
    logger.info(log_message)

    # Process: Add Field
    arcpy.AddField_management(rail_taz_stations, "location_type", "TEXT", "", "", "", "location_type", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(rail_taz_stations, "location_type", "setLocType( !LINE! )", "PYTHON_9.3", "def setLocType(line):\\n  retType = None\\n  typeNdx = line.find(\",\")\\n  if typeNdx != -1:\\n    retType = \"transfer\"\\n  return retType\\n  \\n  ")

    log_message = "Preparing GTFS Departure/Arrival times tables for rail-to-rail transfer wait times calibration"
    logger.info(log_message)

    railTimesNmList = ["GTFSVirginiaExpressRailStopTimesWD", "GTFSVirginiaExpressRailStopTimesWE", "GTFSWMATARailStopTimesWD", "GTFSWMATAStreetcarRailStopTimesWD", "GTFSWMATARailStopTimesWE"]
    railString, railDayChar = None, None
    zCount = 0
    railTimesTbl = wkspcdata_gdb + "\\GTFS_Rail_Times"
    railTimesWD = wkspcdata_gdb + "\\GTFS_Rail_Times_WD"
    railTimesWDTemp = wkspcdata_gdb + "\\GTFS_Rail_Times_WD_Temp"
    railTimesWDSort = wkspcdata_gdb + "\\GTFS_Rail_Times_WD_Sort"
    railTimesWE = wkspcdata_gdb + "\\GTFS_Rail_Times_WE"
    railTimesWETemp = wkspcdata_gdb + "\\GTFS_Rail_Times_WE_Temp"
    railTimesWESort = wkspcdata_gdb + "\\GTFS_Rail_Times_WE_Sort"
    railStopList = wkspcdata_gdb + "\\GTFS_Rail_StopList" ## src_gtfs_rail_stops, where RouteModeCD == '0'

    for rTimeNm in railTimesNmList:

        rTimesTbl = os.path.join(srcdata_gdb, rTimeNm)

        log_message = "Importing: {}".format(rTimeNm)
        logger.info(log_message)
        zCount += 1
        railString = str(rTimeNm)
        railDayChar = railString[-1]

        if arcpy.Exists(railTimesTbl):
            arcpy.Delete_management(railTimesTbl, "Table")

        # Process: Table to Table
        arcpy.TableToTable_conversion(rTimesTbl, wkspcdata_gdb, "GTFS_Rail_Times", "", "stop_id \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + rTimesTbl + ",stop_id,-1,-1;arrival_time \"arrival_time\" true true false 1073741822 Text 0 0 ,First,#," + rTimesTbl + ",arrival_time,-1,-1;departure_time \"departure_time\" true true false 1073741822 Text 0 0 ,First,#," + rTimesTbl + ",departure_time,-1,-1;trip_id \"trip_id\" true true false 1073741822 Text 0 0 ,First,#," + rTimesTbl + ",trip_id,-1,-1", "")

        ## Use query cursors to sort these times into 1 average transfer wait time per day type, day part, and rail station.
        if railDayChar == "D":
            log_message = "Collecting Arrival/Departure Times on Weekdays"
            logger.info(log_message)

            if zCount == 1:
                log_message = "Recreating GTFS Stop Time Template for Weekdays"
                logger.info(log_message)

                if arcpy.Exists(railTimesWD):
                    arcpy.Delete_management(railTimesWD, "Table")

                # Process: Copy
                arcpy.Copy_management(railTimesTbl, railTimesWD, "")

            else:

                # Process: Append
                arcpy.Append_management(railTimesTbl, railTimesWD, "NO_TEST", "stop_id \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",stop_id,-1,-1;arrival_time \"arrival_time\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",arrival_time,-1,-1;departure_time \"departure_time\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",departure_time,-1,-1;trip_id \"trip_id\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",trip_id,-1,-1", "")

        elif railDayChar == "E":
            log_message = "Collecting Arrival/Departure Times on Weekends"
            logger.info(log_message)

            if zCount == 2:
                log_message = "Recreating GTFS Stop Time Template for Weekends"
                logger.info(log_message)

                if arcpy.Exists(railTimesWE):
                    arcpy.Delete_management(railTimesWE, "Table")

                # Process: Copy
                arcpy.Copy_management(railTimesTbl, railTimesWE, "")

            else:
                # Process: Append
                arcpy.Append_management(railTimesTbl, railTimesWE, "NO_TEST", "stop_id \"stop_id\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",stop_id,-1,-1;arrival_time \"arrival_time\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",arrival_time,-1,-1;departure_time \"departure_time\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",departure_time,-1,-1;trip_id \"trip_id\" true true false 1073741822 Text 0 0 ,First,#," + railTimesTbl + ",trip_id,-1,-1", "")

        else:
            log_message = "Adding GTFS Stop Times for Additional Rail Operators (>2)"
            logger.info(log_message)

    log_message = "Reformatting Arrival/Departure Times in {} and {}".format(railTimesWD, railTimesWE)
    logger.info(log_message)

    railTimesList = [railTimesWD, railTimesWE]
    wrStationTimes = None
    dayType = None
    stCount = 0
    iCount = 0

    for rt in railTimesList:
        railString = str(rt)
        railDayChar = railString[-1]

        fc_list3 = [f.name for f in arcpy.ListFields(rt)]
        field_names3 = ["arrival_time", "departure_time"]
        for field_name in field_names3:
            log_message = "Applying HH:MM:SS formatiing to {} in {}".format(field_name, rt)
            logger.info(log_message)
            if field_name in fc_list3:
                # Process: Calculate Field (3)
                arcpy.CalculateField_management(rt, field_name, "formatTime( !" + field_name + "! )", "PYTHON_9.3",
                                                "def formatTime(rtime):\\n  retTime = \"\"  \\n  rNdx = rtime.find(\"/\")\\n  if rNdx == -1:\\n    retTime = rtime\\n  else:\\n    retTime = rtime.replace(\"/\", \":\")\\n  return retTime")

        dataCount = arcpy.GetCount_management(rt)
        dCount = int(dataCount[0])

        edit3 = arcpy.da.Editor(wkspcdata_gdb)

        log_message = "Filtering {}".format(rt)
        logger.info(log_message)

        tOID = None
        tStopID = None
        tArrival = None
        tDeparture = None
        x = 0
        xTimeRecNDX = arcpy.da.UpdateCursor(rt, ["OBJECTID", "stop_id", "arrival_time", "departure_time"], None, None, "False", (None, None))
        for xRow in xTimeRecNDX:
            tOID, tStopID, tArrival, tDeparture = xRow[0], xRow[1], xRow[2], xRow[3]
            if tArrival == None or tDeparture == None:
                x += 1
                xTimeRecNDX.deleteRow()
            else:
                pass

        del xRow
        del xTimeRecNDX

        log_message = "Cleared {} null records of {} in {}".format(str(x), dCount, rt)
        logger.info(log_message)

        ## Breakpoint %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        log_message = "Adding the Minutes field to {}".format(rt)
        logger.info(log_message)

        fc_list = [f.name for f in arcpy.ListFields(rt)]
        field_names = ["DayMinutes"]
        for field_name in field_names:
            if field_name not in fc_list:
                arcpy.AddField_management(rt, field_name, "DOUBLE")

        timesCount = arcpy.GetCount_management(rt)
        tCount = int(timesCount[0])

        # Process: Calculate Field (4)
        arcpy.CalculateField_management(rt, "DayMinutes", "convertToMinutes( !arrival_time! )", "PYTHON_9.3",
                                        "def convertToMinutes(atime):\\n  aNdx = 0\\n  retNbr = 0.0\\n  hrmins = 0.0\\n  mins = 0.0\\n  timeStr = str(atime)\\n  aNdx = timeStr.find(\":\")\\n  if aNdx != -1:\\n    nbrList = timeStr.split(\":\")\\n    hrmins = float(nbrList[0]) * 60\\n    mins = float(nbrList[1])\\n    retNbr = hrmins + mins\\n  return retNbr\\n  ")

        log_message = "Filtering {}".format(rt)
        logger.info(log_message)

        rOID = None
        rStopID = None
        rArrival = None
        rDeparture = None
        rTrip = None
        rTripNbr = 0
        dMinutes = 0.0
        x = 0
        xRecNDX = arcpy.da.UpdateCursor(rt, ["OBJECTID", "stop_id", "arrival_time", "departure_time", "trip_id", "DayMinutes"], None, None, "False", (None, None))
        for xRow in xRecNDX:
            rOID, rStopID, rArrival, rDeparture, rTrip, dMinutes = xRow[0], xRow[1], xRow[2], xRow[3], xRow[4], xRow[5]
            rTripNbr = rTrip.find("-")
            if rTripNbr == -1:
                pass
            else:
                x += 1
                xRecNDX.deleteRow()
        del xRow
        del xRecNDX

        if iCount < 2:
            log_message = "Cleared {} records with defective formatting in Stop ID".format(str(x))
            logger.info(log_message)

            if railDayChar == "D":

                dayType = "Weekdays"

                log_message = "Generating the Weekday GTFS Rail Times template ..."
                logger.info(log_message)

                if arcpy.Exists(railTimesWDTemp):
                    arcpy.Delete_management(railTimesWDTemp, "Table")

                # Process: Table to Table (2)
                arcpy.TableToTable_conversion(rt, wkspcdata_gdb, "GTFS_Rail_Times_WD_Temp", "stop_id IS NULL", "stop_id \"stop_id\" true true false 64 Text 0 0 ,First,#," + rt + ",stop_id,-1,-1;arrival_time \"arrival_time\" true true false 16 Text 0 0 ,First,#," + rt + ",arrival_time,-1,-1;departure_time \"departure_time\" true true false 16 Text 0 0 ,First,#," + rt + ",departure_time,-1,-1;trip_id \"trip_id\" true true false 32 Text 0 0 ,First,#," + rt + ",trip_id,-1,-1;DayMinutes \"DayMinutes\" true true false 8 Double 0 0 ,First,#," + rt + ",DayMinutes,-1,-1", "")

                log_message = "Beginning edit session 2 in {}".format(wkspcdata_gdb)
                logger.info(log_message)
                edit3.startEditing()

                # Cursor Search and Insert
                log_message = "Starting edit operations ..."
                logger.info(log_message)
                edit3.startOperation()

                wrStationTimes = arcpy.da.InsertCursor(railTimesWDTemp, ["OBJECTID", "stop_id", "arrival_time", "departure_time", "trip_id", "DayMinutes"])

            elif railDayChar == "E":

                dayType = "Weekends"

                log_message = "Generating the Weekend GTFS Rail Times template ..."
                logger.info(log_message)

                if arcpy.Exists(railTimesWETemp):
                    arcpy.Delete_management(railTimesWETemp, "Table")

                # Process: Table to Table (2)
                arcpy.TableToTable_conversion(rt, wkspcdata_gdb, "GTFS_Rail_Times_WE_Temp", "stop_id IS NULL", "stop_id \"stop_id\" true true false 64 Text 0 0 ,First,#," + rt + ",stop_id,-1,-1;arrival_time \"arrival_time\" true true false 16 Text 0 0 ,First,#," + rt + ",arrival_time,-1,-1;departure_time \"departure_time\" true true false 16 Text 0 0 ,First,#," + rt + ",departure_time,-1,-1;trip_id \"trip_id\" true true false 32 Text 0 0 ,First,#," + rt + ",trip_id,-1,-1;DayMinutes \"DayMinutes\" true true false 8 Double 0 0 ,First,#," + rt + ",DayMinutes,-1,-1", "")

                log_message = "Beginning edit session 2 in {}".format(wkspcdata_gdb)
                logger.info(log_message)
                edit3.startEditing()

                # Cursor Search and Insert
                log_message = "Starting edit operations ..."
                logger.info(log_message)
                edit3.startOperation()

                wrStationTimes = arcpy.da.InsertCursor(railTimesWETemp, ["OBJECTID", "stop_id", "arrival_time", "departure_time", "trip_id", "DayMinutes"])

            else:
                log_message = "GTFS Times table has an unexpected name ..."
                logger.info(log_message)

            log_message = "Collecting Rail Station Times on {}".format(dayType)
            logger.info(log_message)

            statOID = None
            statShape = ["SHAPE@"]
            statNAme = None
            statStopID = None
            stCount = 0
            ndxRailStations = arcpy.da.SearchCursor(rail_taz_stations, ["OBJECTID", "SHAPE@", "NAME", "stop_id"], None, None, "False", (None, None))
            for sRow in ndxRailStations:
                statOID, statShape, statNAme, statStopID = sRow[0], sRow[1], sRow[2], sRow[3]
                if statStopID == None or statStopID == "":
                    pass
                else:
                    timeOID = None
                    timeStopID = None
                    timeArrival = None
                    timeDeparture = None
                    timeTripID = None
                    dayMinutes = 0.0

                    log_message = "Processing Stop ID: {}".format(statStopID)
                    logger.info(log_message)

                    exp = arcpy.AddFieldDelimiters(rt, "stop_id") + " = '" + statStopID + "'"
                    ndxRailTimes = arcpy.da.SearchCursor(rt, ["OBJECTID", "stop_id", "arrival_time", "departure_time", "trip_id", "DayMinutes"], where_clause=exp)
                    for tRow in ndxRailTimes:
                        timeOID, timeStopID, timeArrival, timeDeparture, timeTripID, dayMinutes = tRow[0], tRow[1], tRow[2], tRow[3], tRow[4], tRow[5]
                        if timeOID == None:
                            pass
                        else:
                            stCount += 1
                            wrStationTimes.insertRow([timeOID, timeStopID, timeArrival, timeDeparture, timeTripID, dayMinutes])
                    ## del tRow
                    del ndxRailTimes

            log_message = "{} GTFS Arrival/Departure times collected".format(str(stCount))
            logger.info(log_message)

        ## del sRow
        del ndxRailStations
        iCount += 1

        log_message = "Stopping edit operations ..."
        logger.info(log_message)
        edit3.stopOperation()

        log_message = "Ending edit session in {}".format(wkspcdata_gdb)
        logger.info(log_message)
        edit3.stopEditing(True)

        log_message = "{} records processed in {}".format(str(tCount), rt)
        logger.info(log_message)
        ## Breakpoint %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    log_message = "Sorting Weekday Rail Times... "
    logger.info(log_message)

    if arcpy.Exists(railTimesWDSort):
        arcpy.Delete_management(railTimesWDSort, "Table")

    # Process: Sort (3)
    arcpy.Sort_management(railTimesWDTemp, railTimesWDSort, "stop_id ASCENDING;DayMinutes ASCENDING", "UR")

    log_message = "Deleting {}".format(railTimesWD)
    logger.info(log_message)

    if arcpy.Exists(railTimesWD):
        arcpy.Delete_management(railTimesWD, "Table")

    log_message = "Creating distinct Stop List for Rail Transfer Times"
    logger.info(log_message)

    if arcpy.Exists(rail_taz_stoplist):
        arcpy.Delete_management(rail_taz_stoplist, "Table")

    # Process: Table to Table (3)
    arcpy.TableToTable_conversion(rail_taz_stations, wkspcdata_gdb, "Rail_TAZ_StopList", "location_type IS NOT NULL", "NAME \"Name\" true true false 80 Text 0 0 ,First,#," + rail_taz_stations + ",NAME,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + rail_taz_stations + ",stop_id,-1,-1;location_type \"location_type\" true true false 255 Text 0 0 ,First,#," + rail_taz_stations + ",location_type,-1,-1", "")

    log_message = "Calculating Weekday Average Rail Transfer Times ..."
    logger.info(log_message)
    wdCount = 0
    weCount = 0
    targetOID = None
    targetName = None
    targetStopID = None
    ndxTargetList = arcpy.da.SearchCursor(rail_taz_stoplist, ["OBJECTID", "NAME", "stop_id"], None, None, "False", (None, None))
    for stopRow in ndxTargetList:
        targetOID, targetName, targetStopID = stopRow[0], stopRow[1], stopRow[2]

        currOID = None
        currStopID, prevStopID = None, None
        currArrival = None
        currDeparture = None
        currTripID = None
        currMinutes, prevMinutes = 0.0, 0.0

        listAllDayXferWD = 0.0
        AllDayXferWDCount = 0
        avgAllDayXferWD = 0.0

        listEarlyAMXferWD = 0.0
        EarlyAMXferWDCount = 0
        avgEarlyAMXferWD = 0.0

        listPeakAMXferWD = 0.0
        PeakAMXferWDCount = 0
        avgPeakAMXferWD = 0.0

        listMidDayXferWD = 0.0
        MidDayXferWDCount = 0
        avgMidDayXferWD = 0.0

        listPeakPMXferWD = 0.0
        PeakPMXferWDCount = 0
        avgPeakPMXferWD = 0.0

        listLatePMXferWD = 0.0
        LatePMXferWDCount = 0
        avgLatePMXferWD = 0.0

        rdExp = arcpy.AddFieldDelimiters(railTimesWDSort, "stop_id") + " = '" + targetStopID + "'"
        ndxTimeCalc = arcpy.da.SearchCursor(railTimesWDSort, ["OBJECTID", "stop_id", "arrival_time", "departure_time", "trip_id", "DayMinutes"], where_clause=rdExp)
        for cRow in ndxTimeCalc:
            currOID, currStopID, currArrival, currDeparture, currTripID, currMinutes = cRow[0], cRow[1], cRow[2], cRow[3], cRow[4], cRow[5]
            if prevStopID == None:
                pass
            else:
                AllDayXferWDCount += 1

                if currMinutes < 180:
                    listEarlyAMXferWD = listEarlyAMXferWD + (currMinutes - prevMinutes)
                    EarlyAMXferWDCount += 1
                elif currMinutes < 360:
                    listPeakAMXferWD = listPeakAMXferWD + (currMinutes - prevMinutes)
                    PeakAMXferWDCount += 1
                elif currMinutes < 540:
                    listMidDayXferWD = listMidDayXferWD + (currMinutes - prevMinutes)
                    MidDayXferWDCount += 1
                elif currMinutes < 720:
                    listPeakPMXferWD = listPeakPMXferWD + (currMinutes - prevMinutes)
                    PeakPMXferWDCount += 1
                else:
                    listLatePMXferWD = listLatePMXferWD + (currMinutes - prevMinutes)
                    LatePMXferWDCount += 1

                listAllDayXferWD = listAllDayXferWD + (currMinutes - prevMinutes)

            prevStopID = currStopID
            prevMinutes = currMinutes

        ## del cRow
        del ndxTimeCalc

        if AllDayXferWDCount > 0:
            avgAllDayXferWD = listAllDayXferWD / AllDayXferWDCount
        else:
            avgAllDayXferWD = 0.0
        if EarlyAMXferWDCount > 0:
            avgEarlyAMXferWD = listEarlyAMXferWD / EarlyAMXferWDCount
        else:
            avgEarlyAMXferWD = 0.0
        if PeakAMXferWDCount > 0:
            avgPeakAMXferWD = listPeakAMXferWD / PeakAMXferWDCount
        else:
            avgPeakAMXferWD = 0.0
        if MidDayXferWDCount > 0:
            avgMidDayXferWD = listMidDayXferWD / MidDayXferWDCount
        else:
            avgMidDayXferWD = 0.0
        if PeakPMXferWDCount > 0:
            avgPeakPMXferWD = listPeakPMXferWD / PeakPMXferWDCount
        else:
            avgPeakPMXferWD = 0.0
        if LatePMXferWDCount > 0:
            avgLatePMXferWD = listLatePMXferWD / LatePMXferWDCount
        else:
            avgLatePMXferWD = 0.0

        railOID = None
        railStopID = None
        railAllDayXferWD = 0.0
        railEarlyAMXferWD = 0.0
        railPeakAMXferWD = 0.0
        railMidDayXferWD = 0.0
        railPeakPMXferWD = 0.0
        railLatePMXferWD = 0.0
        railAllDayXferWD = 0.0
        railEarlyAMXferWD = 0.0
        railPeakAMXferWD = 0.0
        railMidDayXferWD = 0.0
        railPeakPMXferWD = 0.0
        railLatePMXferWD = 0.0
        railLocType = None
        ## wrExp = arcpy.AddFieldDelimiters(rail_taz_stations, "stop_id") + " = '" + targetStopID + "'"
        wdRailNDX = arcpy.da.UpdateCursor(rail_taz_stations, ["OBJECTID", "stop_id", "Avg_AllDay_WaitTime_WD",
                                                               "Avg_EarlyAM_WaitTime_WD", "Avg_PeakAM_WaitTime_WD",
                                                               "Avg_MidDay_WaitTime_WD", "Avg_PeakPM_WaitTime_WD",
                                                               "Avg_LatePM_WaitTime_WD", "location_type"], None, None, "False", (None, None))
        for wdRow in wdRailNDX:
            railOID, railStopID, railAllDayXferWD, railEarlyAMXferWD, railPeakAMXferWD, railMidDayXferWD, railPeakPMXferWD, railLatePMXferWD, railLocType = \
            wdRow[0], wdRow[1], wdRow[2], wdRow[3], wdRow[4], wdRow[5], wdRow[6], wdRow[7], wdRow[8]
            if railStopID == targetStopID:
                wdCount += 1
                wdRow[2] = avgAllDayXferWD
                wdRow[3] = avgEarlyAMXferWD
                wdRow[4] = avgPeakAMXferWD
                wdRow[5] = avgMidDayXferWD
                wdRow[6] = avgPeakPMXferWD
                wdRow[7] = avgLatePMXferWD
                wdRailNDX.updateRow(wdRow)

                log_message = "Updated row {} for Weekday Average Tranfer Time at StopID {}".format(str(wdCount), targetStopID)
                logger.info(log_message)

        ## del wdRow
        del wdRailNDX

    ## del stopRow
    del ndxTargetList

    log_message = "Sorting Weekdend Rail Times... "
    logger.info(log_message)

    if arcpy.Exists(railTimesWESort):
        arcpy.Delete_management(railTimesWESort, "Table")

    # Process: Sort (3)
    arcpy.Sort_management(railTimesWETemp, railTimesWESort, "stop_id ASCENDING;DayMinutes ASCENDING", "UR")

    log_message = "Deleting {}".format(railTimesWE)
    logger.info(log_message)

    if arcpy.Exists(railTimesWE):
        arcpy.Delete_management(railTimesWE, "Table")

    log_message = "Calculating Weekend Average Rail Transfer Times ..."
    logger.info(log_message)

    targetOID = None
    targetName = None
    targetStopID = None
    ndxTargetList2 = arcpy.da.SearchCursor(rail_taz_stoplist, ["OBJECTID", "NAME", "stop_id"], None, None, "False", (None, None))
    for stop2Row in ndxTargetList2:
        targetOID, targetName, targetStopID = stop2Row[0], stop2Row[1], stop2Row[2]

        currOID = None
        currStopID, prevStopID = None, None
        currArrival = None
        currDeparture = None
        currTripID = None
        currMinutes, prevMinutes = 0.0, 0.0

        listAllDayXferWE = 0.0
        AllDayXferWECount = 0
        avgAllDayXferWE = 0.0

        listEarlyAMXferWE = 0.0
        EarlyAMXferWECount = 0
        avgEarlyAMXferWE = 0.0

        listPeakAMXferWE = 0.0
        PeakAMXferWECount = 0
        avgPeakAMXferWE = 0.0

        listMidDayXferWE = 0.0
        MidDayXferWECount = 0
        avgMidDayXferWE = 0.0

        listPeakPMXferWE = 0.0
        PeakPMXferWECount = 0
        avgPeakPMXferWE = 0.0

        listLatePMXferWE = 0.0
        LatePMXferWECount = 0
        avgLatePMXferWE = 0.0

        rdExp2 = arcpy.AddFieldDelimiters(railTimesWESort, "stop_id") + " = '" + targetStopID + "'"
        ndxTimeCalc2 = arcpy.da.SearchCursor(railTimesWESort, ["OBJECTID", "stop_id", "arrival_time", "departure_time", "trip_id", "DayMinutes"], where_clause=rdExp2)
        for c2Row in ndxTimeCalc2:
            currOID, currStopID, currArrival, currDeparture, currTripID, currMinutes = c2Row[0], c2Row[1], c2Row[2], c2Row[3], c2Row[4], c2Row[5]
            if prevStopID == None:
                pass
            else:
                AllDayXferWECount += 1

                if currMinutes < 180:
                    listEarlyAMXferWE = listEarlyAMXferWE + (currMinutes - prevMinutes)
                    EarlyAMXferWECount += 1
                elif currMinutes < 360:
                    listPeakAMXferWE = listPeakAMXferWE + (currMinutes - prevMinutes)
                    PeakAMXferWECount += 1
                elif currMinutes < 540:
                    listMidDayXferWE = listMidDayXferWE + (currMinutes - prevMinutes)
                    MidDayXferWECount += 1
                elif currMinutes < 720:
                    listPeakPMXferWE = listPeakPMXferWE + (currMinutes - prevMinutes)
                    PeakPMXferWECount += 1
                else:
                    listLatePMXferWE = listLatePMXferWE + (currMinutes - prevMinutes)
                    LatePMXferWECount += 1

                listAllDayXferWE = listAllDayXferWE + (currMinutes - prevMinutes)

            prevStopID = currStopID
            prevMinutes = currMinutes

        ## del c2Row
        del ndxTimeCalc2

        if AllDayXferWECount > 0:
            avgAllDayXferWE = listAllDayXferWE / AllDayXferWECount
        else:
            avgAllDayXferWE = 0.0
        if EarlyAMXferWECount > 0:
            avgEarlyAMXferWE = listEarlyAMXferWE / EarlyAMXferWECount
        else:
            avgEarlyAMXferWE = 0.0
        if PeakAMXferWECount > 0:
            avgPeakAMXferWE = listPeakAMXferWE / PeakAMXferWECount
        else:
            avgPeakAMXferWE = 0
        if MidDayXferWECount > 0:
            avgMidDayXferWE = listMidDayXferWE / MidDayXferWECount
        else:
            avgMidDayXferWE = 0.0
        if PeakPMXferWECount > 0:
            avgPeakPMXferWE = listPeakPMXferWE / PeakPMXferWECount
        else:
            avgPeakPMXferWE = 0.0
        if LatePMXferWECount > 0:
            avgLatePMXferWE = listLatePMXferWE / LatePMXferWECount
        else:
            avgLatePMXferWE = 0.0

        railOID = None
        railStopID = None
        railAllDayXferWE = 0.0
        railEarlyAMXferWE = 0.0
        railPeakAMXferWE = 0.0
        railMidDayXferWE = 0.0
        railPeakPMXferWE = 0.0
        railLatePMXferWE = 0.0
        railLocType = None
        ## wrExp2 = arcpy.AddFieldDelimiters(rail_taz_stations, "stop_id") + " = '" + targetStopID + "'"
        weRailNDX = arcpy.da.UpdateCursor(rail_taz_stations, ["OBJECTID", "stop_id", "Avg_AllDay_WaitTime_WE",
                                                              "Avg_EarlyAM_WaitTime_WE", "Avg_PeakAM_WaitTime_WE",
                                                              "Avg_MidDay_WaitTime_WE", "Avg_PeakPM_WaitTime_WE",
                                                              "Avg_LatePM_WaitTime_WE", "location_type"], None, None, "False", (None, None))
        for weRow in weRailNDX:
            railOID, railStopID, railAllDayXferWE, railEarlyAMXferWE, railPeakAMXferWE, railMidDayXferWE, railPeakPMXferWE, railLatePMXferWE, railLocType = \
            weRow[0], weRow[1], weRow[2], weRow[3], weRow[4], weRow[5], weRow[6], weRow[7], weRow[8]
            if railStopID == targetStopID:
                weCount += 1
                weRow[2] = avgAllDayXferWE
                weRow[3] = avgEarlyAMXferWE
                weRow[4] = avgPeakAMXferWE
                weRow[5] = avgMidDayXferWE
                weRow[6] = avgPeakPMXferWE
                weRow[7] = avgLatePMXferWE
                weRailNDX.updateRow(weRow)

                log_message = "Updated row {} for Weekend Average Tranfer Time at StopID {}".format(str(weCount), targetStopID)
                logger.info(log_message)

        ## del weRow
        del weRailNDX

    ## del stop2Row
    del ndxTargetList2

    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%% NEW CODE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Extending Rail Line (5 meters) in : " + src_all_rail_lines
    logger.info(log_message)

    # Process: Extend Line - Reset intersections of segments up to 5.0 meters
    arcpy.ExtendLine_edit(src_all_rail_lines, "5 Meters", "EXTENSION")

    if arcpy.Exists(rail_service_lines):
        arcpy.Delete_management(rail_service_lines, "FeatureClass")

    log_message = "Splitting traversal at Rail Stops to create {}".format(rail_service_lines)
    logger.info(log_message)

    # Process: Split Line at Point
    arcpy.SplitLineAtPoint_management(src_all_rail_lines, rail_taz_stations, rail_service_lines, "0.015 Miles")

    log_message = "Clipping Rail Lines by the Study Area to create {}".format(rail_service_lineM)
    logger.info(log_message)

    if arcpy.Exists(rail_service_lineM):
        arcpy.Delete_management(rail_service_lineM, "FeatureClass")

    # Process: Clip
    arcpy.Clip_analysis(rail_service_lines, taz_studyarea_proj, rail_service_lineM, "0.001 Miles")

    log_message = "Calculating the Rail Line Identifier: LINEARID"
    logger.info(log_message)

    # Process: Calculate Field (6)
    arcpy.CalculateField_management(rail_service_lineM, "LINEARID", "railIdentifier( !LINEARID! , !LINE! )", "PYTHON_9.3",
                                    "def railIdentifier(lineID, lineNM):\\n  retVal = \"\"\\n  if lineID == None:\\n    retVal = lineNM\\n  else:\\n    retVal = lineID\\n  return retVal")

    if arcpy.Exists(rail_service_sortM):
        arcpy.Delete_management(rail_service_sortM, "FeatureClass")

    log_message = "Creating M-Enabled Rail Lines in {}".format(str(rail_service_sortM))
    logger.info(log_message)

    # Process: Create Routes
    arcpy.CreateRoutes_lr(rail_service_lineM, "LINEARID", rail_service_sortM, "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    ## Adding TAZ Zone Name %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if arcpy.Exists(rail_taz_sortM):
        arcpy.Delete_management(rail_taz_sortM, "FeatureClass")

    log_message = "Clipping Rail Links to the Study Area for {}".format(rail_taz_sortM)
    logger.info(log_message)

    # Process: Clip
    arcpy.Clip_analysis(rail_service_sortM, taz_studyarea_proj, rail_taz_sortM, "0.001 Miles")

    if arcpy.Exists(rail_taz_path):
        arcpy.Delete_management(rail_taz_path, "FeatureClass")

    log_message = "Running Spatial Join between Rail Paths and TAZ Polygons for the Zone Name identifier ..."
    logger.info(log_message)

    # Process: Spatial Join
    arcpy.SpatialJoin_analysis(rail_taz_sortM, taz_studyarea_proj, rail_taz_path, "JOIN_ONE_TO_ONE", "KEEP_ALL", "LINEARID \"LINEARID\" true true false 22 Text 0 0 ,First,#," + rail_taz_sortM + ",LINEARID,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + rail_taz_sortM + ",Shape_Length,-1,-1;ZONE_NAME \"name\" true true false 13 Text 0 0 ,First,#," + taz_studyarea_proj + ",name,-1,-1", "HAVE_THEIR_CENTER_IN", "", "")
    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    log_message = "Repairing Geometry in: {}".format(rail_taz_path)
    logger.info(log_message)

    arcpy.RepairGeometry_management(in_features=rail_taz_path, delete_null="DELETE_NULL")

    log_message = "Extracting First & Last X, Y, M from Intersection Segments in: " + rail_taz_path + " ..."
    logger.info(log_message)

    fc_list = [f.name for f in arcpy.ListFields(rail_taz_path)]
    field_names = ["FROM_X", "FROM_Y", "TO_X", "TO_Y", "FROM_M", "TO_M"]
    for field_name in field_names:
        if field_name not in fc_list:
            arcpy.AddField_management(rail_taz_path, field_name, "DOUBLE")

    field_names = ["SHAPE@"] + field_names

    with arcpy.da.UpdateCursor(rail_taz_path, field_names) as cursor:
        for row in cursor:
            line_geom = row[0]

            start = arcpy.PointGeometry(line_geom.firstPoint)
            start_xy = start.WKT.strip("POINT (").strip(")").split(" ")
            row[1] = start_xy[0]  # FROM_X
            row[2] = start_xy[1]  # FROM_Y

            end = arcpy.PointGeometry(line_geom.lastPoint)
            end_xy = end.WKT.strip("POINT (").strip(")").split(" ")
            row[3] = end_xy[0]  # TO_X
            row[4] = end_xy[1]  # TO_Y

            from_dfo = line_geom.firstPoint.M  ## row[5]
            to_dfo = line_geom.lastPoint.M
            if to_dfo > from_dfo:
                row[5] = from_dfo
                row[6] = to_dfo
            elif to_dfo != 0:
                row[5] = to_dfo
                row[6] = from_dfo
            cursor.updateRow(row)
    del row
    del cursor

    log_message = "Adjusting From M for segment length accuracy ..."
    logger.info(log_message)

    # Process: Calculate Field (7)
    arcpy.CalculateField_management(rail_taz_path, "FROM_M", "adjustFrmDFO( !FROM_M! , !TO_M! )", "PYTHON_9.3",
                                    "def adjustFrmDFO(fdfo, tdfo):\\n  outM = fdfo\\n  calcM = tdfo - fdfo\\n  if calcM < 0.001:\\n    outM = 0.0\\n  return outM\\n  \\n  ")

    log_message = "Converting Meters to Miles in From_M and To_M fields ..."
    logger.info(log_message)

    # Process: Calculate Field
    arcpy.CalculateField_management(rail_taz_path, "FROM_M", "convertAutoFrmM( !FROM_M! )", "PYTHON_9.3",
                                    "def convertAutoFrmM(fromM):\\n  inFDFO = 0  \\n  outFDFO = 0\\n  if fromM == None or fromM == 0:\\n    pass\\n  else:       \\n    inFDFO = fromM/1609.344\\n    outFDFO = str((inFDFO * 1000)/1000)\\n  return round(float(outFDFO), 3)\\n  ")

    # Process: Calculate Field (2)
    arcpy.CalculateField_management(rail_taz_path, "TO_M", "convertAutoToM( !TO_M! )", "PYTHON_9.3",
                                    "def convertAutoToM(toM):\\n  inTDFO = 0  \\n  outTDFO = 0\\n  if toM == None or toM == 0:\\n    pass\\n  else:       \\n    inTDFO = toM/1609.344\\n    outTDFO = str((inTDFO * 1000)/1000)\\n  return round(float(outTDFO), 3)")

    if arcpy.Exists(rail_taz_centerline):
        arcpy.Delete_management(rail_taz_centerline, "FeatureClass")

    log_message = "Sorting results to {}".format(str(rail_taz_centerline))
    logger.info(log_message)

    # Process: Sort (3)
    arcpy.Sort_management(rail_taz_path, rail_taz_centerline, "LINEARID ASCENDING;FROM_M ASCENDING;TO_M ASCENDING", "UR")

    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    log_message = "Repairing Geometry in: {}".format(rail_taz_stations)
    logger.info(log_message)

    arcpy.RepairGeometry_management(in_features=rail_taz_stations, delete_null="DELETE_NULL")

    spatial_ref = arcpy.Describe(rail_taz_stations).spatialReference

    log_message = "Extracting X, Y Coordinates from: {}".format(rail_taz_stations)
    logger.info(log_message)

    pnt_list = [p.name for p in arcpy.ListFields(rail_taz_stations)]
    field_nms = ["STOP_X", "STOP_Y"]
    for field_nm in field_nms:
        if field_nm not in pnt_list:
            arcpy.AddField_management(rail_taz_stations, field_nm, "DOUBLE")

    field_nms = ["SHAPE@"] + field_nms

    with arcpy.da.UpdateCursor(rail_taz_stations, field_nms) as pCursor:
        for pRow in pCursor:
            pnt_geom = pRow[0]

            pStop = arcpy.PointGeometry(pnt_geom.firstPoint, spatial_ref)
            pStop_XY = pStop.WKT.strip("POINT (").strip(")").split(" ")
            pRow[1] = pStop_XY[0]  # STOP_X
            pRow[2] = pStop_XY[1]  # STOP_Y

            pCursor.updateRow(pRow)

    del pRow
    del pCursor

    log_message = "Adding/Updating Bus Stop GeoID in {}".format(rail_taz_stations)
    logger.info(log_message)

    geoid_list = [g.name for g in arcpy.ListFields(rail_taz_stations)]
    geoid_nms = ["GeoID"]
    for geoid_nm in geoid_nms:
        if geoid_nm not in geoid_list:
            arcpy.AddField_management(rail_taz_stations, "GeoID", "TEXT", "", "", "30", "GeoID", "NULLABLE", "NON_REQUIRED", "")

    # Process: Calculate Field (3)
    arcpy.CalculateField_management(rail_taz_stations, "GeoID", "createGeoID( !STOP_Y! , !STOP_X! )", "PYTHON_9.3",
                                    "def createGeoID(stop_y, stop_x):\\n  retID = \"\"\\n  if stop_y == None or stop_x == None:\\n    pass\\n  else:\\n    retID = str(round(stop_y, 8)) + \",\" + str(round(stop_x, 8))\\n  return retID")
    ### %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    log_message = "Clearing intermediate tables..."
    logger.info(log_message)

    if arcpy.Exists(rail_taz_stops_temp):
        arcpy.Delete_management(rail_taz_stops_temp, "FeatureClass")

    if arcpy.Exists(rail_service_lines):
        arcpy.Delete_management(rail_service_lines, "FeatureClass")

    if arcpy.Exists(railTimesWDSort):
        arcpy.Delete_management(railTimesWDSort, "Table")

    if arcpy.Exists(railTimesWDTemp):
        arcpy.Delete_management(railTimesWDTemp, "Table")

    if arcpy.Exists(railTimesWESort):
        arcpy.Delete_management(railTimesWESort, "Table")

    if arcpy.Exists(railTimesWETemp):
        arcpy.Delete_management(railTimesWETemp, "Table")

    if arcpy.Exists(src_all_rail_lines):
        arcpy.Delete_management(src_all_rail_lines, "FeatureClass")

    if arcpy.Exists(rail_service_lineM):
        arcpy.Delete_management(rail_service_lineM, "FeatureClass")

    if arcpy.Exists(rail_service_sortM):
        arcpy.Delete_management(rail_service_sortM, "FeatureClass")

    log_message = "Rail Network inputs are ready !!"
    logger.info(log_message)

    return "%%%%%%% Process E4 Complete %%%%%%%"


def loadTransitNetworkInputs(wkspcdata_gdb, transit_fd_gdb, logger):

    log_message = "%%%%%%% Process E5 - Load All Network Inputs to the Local Feature Datasets %%%%%%%"
    logger.info(log_message)

    # Local variables:
    ped_taz_centerline = os.path.join(wkspcdata_gdb, "Ped_TAZ_Centerline")
    ped_taz_network = transit_fd_gdb + "\\Ped_TAZ_Network"

    bus_taz_centerline = os.path.join(wkspcdata_gdb, "Bus_TAZ_Centerline")
    bus_taz_network = transit_fd_gdb + "\\Bus_TAZ_Network"

    bus_taz_stop_pnt = os.path.join(wkspcdata_gdb, "Bus_TAZ_StopPoints")  ## Bus-to-Bus Transfer Times
    bus_taz_stops = transit_fd_gdb + "\\Bus_TAZ_Stops"

    trans_xfer_stations = os.path.join(wkspcdata_gdb, "Transit_Transfer_Stations")  ## Bus-to-Rail & Rail-to-Bus Transfer Times
    transit_transfer_stations = transit_fd_gdb + "\\Transit_Transfer_Stations"

    rail_taz_stations = os.path.join(wkspcdata_gdb, "Rail_TAZ_Stations")  ## Rail-to-Rail Transfer Times
    rail_transfer_stations = transit_fd_gdb + "\\Rail_TAZ_Stations"

    rail_taz_centerline = os.path.join(wkspcdata_gdb, "Rail_TAZ_Centerline")
    rail_taz_network = transit_fd_gdb + "\\Rail_TAZ_Network"

    ## Multimodal Transit Network Dataset
    mm_transit_nd = transit_fd_gdb + "\\TransitNetwork_ND"
    mm_transit_junctions = transit_fd_gdb + "\\TransitNetwork_ND_Junctions"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    log_message = "Writing Ped_TAZ_Centerline in GCS NAD83 to {}".format(ped_taz_network)
    logger.info(log_message)

    if arcpy.Exists(ped_taz_network):
        arcpy.Delete_management(ped_taz_network, "FeatureClass")

    # Process: Project
    arcpy.Project_management(ped_taz_centerline, ped_taz_network,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Bus_TAZ_Centerline in GCS NAD83 to {}".format(bus_taz_network)
    logger.info(log_message)

    if arcpy.Exists(bus_taz_network):
        arcpy.Delete_management(bus_taz_network, "FeatureClass")

    # Process: Project (2)
    arcpy.Project_management(bus_taz_centerline, bus_taz_network,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Bus_TAZ_StopPoints in GCS NAD83 to {}".format(bus_taz_stops)
    logger.info(log_message)

    if arcpy.Exists(bus_taz_stops):
        arcpy.Delete_management(bus_taz_stops, "FeatureClass")

    # Process: Project (3)
    arcpy.Project_management(bus_taz_stop_pnt, bus_taz_stops,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Transit_Transfer_Stations in GCS NAD83 to {}".format(transit_transfer_stations)
    logger.info(log_message)

    if arcpy.Exists(transit_transfer_stations):
        arcpy.Delete_management(transit_transfer_stations, "FeatureClass")

    # Process: Project (4)
    arcpy.Project_management(trans_xfer_stations, transit_transfer_stations,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Rail_TAZ_Stations in GCS NAD83 to {}".format(rail_transfer_stations)
    logger.info(log_message)

    if arcpy.Exists(rail_transfer_stations):
        arcpy.Delete_management(rail_transfer_stations, "FeatureClass")

    # Process: Project (5)
    arcpy.Project_management(rail_taz_stations, rail_transfer_stations,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Writing Rail_TAZ_Centerline in GCS NAD83 to {}".format(rail_taz_network)
    logger.info(log_message)

    if arcpy.Exists(rail_taz_network):
        arcpy.Delete_management(rail_taz_network, "FeatureClass")

    # Process: Project (6)
    arcpy.Project_management(rail_taz_centerline, rail_taz_network,
                             "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                             "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]",
                             "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

    log_message = "Transit Network Inputs are ready for the ND Build manual process !!!"
    logger.info(log_message)

    return "%%%%%%% Process E5 Complete %%%%%%%"


def createMultiModalTemplate(wkspcdata_gdb, cgc_templates, logger):

    log_message = "%%%%%%% Create the Multimodal Transit Centerline Template %%%%%%%"
    logger.info(log_message)

    auto_taz_centerline = os.path.join(wkspcdata_gdb, "Auto_TAZ_Centerline")
    multimodal_trans_layer = cgc_templates + "\\MultiModalTransitTemp"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = cgc_templates
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    if arcpy.Exists(multimodal_trans_layer):
        arcpy.Delete_management(multimodal_trans_layer, "FeatureClass")

    log_message = "Converting the Auto Centerline to the Multimodal Transport template: {}".format(multimodal_trans_layer)
    logger.info(log_message)

    # Process: Feature Class to Feature Class
    arcpy.FeatureClassToFeatureClass_conversion(auto_taz_centerline, cgc_templates, "MultiModalTransitTemp", "", "RouteID \"RouteID\" true true false 22 Text 0 0 ,First,#," + auto_taz_centerline + ",LINEARID,-1,-1;RouteName \"RouteName\" true true false 100 Text 0 0 ,First,#," + auto_taz_centerline + ",FULLNAME,-1,-1;RouteModeCD \"RouteModeCD\" true true false 3 Text 0 0 ,First,#," + auto_taz_centerline + ",id,-1,-1;ZONE_NAME \"ZONE_NAME\" true true false 18 Text 0 0 ,First,#," + auto_taz_centerline + ",ZONE_NAME,-1,-1;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#," + auto_taz_centerline + ",SHAPE_Length,-1,-1", "")

    # Process: Delete Features
    arcpy.DeleteFeatures_management(multimodal_trans_layer)

    return "%%%%%%% Template Ready %%%%%%%"


def createBusCenterlineTemplate(wkspcdata_gdb, bus_rte_link_data, logger):

    log_message = "%%%%%%% Create the Bus Centerline Template %%%%%%%"
    logger.info(log_message)

    bus_centerline_layer = wkspcdata_gdb + "\\Bus_Data_Centerline"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    if arcpy.Exists(bus_centerline_layer ):
        arcpy.Delete_management(bus_centerline_layer, "FeatureClass")

    log_message = "Converting the bus link data features to the Bus Data Centerline template: {}".format(bus_centerline_layer)
    logger.info(log_message)

    # Process: Feature Class to Feature Class (2)
    arcpy.FeatureClassToFeatureClass_conversion(bus_rte_link_data, wkspcdata_gdb, "Bus_Data_Centerline", "", "OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + bus_rte_link_data + ",OperRtNM,-1,-1;stop_id \"stop_id\" true true false 8000 Text 0 0 ,First,#," + bus_rte_link_data + ",stop_id,-1,-1;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_PeakPM_WaitTime_WD,-1,-1;Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_PeakPM_WaitTime_WE,-1,-1;Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0 ,First,#," + bus_rte_link_data + ",agency,-1,-1;route_id_all \"route_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_rte_link_data + ",route_id_all,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + bus_rte_link_data + ",direction_id_all,-1,-1;location_type \"location_type\" true true false 2147483647 Text 0 0 ,First,#," + bus_rte_link_data + ",location_type,-1,-1;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0 ,First,#," + bus_rte_link_data + ",wheelchair_boarding,-1,-1;stop_lat \"stop_lat\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0 ,First,#," + bus_rte_link_data + ",stop_lon,-1,-1;stop_url \"stop_url\" true true false 2147483647 Text 0 0 ,First,#," + bus_rte_link_data + ",stop_url,-1,-1;parent_station \"parent_station\" true true false 2147483647 Text 0 0 ,First,#," + bus_rte_link_data + ",parent_station,-1,-1;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID1,-1,-1;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID2,-1,-1;BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID3,-1,-1;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID4,-1,-1;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID5,-1,-1;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID6,-1,-1;BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID7,-1,-1;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID8,-1,-1;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID9,-1,-1;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0 ,First,#," + bus_rte_link_data + ",BusRouteID10,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + bus_rte_link_data + ",Shape_Length,-1,-1", "")

    return "%%%%%%% Template Ready %%%%%%%"


def createBusRouteLnTemplate(wkspcdata_gdb, proxy_bus_routes, logger):

    log_message = "%%%%%%% Create the Bus Route Line Template %%%%%%%"
    logger.info(log_message)

    bus_route_layer = wkspcdata_gdb + "\\BusRouteTemp"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    if arcpy.Exists(bus_route_layer):
        arcpy.Delete_management(bus_route_layer, "FeatureClass")

    log_message = "Converting the bus route features in proximity to the Bus Route template: {}".format(bus_route_layer)
    logger.info(log_message)

    # Process: Feature Class to Feature Class
    arcpy.FeatureClassToFeatureClass_conversion(proxy_bus_routes, wkspcdata_gdb, "BusRouteTemp", "", "TransitRouteID \"Transit Route ID\" true true false 4 Long 0 0 ,First,#," + proxy_bus_routes + ",TransitRouteID,-1,-1;TransitRoute \"Transit Route Number\" true true false 254 Text 0 0 ,First,#," + proxy_bus_routes + ",TransitRoute,-1,-1;OperRtNM \"Operator Route Name(s)\" true true false 8000 Text 0 0 ,First,#," + proxy_bus_routes + ",OperRtNM,-1,-1;FullRtName \"Full Route Name\" true true false 75 Text 0 0 ,First,#," + proxy_bus_routes + ",FullRtName,-1,-1;Operator \"Operator\" true true false 254 Text 0 0 ,First,#," + proxy_bus_routes + ",Operator,-1,-1;Headyway \"Headway\" true true false 4 Long 0 0 ,First,#," + proxy_bus_routes + ",Headyway,-1,-1;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0 ,First,#," + proxy_bus_routes + ",direction_id_all,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + proxy_bus_routes + ",Shape_Length,-1,-1", "")

    return "%%%%%%% Template Ready %%%%%%%"


def createBusRteSelectTemplate(wkspcdata_gdb, bus_taz_stops, logger):

    log_message = "%%%%%%% Create the Bus Route Selection Template %%%%%%%"
    logger.info(log_message)

    bus_route_select_layer = wkspcdata_gdb + "\\BusRouteSelectTemp"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    if arcpy.Exists(bus_route_select_layer):
        arcpy.Delete_management(bus_route_select_layer, "FeatureClass")

    log_message = "Converting the Bus Stops to the Bus Route Selection template: {}".format(bus_route_select_layer)
    logger.info(log_message)

    # Process: Feature Class To Feature Class
    arcpy.FeatureClassToFeatureClass_conversion(in_features=bus_taz_stops, out_path=wkspcdata_gdb, out_name="BusRouteSelectTemp", where_clause="", field_mapping="stop_id \"stop_id\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",stop_id,0,8000;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",direction_id_all,0,8000;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID1,0,255;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID2,0,255", config_keyword="")

    return "%%%%%%% Template Ready %%%%%%%"


def createBusRteStopTemplate(wkspcdata_gdb, bus_taz_stops, logger):

    log_message = "%%%%%%% Create the Bus Route Stops Template %%%%%%%"
    logger.info(log_message)

    bus_route_stop_layer = wkspcdata_gdb + "\\BusRouteStopsTemp"

    # Set Geoprocessing environments
    arcpy.env.scratchWorkspace = wkspcdata_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    if arcpy.Exists(bus_route_stop_layer):
        arcpy.Delete_management(bus_route_stop_layer, "FeatureClass")

    log_message = "Converting the Bus Stops to the Bus Route Stops template: {}".format(bus_route_stop_layer)
    logger.info(log_message)

    # Process: Feature Class To Feature Class
    arcpy.FeatureClassToFeatureClass_conversion(in_features=bus_taz_stops, out_path=wkspcdata_gdb, out_name="BusRouteStopsTemp", where_clause="", field_mapping="stop_id \"stop_id\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",stop_id,0,8000;Avg_AllDay_WaitTime_WD \"Avg_AllDay_WaitTime_WD\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_AllDay_WaitTime_WD,-1,-1;Avg_EarlyAM_WaitTime_WD \"Avg_EarlyAM_WaitTime_WD\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_EarlyAM_WaitTime_WD,-1,-1;Avg_PeakAM_WaitTime_WD \"Avg_PeakAM_WaitTime_WD\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_PeakAM_WaitTime_WD,-1,-1;Avg_MidDay_WaitTime_WD \"Avg_MidDay_WaitTime_WD\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_MidDay_WaitTime_WD,-1,-1;Avg_PeakPM_WaitTime_WD \"Avg_PeakPM_WaitTime_WD\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_PeakPM_WaitTime_WD,-1,-1;Avg_LatePM_WaitTime_WD \"Avg_LatePM_WaitTime_WD\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_LatePM_WaitTime_WD,-1,-1;Avg_AllDay_WaitTime_WE \"Avg_AllDay_WaitTime_WE\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_AllDay_WaitTime_WE,-1,-1;Avg_EarlyAM_WaitTime_WE \"Avg_EarlyAM_WaitTime_WE\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_EarlyAM_WaitTime_WE,-1,-1;Avg_PeakAM_WaitTime_WE \"Avg_PeakAM_WaitTime_WE\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_PeakAM_WaitTime_WE,-1,-1;Avg_MidDay_WaitTime_WE \"Avg_MidDay_WaitTime_WE\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_MidDay_WaitTime_WE,-1,-1;Avg_PeakPM_WaitTime_WE \"Avg_PeakPM_WaitTime_WE\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_PeakPM_WaitTime_WE,-1,-1;Avg_LatePM_WaitTime_WE \"Avg_LatePM_WaitTime_WE\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",Avg_LatePM_WaitTime_WE,-1,-1;agency \"agency\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",agency,0,8000;route_id_all \"route_id_all\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",route_id_all,0,8000;route_short_name_all \"route_short_name_all\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",route_short_name_all,0,8000;direction_id_all \"direction_id_all\" true true false 8000 Text 0 0,First,#," + bus_taz_stops + ",direction_id_all,0,8000;location_type \"location_type\" true true false 2147483647 Text 0 0,First,#," + bus_taz_stops + ",location_type,0,2147483647;wheelchair_boarding \"wheelchair_boarding\" true true false 4 Long 0 0,First,#," + bus_taz_stops + ",wheelchair_boarding,-1,-1;stop_desc \"stop_desc\" true true false 2147483647 Text 0 0,First,#," + bus_taz_stops + ",stop_desc,0,2147483647;stop_lat \"stop_lat\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",stop_lat,-1,-1;stop_lon \"stop_lon\" true true false 8 Double 0 0,First,#," + bus_taz_stops + ",stop_lon,-1,-1;zone_id \"zone_id\" true true false 2147483647 Text 0 0,First,#," + bus_taz_stops + ",zone_id,0,2147483647;stop_url \"stop_url\" true true false 2147483647 Text 0 0,First,#," + bus_taz_stops + ",stop_url,0,2147483647;parent_station \"parent_station\" true true false 2147483647 Text 0 0,First,#," + bus_taz_stops + ",parent_station,0,2147483647;BusRouteID1 \"BusRouteID1\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID1,0,255;BusRouteID2 \"BusRouteID2\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID2,0,255;BusRouteID3 \"BusRouteID3\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID3,0,255;BusRouteID4 \"BusRouteID4\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID4,0,255;BusRouteID5 \"BusRouteID5\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID5,0,255;BusRouteID6 \"BusRouteID6\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID6,0,255;BusRouteID7 \"BusRouteID7\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID7,0,255;BusRouteID8 \"BusRouteID8\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID8,0,255;BusRouteID9 \"BusRouteID9\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID9,0,255;BusRouteID10 \"BusRouteID10\" true true false 255 Text 0 0,First,#," + bus_taz_stops + ",BusRouteID10,0,255", config_keyword="")

    return "%%%%%%% Template Ready %%%%%%%"


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

    result_e1 = constructAutoNetwork(staging_gdb, workspace_gdb, localAutoFD, logger)
    logger.info(result_e1)

    result_e2 = segmentPedestrianPaths(staging_gdb, workspace_gdb, template_gdb, logger)
    logger.info(result_e2)

    result_e3 = segmentBusRoutes(cgcsrcdata, staging_gdb, workspace_gdb, template_gdb, logger)
    logger.info(result_e3)

    result_e4 = segmentRailLines(cgcsrcdata, staging_gdb, workspace_gdb, template_gdb, logger)
    logger.info(result_e4)

    result_e5 = loadTransitNetworkInputs(workspace_gdb, localTransitFD, logger)
    logger.info(result_e5)