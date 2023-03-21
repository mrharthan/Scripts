# ---------------------------------------------------------------------------
# execute_lrm.py
# Modified on: 2021-11-22
# Description: Applies linear referencing methods to the input assets
# Author: J. S. Pedigo --- D:\Projects\GISDWH_ASSETS\scripts
# ---------------------------------------------------------------------------

import os
import sys
import string
import arcpy
import cgc_logging

#----------------------------------------------------------------------
def transformEventLRM(gisdwh, localFD, conn_data_path, tools_dir_nm, workspace_gdb_nm, data_dir_nm, asset_data_gdb_nm, temp_data_gdb, assetgroup, logger):

    log_message = "Begin Asset/Event Transformation:"
    logger.info(log_message)

    # Set Geoprocessing environments
    tc_dir = os.path.join(conn_data_path, tools_dir_nm)
    tcEvents_gdb = os.path.join(tc_dir, workspace_gdb_nm)
    dc_dir = os.path.join(conn_data_path, data_dir_nm)
    dcEvents_gdb = os.path.join(dc_dir, asset_data_gdb_nm)
    local_data_path = r"D:\Projects\GISDWH\lrs_locator\tools"  # for access to local FGDB

    arcpy.env.scratchWorkspace = tcEvents_gdb
    arcpy.env.workspace = arcpy.env.scratchWorkspace

    # Local variables:
    lrs_ctrl_sect_asset_lyr = os.path.join(localFD, "lrs_ctrl_sect_asset_lyr")  # V2 Production Version
    template_ctrl_sect_asset_lyr = os.path.join(temp_data_gdb, "local_ctrl_sect_asset_lyr")  # local template data store
    aadt_ctrl_sect_asset_lyr = os.path.join(dcEvents_gdb, "aadt_ctrl_sect_asset_lyr")
    aadt_ctrl_sect_asset_dissolve = os.path.join(dcEvents_gdb, "aadt_ctrl_sect_asset_dissolve")
    format_ctrl_sect_asset_lyr = os.path.join(dcEvents_gdb, "format_ctrl_sect_asset_lyr")
    sort_ctrl_sect_asset_lyr = os.path.join(dcEvents_gdb, "sort_ctrl_sect_asset_lyr")
    ctrl_sect_rdbd_tbl = os.path.join(tcEvents_gdb, "ctrl_sect_rdbd_tbl")
    asset_traversal_tbl = os.path.join(tcEvents_gdb, "asset_traversal_tbl")
    asset_traversal_event = os.path.join(tcEvents_gdb, "asset_traversal_event")
    sort_asset_traversal_event = os.path.join(tcEvents_gdb, "sort_asset_traversal_event")
    Output_Event_Table_Properties = "LRS_RTE_ID LINE ASSET_LN_BEGIN_DFO_MS ASSET_LN_END_DFO_MS"
    ctrl_sect_rdbd_m = os.path.join(tcEvents_gdb, "ctrl_sect_rdbd_m")
    asset_traversal_events = "in_memory\\asset_traversal_events"
    ctrl_sect_assets = os.path.join(tcEvents_gdb, "ctrl_sect_assets")
    mprme = os.path.join(tcEvents_gdb, "mprme")
    Delete_succeeded = "false"
    Delete_succeeded_1 = "false"
    Delete_succeeded_2 = "false"
    Delete_succeeded_3 = "false"
    Delete_succeeded_4 = "false"
    Delete_succeeded_5 = "false"
    Delete_succeeded_6 = "false"
    Delete_succeeded_7 = "false"
    Delete_succeeded_8 = "false"

    eventFlag = False  # Permanent

    if assetgroup == ['CUR_AADT_LN_TBL', 'CUR_AADT_LN_TBL2']:  ## Job 3 failed due to environmental issues (Error: 999999/999998)

        log_message = "Clearing AADT Records in {}".format(lrs_ctrl_sect_asset_lyr)
        logger.info(log_message)

        trackCount = arcpy.GetCount_management(lrs_ctrl_sect_asset_lyr)
        tCount = int(trackCount[0])

        exp = arcpy.AddFieldDelimiters(lrs_ctrl_sect_asset_lyr, "asset_type_desc") + " IN('Current AADT')"

        ID1 = None
        trackID = None
        t = 0
        assetLN = arcpy.da.UpdateCursor(lrs_ctrl_sect_asset_lyr, ["OBJECTID", "lrs_rte_id"], where_clause=exp)
        for aRow in assetLN:
            ID1, trackID = aRow[0], aRow[1]
            if trackID != None:
                t += 1
                assetLN.deleteRow()

        del aRow
        del assetLN

        log_message = "Cleared {} AADT Records of {} in {}".format(t, str(tCount), lrs_ctrl_sect_asset_lyr)
        logger.info(log_message)

    else:  ## Job 3 under normal process

        log_message = "Clearing Records in " + template_ctrl_sect_asset_lyr + " ..."
        logger.info(log_message)

        # Process: Delete Features
        arcpy.DeleteFeatures_management(template_ctrl_sect_asset_lyr)

        log_message = "Exporting " + lrs_ctrl_sect_asset_lyr + " from template"
        logger.info(log_message)

        if arcpy.Exists(lrs_ctrl_sect_asset_lyr):
            arcpy.Delete_management(lrs_ctrl_sect_asset_lyr, "FeatureClass")
            Delete_succeeded = "true"

        # V2 Production Process: Feature Class to Feature Class (2)
        arcpy.FeatureClassToFeatureClass_conversion(template_ctrl_sect_asset_lyr, localFD, "lrs_ctrl_sect_asset_lyr", "", "lrs_rte_id \"lrs_rte_id\" true true false 20 Text 0 0 ,First,#," + template_ctrl_sect_asset_lyr + ",lrs_rte_id,-1,-1;asset_ln_begin_dfo_ms \"asset_ln_begin_dfo_ms\" true false false 8 Double 8 38 ,First,#," + template_ctrl_sect_asset_lyr + ",asset_ln_begin_dfo_ms,-1,-1;asset_ln_end_dfo_ms \"asset_ln_end_dfo_ms\" true false false 8 Double 8 38 ,First,#," + template_ctrl_sect_asset_lyr + ",asset_ln_end_dfo_ms,-1,-1;asset_id \"asset_id\" true false false 4 Long 0 10 ,First,#," + template_ctrl_sect_asset_lyr + ",asset_id,-1,-1;asset_value_cd \"asset_value_cd\" true true false 4 Long 0 10 ,First,#," + template_ctrl_sect_asset_lyr + ",asset_value_cd,-1,-1;asset_value_desc \"asset_value_desc\" true true false 255 Text 0 0 ,First,#," + template_ctrl_sect_asset_lyr + ",asset_value_desc,-1,-1;asset_type_desc \"asset_type_desc\" true true false 255 Text 0 0 ,First,#," + template_ctrl_sect_asset_lyr + ",asset_type_desc,-1,-1;ctrl_sect_nbr \"ctrl_sect_nbr\" true true false 7 Text 0 0 ,First,#," + template_ctrl_sect_asset_lyr + ",ctrl_sect_nbr,-1,-1;bmp \"bmp\" true false false 8 Double 8 38 ,First,#," + template_ctrl_sect_asset_lyr + ",bmp,-1,-1;emp \"emp\" true false false 8 Double 8 38 ,First,#," + template_ctrl_sect_asset_lyr + ",emp,-1,-1;gid \"gid\" true false false 4 Long 0 10 ,First,#," + template_ctrl_sect_asset_lyr + ",gid,-1,-1;hwy_name \"hwy_name\" true true false 50 Text 0 0 ,First,#," + template_ctrl_sect_asset_lyr + ",hwy_name,-1,-1;dfo_len \"dfo_len\" true false false 8 Double 8 38 ,First,#," + template_ctrl_sect_asset_lyr + ",dfo_len,-1,-1;factor \"factor\" true true false 8 Double 8 38 ,First,#," + template_ctrl_sect_asset_lyr + ",factor,-1,-1;st_length_shape_ \"st_length_shape_\" false false true 0 Double 0 0 ,First,#," + template_ctrl_sect_asset_lyr + ",shape_Length,-1,-1", "")

    log_message = "################### Begin Asset/Event Transformation ###################"
    logger.info(log_message)

    if assetgroup.index(assetgroup[-1]) > 0:

        assetgroup.pop(0)  ## remove the first list item, which is either 'lrm' or '#'
        strAsset = ""

        for asset in assetgroup:

            event_tbl = os.path.join(tcEvents_gdb, asset)
            counting = arcpy.GetCount_management(event_tbl)

            log_message = "Overlaying Control Sections with " + event_tbl + " by Primary LRM...  "
            logger.info(log_message)

            if arcpy.Exists(asset_traversal_tbl):
                arcpy.Delete_management(asset_traversal_tbl, "Table")
                Delete_succeeded_1 = "true"

            # Process: Overlay Route Events
            arcpy.OverlayRouteEvents_lr(event_tbl, "LRS_RTE_ID LINE ASSET_LN_BEGIN_DFO_MS ASSET_LN_END_DFO_MS",
                                        ctrl_sect_rdbd_tbl, "lrs_rte_id LINE ctrl_sect_ln_begin_dfo_ms ctrl_sect_ln_end_dfo_ms",
                                        "INTERSECT", asset_traversal_tbl, Output_Event_Table_Properties, "NO_ZERO", "FIELDS",
                                        "INDEX")

            log_message = "Calculating Roadbed Length of " + asset_traversal_tbl
            logger.info(log_message)

            # Process: Calculate Field
            arcpy.CalculateField_management(asset_traversal_tbl, "rdbd_len", "!ASSET_LN_END_DFO_MS! - !ASSET_LN_BEGIN_DFO_MS!", "PYTHON_9.3", "")

            if arcpy.Exists(asset_traversal_event):
                arcpy.Delete_management(asset_traversal_event, "Table")
                Delete_succeeded_2 = "true"

            log_message = "Converting asset_traversal_tbl to " + asset_traversal_event
            logger.info(log_message)

            # Process: Table to Table -- This is where Lat/Lon and Temporal Data fields are trimmed out
            arcpy.TableToTable_conversion(asset_traversal_tbl, tcEvents_gdb, "asset_traversal_event", "rdbd_len <> 0", "LRS_RTE_ID \"LRS_RTE_ID\" true true false 20 Text 0 0 ,First,#," + asset_traversal_tbl + ",LRS_RTE_ID,-1,-1;ASSET_LN_BEGIN_DFO_MS \"ASSET_LN_BEGIN_DFO_MS\" true false false 8 Double 3 7 ,First,#," + asset_traversal_tbl + ",ASSET_LN_BEGIN_DFO_MS,-1,-1;ASSET_LN_END_DFO_MS \"ASSET_LN_END_DFO_MS\" true false false 8 Double 3 7 ,First,#," + asset_traversal_tbl + ",ASSET_LN_END_DFO_MS,-1,-1;ASSET_ID \"ASSET_ID\" true false false 4 Long 0 0 ,First,#," + asset_traversal_tbl + ",ASSET_ID,-1,-1;ASSET_VALUE_CD \"ASSET_VALUE_CD\" true true false 4 Long 0 0 ,First,#," + asset_traversal_tbl + ",ASSET_VALUE_CD,-1,-1;ASSET_VALUE_DESC \"ASSET_VALUE_DESC\" true true false 255 Text 0 0 ,First,#," + asset_traversal_tbl + ",ASSET_VALUE_DESC,-1,-1;ASSET_TYPE_DESC \"ASSET_TYPE_DESC\" true true true 255 Text 0 0 ,First,#," + asset_traversal_tbl + ",ASSET_TYPE_DESC,-1,-1;ctrl_sect_ln_nbr \"CTRL_SECT_LN_NBR\" true true false 7 Text 0 0 ,First,#," + asset_traversal_tbl + ",ctrl_sect_ln_nbr,-1,-1;ctrl_sect_ln_begin_mpt_ms \"CTRL_SECT_LN_BEGIN_MPT_MS\" true false false 8 Double 3 7 ,First,#," + asset_traversal_tbl + ",ctrl_sect_ln_begin_mpt_ms,-1,-1;ctrl_sect_ln_end_mpt_ms \"CTRL_SECT_LN_END_MPT_MS\" true false false 8 Double 3 7 ,First,#," + asset_traversal_tbl + ",ctrl_sect_ln_end_mpt_ms,-1,-1;rdbd_gmtry_ln_id \"RDBD_GMTRY_LN_ID\" true false false 4 Long 0 0 ,First,#," + asset_traversal_tbl + ",rdbd_gmtry_ln_id,-1,-1;hname \"HNAME\" true true false 50 Text 0 0 ,First,#," + asset_traversal_tbl + ",hname,-1,-1;rdbd_len \"rdbd_len\" true false false 8 Double 3 7 ,First,#," + asset_traversal_tbl + ",rdbd_len,-1,-1;loc_error \"loc_error\" true true false 50 Text 0 0 ,First,#," + asset_traversal_tbl + ",loc_error,-1,-1;Factor \"Factor\" true true false 8 Double 0 0 ,First,#," + asset_traversal_tbl + ",Factor,-1,-1", "")

            log_message = "Formatting fields in  " + asset_traversal_event + " with MPRME Control Section End Codes to calculate walking milepoints... "
            logger.info(log_message)

            # Process: Alter Field
            arcpy.AlterField_management(asset_traversal_event, "ctrl_sect_ln_nbr", "CTRL_SECT_NBR", "CTRL_SECT_NBR", "", "7", "NON_NULLABLE", "false")

            # Process: Alter Field (2)
            arcpy.AlterField_management(asset_traversal_event, "ctrl_sect_ln_begin_mpt_ms", "BMP", "BMP", "", "8", "NON_NULLABLE", "false")

            # Process: Alter Field (3)
            arcpy.AlterField_management(asset_traversal_event, "ctrl_sect_ln_end_mpt_ms", "EMP", "EMP", "", "8", "NON_NULLABLE", "false")

            # Process: Alter Field (4)
            arcpy.AlterField_management(asset_traversal_event, "rdbd_gmtry_ln_id", "GID", "GID", "", "4", "NON_NULLABLE", "false")

            # Process: Alter Field (5)
            arcpy.AlterField_management(asset_traversal_event, "hname", "HWY_NAME", "HWY_NAME", "", "50", "NON_NULLABLE", "false")

            # Process: Alter Field (6)
            arcpy.AlterField_management(asset_traversal_event, "rdbd_len", "DFO_LEN", "DFO_LEN", "", "8", "NON_NULLABLE", "false")

            # Process: Alter Field (7)
            arcpy.AlterField_management(asset_traversal_event, "loc_error", "LOC_ERR", "LOC_ERR", "", "50", "NON_NULLABLE", "false")

            # Process: Add Field
            arcpy.AddField_management(asset_traversal_event, "ECODE", "TEXT", "", "", "2", "ECODE", "NULLABLE", "NON_REQUIRED", "")

            # Process: Add Field (2)
            arcpy.AddField_management(asset_traversal_event, "hwy_key", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

            # Process: Calculate Field (2)
            arcpy.CalculateField_management(asset_traversal_event, "hwy_key", "calcHwyKey( !HWY_NAME! , !ASSET_LN_END_DFO_MS! )", "PYTHON_9.3", "def calcHwyKey(hwyName, endDFO):\\n    hwy = str(hwyName)\\n    mTxt = str((endDFO * 1000)/1000)\\n    retVal = hwy.rstrip() + '-' + mTxt\\n    return retVal")

            if arcpy.Exists(sort_asset_traversal_event):
                arcpy.Delete_management(sort_asset_traversal_event, "Table")
                Delete_succeeded_3 = "true"

            # Sort asset_traversal_event
            arcpy.Sort_management(asset_traversal_event, sort_asset_traversal_event, "ASSET_TYPE_DESC ASCENDING;LRS_RTE_ID ASCENDING;ASSET_LN_BEGIN_DFO_MS ASCENDING;ASSET_LN_END_DFO_MS ASCENDING", "UR")

            # Process: Join Field
            arcpy.JoinField_management(sort_asset_traversal_event, "hwy_key", mprme, "hwy_key", "erc")

            # Process: Calculate Field (4)
            arcpy.CalculateField_management(sort_asset_traversal_event, "ECODE", "!erc!", "PYTHON_9.3", "")

            # Process: Delete Field
            arcpy.DeleteField_management(sort_asset_traversal_event, "hwy_key;erc")

            log_message = "Field formatting complete in  " + sort_asset_traversal_event
            logger.info(log_message)

            log_message = "Processing Control Section Milepoints ..."
            logger.info(log_message)

            prevRowID = 0
            prevCS_NBR = None
            prevEMP = None
            prevBMP = None
            prevEDFO = None
            prevBDFO = None
            assetTypeDscr = None
            currAssetType = None
            myRow = None

            # Create walking milepoints for the event, according to the Control Section End Code.
            LRM = arcpy.da.UpdateCursor(sort_asset_traversal_event, ["OBJECTID", "ASSET_TYPE_DESC", "CTRL_SECT_NBR", "BMP", "EMP", "ASSET_LN_BEGIN_DFO_MS", "ASSET_LN_END_DFO_MS", "DFO_LEN", "Factor", "ECODE"], None, None, "False", (None, None))
            for myRow in LRM:
                currentRowID, currAssetType, currentCS_NBR, currentBMP, currentEMP, currentBDFO, currentEDFO, currentDFOLEN, currentFac, currentCode = myRow[0], myRow[1], myRow[2], myRow[3], myRow[4], myRow[5], myRow[6], myRow[7], myRow[8], myRow[9]
                currentFacLEN = ((currentDFOLEN * currentFac) * 1000)/1000
                assetTypeDscr = currAssetType
                if (prevCS_NBR == currentCS_NBR):
                    ## Update
                    if (prevEMP == None):
                        pass
                    else:
                        ## this is the same control section but not the first pass
                        if (currentCode == 'CE' or currentCode == 'E' or currentCode == 'CQ' or currentCode == 'Q'):
                            # this is the last record of the control section
                            ## BMP:  carries in and applies the previous EMP as the current records BMP; no update to EMP.
                            if (currentBDFO == prevEDFO):
                                # Update:
                                myRow[3] = prevEMP
                                LRM.updateRow(myRow)
                            else:
                                pass
                        else:
                            ## BMP:  carries in and applies the previous EMP as the current records BMP.
                            ## EMP:  adds Factor_LEN to the updated current BMP to return the new EMP
                            currentEMP = prevEMP + currentFacLEN
                            # Update:
                            myRow[3] = prevEMP
                            myRow[4] = currentEMP
                            LRM.updateRow(myRow)
                else:
                    # this is the next control section
                    if (currentCode == 'CE' or currentCode == 'E' or currentCode == 'CQ' or currentCode == 'Q'):
                        # this is the only record of the control section
                        pass
                    else:
                        currentEMP = currentBMP + currentFacLEN
                        # Update:
                        myRow[4] = currentEMP
                        LRM.updateRow(myRow)
                ## Prepare for looping
                prevCS_NBR = currentCS_NBR
                prevRowID = currentRowID
                prevEMP = currentEMP
                prevBMP = currentBMP
                prevEDFO = currentEDFO
                prevBDFO = currentBDFO

            strAsset = currAssetType
            del myRow
            del LRM

            log_message = "Milepoint Processing Complete."
            logger.info(log_message)

            log_message = "Begin Dynamic Segmentation of results ..."
            logger.info(log_message)

            # Process: Delete Field
            arcpy.DeleteField_management(sort_asset_traversal_event, "LOC_ERR;ECODE")

            if arcpy.Exists(asset_traversal_events):
                arcpy.Delete_management(asset_traversal_events, "in_memory")
                Delete_succeeded_3 = "true"

            # Process: Make Route Event Layer
            arcpy.MakeRouteEventLayer_lr(ctrl_sect_rdbd_m, "lrs_rte_id", sort_asset_traversal_event, "LRS_RTE_ID LINE ASSET_LN_BEGIN_DFO_MS ASSET_LN_END_DFO_MS", asset_traversal_events, "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

            log_message = "Dynamic Segmentation complete."
            logger.info(log_message)

            if arcpy.Exists(ctrl_sect_assets):
                arcpy.Delete_management(ctrl_sect_assets, "FeatureClass")
                Delete_succeeded_4 = "true"

            log_message = "Copy Routed Event to " + arcpy.env.workspace
            logger.info(log_message)

            # Process: Copy Features
            arcpy.CopyFeatures_management(asset_traversal_events, ctrl_sect_assets, "", "0", "0", "0")

            if arcpy.Exists(sort_ctrl_sect_asset_lyr):
                arcpy.Delete_management(sort_ctrl_sect_asset_lyr, "FeatureClass")
                Delete_succeeded_5 = "true"

            log_message = "Sorting " + ctrl_sect_assets + " ..."
            logger.info(log_message)

            if assetTypeDscr == 'Future AADT':
                # Process: Alt. Sort required for the dependency on the data date (in ASSET_VALUE_CD) with FUT_AADT:
                arcpy.Sort_management(ctrl_sect_assets, sort_ctrl_sect_asset_lyr, "ASSET_VALUE_CD ASCENDING;LRS_RTE_ID ASCENDING;ASSET_LN_BEGIN_DFO_MS ASCENDING", "UR")

            elif assetTypeDscr == 'Current AADT':

                if arcpy.Exists(aadt_ctrl_sect_asset_lyr):
                    arcpy.Delete_management(aadt_ctrl_sect_asset_lyr, "FeatureClass")
                    Delete_succeeded_6 = "true"

                # Process: GRID has excessive record breaks on CUR AADT, due to its mis-application of ASSET_ID.  This makes the GISDWH Load operation unstable in the current AWS environment, thus this extra processing is applied to compress/remove this excessive record breaks:
                arcpy.Sort_management(ctrl_sect_assets, aadt_ctrl_sect_asset_lyr, "LRS_RTE_ID ASCENDING;ASSET_LN_BEGIN_DFO_MS ASCENDING;ASSET_LN_END_DFO_MS ASCENDING", "UR")

                if arcpy.Exists(aadt_ctrl_sect_asset_dissolve):
                    arcpy.Delete_management(aadt_ctrl_sect_asset_dissolve, "FeatureClass")
                    Delete_succeeded_7 = "true"

                log_message = "Alt. Processing for Current AADT: Dissolving " + aadt_ctrl_sect_asset_lyr + " ..."
                logger.info(log_message)

                # Process: Dissolve
                arcpy.Dissolve_management(aadt_ctrl_sect_asset_lyr, aadt_ctrl_sect_asset_dissolve, "LRS_RTE_ID;ASSET_VALUE_CD;ASSET_VALUE_DESC;ASSET_TYPE_DESC;CTRL_SECT_NBR;GID;HWY_NAME", "ASSET_LN_BEGIN_DFO_MS FIRST;ASSET_LN_END_DFO_MS LAST;ASSET_ID FIRST;BMP FIRST;EMP LAST;DFO_LEN SUM;Factor FIRST;Shape_Length SUM", "MULTI_PART", "DISSOLVE_LINES")

                if arcpy.Exists(format_ctrl_sect_asset_lyr):
                    arcpy.Delete_management(format_ctrl_sect_asset_lyr, "FeatureClass")
                    Delete_succeeded_8 = "true"

                log_message = "Converting and formating results to: " + format_ctrl_sect_asset_lyr + " ..."
                logger.info(log_message)

                # Process: Feature Class to Feature Class
                arcpy.FeatureClassToFeatureClass_conversion(aadt_ctrl_sect_asset_dissolve, dcEvents_gdb, "format_ctrl_sect_asset_lyr", "", "LRS_RTE_ID \"LRS_RTE_ID\" true true false 20 Text 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",LRS_RTE_ID,-1,-1;ASSET_LN_BEGIN_DFO_MS \"ASSET_LN_BEGIN_DFO_MS\" true true false 8 Double 3 7 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",FIRST_ASSET_LN_BEGIN_DFO_MS,-1,-1;ASSET_LN_END_DFO_MS \"ASSET_LN_END_DFO_MS\" true true false 8 Double 3 7 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",LAST_ASSET_LN_END_DFO_MS,-1,-1;ASSET_ID \"ASSET_ID\" true true false 4 Long 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",FIRST_ASSET_ID,-1,-1;ASSET_VALUE_CD \"ASSET_VALUE_CD\" true true false 4 Long 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",ASSET_VALUE_CD,-1,-1;ASSET_VALUE_DESC \"ASSET_VALUE_DESC\" true true false 255 Text 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",ASSET_VALUE_DESC,-1,-1;ASSET_TYPE_DESC \"ASSET_TYPE_DESC\" true true false 255 Text 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",ASSET_TYPE_DESC,-1,-1;CTRL_SECT_NBR \"CTRL_SECT_NBR\" true true false 7 Text 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",CTRL_SECT_NBR,-1,-1;BMP \"BMP\" true true false 8 Double 3 5 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",FIRST_BMP,-1,-1;EMP \"EMP\" true true false 8 Double 3 5 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",LAST_EMP,-1,-1;GID \"GID\" true false false 4 Long 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",GID,-1,-1;HWY_NAME \"HWY_NAME\" true true false 50 Text 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",HWY_NAME,-1,-1;DFO_LEN \"DFO_LEN\" true true false 8 Double 3 7 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",SUM_DFO_LEN,-1,-1;Factor \"Factor\" true true false 8 Double 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",FIRST_Factor,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + aadt_ctrl_sect_asset_dissolve + ",Shape_Length,-1,-1", "")

                log_message = "Resorting Current AADT Results to: " + sort_ctrl_sect_asset_lyr + " ..."
                logger.info(log_message)

                # Process: Sort (2)
                arcpy.Sort_management(format_ctrl_sect_asset_lyr, sort_ctrl_sect_asset_lyr, "LRS_RTE_ID ASCENDING;ASSET_LN_BEGIN_DFO_MS ASCENDING;ASSET_LN_END_DFO_MS ASCENDING", "UR")

            else:
                # Process: Sort
                arcpy.Sort_management(ctrl_sect_assets, sort_ctrl_sect_asset_lyr, "LRS_RTE_ID ASCENDING;ASSET_LN_BEGIN_DFO_MS ASCENDING", "UR")

            log_message = "Append Routed Event to " + lrs_ctrl_sect_asset_lyr
            logger.info(log_message)

            # Process: Append to local lrs_ctrl_sect_asset_lyr
            arcpy.Append_management(sort_ctrl_sect_asset_lyr, lrs_ctrl_sect_asset_lyr, "NO_TEST", "lrs_rte_id \"LRS_RTE_ID\" true true false 20 Text 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",LRS_RTE_ID,-1,-1;asset_ln_begin_dfo_ms \"ASSET_LN_BEGIN_DFO_MS\" true false false 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",ASSET_LN_BEGIN_DFO_MS,-1,-1;asset_ln_end_dfo_ms \"ASSET_LN_END_DFO_MS\" true false false 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",ASSET_LN_END_DFO_MS,-1,-1;asset_id \"ASSET_ID\" true false false 4 Long 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",ASSET_ID,-1,-1;asset_value_cd \"ASSET_VALUE_CD\" true true false 4 Long 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",ASSET_VALUE_CD,-1,-1;asset_value_desc \"ASSET_VALUE_DESC\" true true false 255 Text 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",ASSET_VALUE_DESC,-1,-1;asset_type_desc \"ASSET_TYPE_DESC\" true true false 255 Text 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",ASSET_TYPE_DESC,-1,-1;ctrl_sect_nbr \"CTRL_SECT_NBR\" true true false 7 Text 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",CTRL_SECT_NBR,-1,-1;bmp \"BMP\" true false false 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",BMP,-1,-1;emp \"EMP\" true false false 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",EMP,-1,-1;gid \"GID\" true false false 4 Long 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",GID,-1,-1;hwy_name \"HWY_NAME\" true true false 50 Text 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",HWY_NAME,-1,-1;dfo_len \"DFO_LEN\" true false false 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",DFO_LEN,-1,-1;factor \"Factor\" true true false 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",Factor,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + sort_ctrl_sect_asset_lyr + ",Shape_Length,-1,-1", "")

            eventFlag = True

            log_message = "################### " + strAsset + " Transformation Complete ###################"
            logger.info(log_message)

    if eventFlag == True:

        log_message = "Asset/Event Transformation and Load Update Completed Successfully"
        logger.info(log_message)

    elif assetgroup[0] == 'lrm':

        log_message = "Asset/Event Transformation Omitted - Only LRS Data Updated"
        logger.info(log_message)

    else:
        log_message = "Asset/Event Transformation Omitted - No Data Updated"
        logger.info(log_message)

    return "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SOE Dataset ETL Complete %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

def defineParams(pList, s):
    strBuilder = ""
    i = 0
    for p in pList:
        if p == 'los':
            # strBuilder = "'Functional System', 'Lane Width', 'Number Thru Lanes', 'Frontage Number Thru Lanes', 'HOV Lanes'"
            strBuilder = "'Functional System'"
        elif p == 'des':
            pass
            # if i == 0:
            #     strBuilder += "'Roadbed Surface Type', 'Frontage Roadbed Surface Type', 'Roadway Design', 'Frontage Roadway Design'"
            #     # strBuilder += "'Roadway Design'"
            # else:
            #     strBuilder += ", 'Roadbed Surface Type', 'Frontage Roadbed Surface Type', 'Roadway Design', 'Frontage Roadway Design'"
            #     # strBuilder += ", 'Roadway Design'"
        elif p == 'gov':
            if i == 0:
                # strBuilder += "'City', 'City Population', 'Urban Pop Routes', 'MPO Name', 'Texas House District', 'Texas Senate District', 'US House District'"
                strBuilder += "'PA Condition Score', 'PA Distress Score', 'PA Ride Score'"
            else:
                # strBuilder += ", 'City', 'City Population', 'Urban Pop Routes', 'MPO Name', 'Texas House District', 'Texas Senate District', 'US House District'"
                strBuilder += ", 'PA Condition Score', 'PA Distress Score', 'PA Ride Score'"
        elif p == 'trf':
            if i == 0:
                strBuilder += "'Future AADT', 'Percent Truck AADT', 'Current AADT'"
                # strBuilder += "'Current AADT'"
            else:
                strBuilder += ", 'Future AADT', 'Percent Truck AADT', 'Current AADT'"
                # strBuilder += ", 'Current AADT'"
        elif p == 'sec':
            pass
            # if i == 0:
            #     # strBuilder += "'Bicycle Route', 'NHS', 'TX Trunk System', 'Evacuation Route', 'Hazardous Route', 'FHWA Freight Network', 'TxDOT Freight Network', 'Energy Sector Route'"
            #     strBuilder += ""
            # else:
            #     # strBuilder += ", 'Bicycle Route', 'NHS', 'TX Trunk System', 'Evacuation Route', 'Hazardous Route', 'FHWA Freight Network', 'TxDOT Freight Network', 'Energy Sector Route'"
            #     strBuilder += ""
        i += 1

    return strBuilder


if __name__ == '__main__':

    gisdwh = ""
    mxd_data_path = ""
    Target_Env = arcpy.GetParameterAsText(1)
    if Target_Env == '#' or not Target_Env:
        Exception("Target environment required as second parameter")  # provide a default value if unspecified
        exit()
    elif Target_Env == 'dev':
        gisdwh = r"D:\Data\Connections\RDS\GISDW_DEV_STAGING_DATAOWNER.sde"
        # gisdwh = r"D:\Data\Connections\GIS_DWH.sde"  # GISDWH DEV
        mxd_data_path = r"D:\mxd\dev"
    elif Target_Env == 'test':
        gisdwh = r"D:\Data\Connections\txdot4awtgdb1_sde.sde"  # GISDWH TEST
        mxd_data_path = r"D:\mxd\test"
    elif Target_Env == 'prod':
        gisdwh = r"D:\Data\Connections\TXDOT4AWPGDB1_sde.sde"  # \\gis_dw.sde. # GISDWH PROD
        mxd_data_path = r"D:\mxd\prod"
    else:
        Exception("Invalid target environment specified in second parameter")
        exit()

    conn_data_path = r"D:\Projects\GISDWH_ASSETS"
    data_dir_nm = "data"
    local_dir_nm = "local"
    tools_dir_nm = "tools"
    template_gdb_nm = "gisdwhtemplates.gdb"
    asset_data_gdb_nm = "gisdwhassets.gdb"
    workspace_gdb_nm = "tcEvents.gdb"
    intersect_gdb_nm = "Intersect_Tools.gdb"

    # Static Template Source GDB
    data_dir = os.path.join(lrm_data_path, data_dir_nm)
    template_dir = os.path.join(data_dir, local_dir_nm)
    template_gdb = os.path.join(template_dir, template_gdb_nm)  # gisdwhtemplates.gdb

    mxd_dir_nm = "LRS"
    mxd_data_gdb_nm = "LRS_SOE_V2.gdb"

    # Stationary MXD/Service Local Data Store
    mxd_dir = os.path.join(mxd_data_path, mxd_dir_nm)
    mxd_gdb = os.path.join(mxd_dir, mxd_data_gdb_nm)
    localNetStr = str(os.path.join(mxd_gdb, "Network"))  # NAD 83 SWPM Projection (TPP)

    logs_dir_nm = "logs"
    logs_file_nm = "asset_data_log.txt"
    assetgroup = []
    paramgroup = []

    logs_dir = os.path.join(conn_data_path, logs_dir_nm)
    logs_file = os.path.join(logs_dir, logs_file_nm)
    logger = lrm_logging.setup_logging(logs_file)

    result_x = transformEventLRM(gisdwh, localNetStr, conn_data_path, tools_dir_nm, workspace_gdb_nm, data_dir_nm, asset_data_gdb_nm, template_gdb, ListGroups, logger)
    logger.info(result_x)
