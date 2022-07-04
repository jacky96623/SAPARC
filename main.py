"""
This is used to calculate the basic statistics including: Frequency, Mean, Median, Max, Min, SD, Var, Skew, PassingFreq, Pass%, Best6, Best5, 4C2X, 4C1X, 332233+, 33222+, 3322+, 22222+
"""

print("****************************************************************")
print("*   Raimondi College - Student Academic Performance Analysis   *")
print("****************************************************************\n")

# Import Module
print("Importing Module...")

import pandas as pd
from os import path
import pandas_access as mdb
import numpy as np

print("done\n")

# Load DB Data
print("Loading DB Data...")

dbFileFolder = "database"
dataDBFilePath = path.join(dbFileFolder, "data.accdb")
metadataDBFilePath = path.join(dbFileFolder, "metadata.accdb")

dfExamMarkG: pd.DataFrame = mdb.read_table(
    dataDBFilePath, "tbl_ExamMark_G",
    dtype={"GradePass": "Int64", "GradeDSEPoint": "Float64"}
)
dfExamMarkP: pd.DataFrame = mdb.read_table(dataDBFilePath, "tbl_ExamMark_P", low_memory=False)
dfExamMarkS: pd.DataFrame = mdb.read_table(dataDBFilePath, "tbl_ExamMark_S", dtype={"MarkS": "Float64"})
dfCListSubject: pd.DataFrame = mdb.read_table(metadataDBFilePath, "CList_Subject", dtype={"JO": "Int64"})

# REVIEW: why need to delete old data?
# cursor=conn.cursor()
# cursor.execute( "delete * from tbl_ExamStat_STierAll_Pivot")
# cursor.execute( "delete * from tbl_ExamMark_DSE_In")
# cursor.execute( "delete * from tbl_ExamMark_DSE_In_Corr")
# cursor.execute( "delete * from tbl_ExamStat_MarkRange")
# conn.commit()
# cursor.close()
# conn.close()

print("done\n")

# Analyze Data
print("Analyzing Data...")

for i in range(6):
    # print("\n*************************************")
    print(f" --- Calculation Process {i + 1} ---")
    # print("*************************************\n")

    runsql = 1

    if i == 0 and not dfExamMarkS.empty:
        dfStat11 = pd.DataFrame(
            dfExamMarkS.groupby(["YCode", "JCode", "ACode", "CForm"], as_index=False)
            .agg({"MarkS": ["count", "max", "mean", "median", "min", "std", "var", "skew"]})
        )
        dfStat11.columns = [
            "YCode", "JCode", "ACode", "CForm", "Freq", "Max", "Avg", "Median", "Min", "SD", "Variance", "Skewness"
        ]
        # REMARK: To obtain a CSV for dfStat11, run:
        # dfStat11.to_csv("SKEW.csv", index=False, header=True)

        dfStat12 = pd.DataFrame(
            dfExamMarkG.groupby(["YCode", "JCode", "ACode", "CForm"], as_index=False).agg({"GradePass": ["sum"]})
        )
        dfStat12.columns = ["YCode", "JCode", "ACode", "CForm", "PassFreq"]

        dfStat13 = pd.merge(
            dfStat11, dfStat12,
            left_on=["YCode", "JCode", "ACode", "CForm"], right_on=["YCode", "JCode", "ACode", "CForm"]
        )
        dfStat13["Pass%"] = dfStat13["PassFreq"] / dfStat13["Freq"]

        dfStatR = pd.DataFrame(dfExamMarkS[["SCode", "YCode", "JCode", "ACode", "MarkS", "CForm"]])
        dfStatR["Rank"] = dfStatR.groupby(
            ["YCode", "JCode", "ACode", "CForm"]
        )["MarkS"].rank(method="min", ascending=False)
        dfStatR["Rankpc"] = dfStatR[dfStatR["JCode"] != "OMF"].groupby(
            ["YCode", "JCode", "ACode", "CForm"]
        )["MarkS"].rank(method="min", pct=True)
        dfStatR["Rankpc2"] = dfStatR[dfStatR["JCode"] == "OMF"].groupby(
            ["YCode", "JCode", "ACode", "CForm"]
        )["MarkS"].rank(method="min", ascending=False, pct=True)
        dfStatR["Rankpc"] = np.where(dfStatR["JCode"] == "OMF", dfStatR["Rankpc2"], dfStatR["Rankpc"])
        dfStatR["Rank"] = np.where(dfStatR["JCode"] == "OMF", dfStatR["MarkS"], dfStatR["Rank"])

        dfStatZ1 = pd.merge(
            dfExamMarkS, dfStat11,
            left_on=["YCode", "JCode", "ACode", "CForm"], right_on=["YCode", "JCode", "ACode", "CForm"]
        )
        dfStatZ1["Z-Score"] = (dfStatZ1["MarkS"] - dfStatZ1["Avg"]) / dfStatZ1["SD"]
        dfStatZ1 = pd.merge(
            dfStatZ1, dfStatR,
            left_on=["YCode", "JCode", "ACode", "CForm", "SCode"], right_on=["YCode", "JCode", "ACode", "CForm", "SCode"]
        )

        # REMARK: Save for future use?
        dfStatZ1for5 = dfStatZ1

        dfStatMRS = pd.DataFrame(dfExamMarkS[["SCode", "YCode", "JCode", "ACode", "MarkS", "CForm"]])
        dfStatMRS = dfStatMRS.drop_duplicates()

        dfStatMRSRangeStart = 0
        dfStatMRSRangeEnd = 105
        dfStatMRSRangeStep = 5
        # Produce the bin array [0, 5, 10, ..., 100, 105]
        dfStatMRSRangeBins = list(
            range(dfStatMRSRangeStart, dfStatMRSRangeEnd + dfStatMRSRangeStep, dfStatMRSRangeStep)
        )
        # Produce the label array ["  0 ≤ x < 5  ", "  5 ≤ x < 10 ", ..., " 90 ≤ x < 95 ", " 95 ≤ x ≤ 100", "100 ≤ x ≤ 105"]
        dfStatMRSRangeLabels = list(map(
            lambda leftMarg: f'{leftMarg:>3} ≤ x {"≤" if leftMarg >= 95 else "<"} {leftMarg + dfStatMRSRangeStep:<3}',
            range(dfStatMRSRangeStart, dfStatMRSRangeEnd, dfStatMRSRangeStep)
        ))

        dfStatMRS["MarkRange"] = pd.cut(
            dfStatMRS["MarkS"], bins=dfStatMRSRangeBins, labels=dfStatMRSRangeLabels, include_lowest=True, right=False
        )
        dfStatMRS["MarkRange"] = np.where(
            dfStatMRS["MarkRange"] == "100 ≤ x ≤ 105", " 95 ≤ x ≤ 100", dfStatMRS["MarkRange"]
        )
        dfStatMRS["MarkRange"] = np.where(dfStatMRS["JCode"] == "OMF", "", dfStatMRS["MarkRange"])
        dfStatMRS["SCForm"] = "S." + dfStatMRS["CForm"]

        dfStatMRSC = pd.DataFrame(
            dfStatMRS.groupby(
                ["YCode", "JCode", "ACode", "CForm", "SCForm", "MarkRange"], as_index=False
            ).agg({"MarkS": ["count"]})
        )
        dfStatMRSC.columns = ["YCode", "JCode", "ACode", "CForm", "SCForm", "MarkRange", "MarkRangeFreqSum"]

        dfStatMRS1 = pd.DataFrame(dfStatMRSC[["YCode", "JCode", "ACode", "CForm", "SCForm"]])
        dfStatMRS1 = dfStatMRS1.drop_duplicates()

        dfStatMRS2 = dfStatMRSC[dfStatMRSC["MarkRange"] != ""]
        dfStatMRS2 = dfStatMRS2.drop(columns=["YCode", "JCode", "ACode", "CForm", "SCForm", "MarkRangeFreqSum"])
        dfStatMRS2 = dfStatMRS2.drop_duplicates()
        dfStatMRS2["MarkRangeFreqSum"] = 0

        dfStatMRS1["Temp"] = 1
        dfStatMRS2["Temp"] = 1
        dfStatMRS3 = pd.merge(dfStatMRS1, dfStatMRS2, on=["Temp"])
        dfStatMRS3 = dfStatMRS3.drop("Temp", axis=1)

        dfStatMRS4 = pd.concat([dfStatMRSC, dfStatMRS3])

        dfStatMRS5 = pd.DataFrame(dfStatMRS4.groupby(
            ["YCode", "JCode", "ACode", "CForm", "SCForm", "MarkRange"], as_index=False
        ).agg({"MarkRangeFreqSum": ["sum"]}))
        dfStatMRS5.columns = ["YCode", "JCode", "ACode", "CForm", "SCForm", "MarkRange", "MarkRangeFreqSum"]

        dfOutput1 = dfStat13[
            ["YCode", "JCode", "ACode", "CForm", "Freq", "Max", "Avg", "Median", "Min", "SD", "Variance", "PassFreq",
             "Pass%", "Skewness"]
        ]
        dfOutput2 = dfStatZ1[
            ["YCode", "JCode", "ACode", "CForm", "CName", "SCode", "YCodeSel", "CFormSel", "CNameSel", "Z-Score",
             "Rank", "Rankpc"]
        ]
        dfOutput3 = dfStatMRS5[["YCode", "JCode", "ACode", "CForm", "SCForm", "MarkRange", "MarkRangeFreqSum"]]

        runsql = 3
    elif i == 1 and not dfExamMarkS.empty:
        dfStat11 = pd.DataFrame(
            dfExamMarkS.groupby(["YCode", "JCode", "ACode", "CForm", "CName"], as_index=False)
            .agg({"MarkS": ["count", "max", "mean", "median", "min", "std", "var", "skew"]})
        )
        dfStat11.columns = [
            "YCode", "JCode", "ACode", "CForm", "CName", "Freq", "Max", "Avg", "Median", "Min", "SD", "Variance",
            "Skewness"
        ]

        dfStat12 = pd.DataFrame(
            dfExamMarkG.groupby(["YCode", "JCode", "ACode", "CForm", "CName"], as_index=False)
            .agg({"GradePass": ["sum"]})
        )
        dfStat12.columns = ["YCode", "JCode", "ACode", "CForm", "CName", "PassFreq"]

        dfStat13 = pd.merge(
            dfStat11, dfStat12,
            left_on=["YCode", "JCode", "ACode", "CForm", "CName"],
            right_on=["YCode", "JCode", "ACode", "CForm", "CName"]
        )
        dfStat13["Pass%"] = dfStat13["PassFreq"] / dfStat13["Freq"]

        dfOutput1 = dfStat13[
            ["YCode", "JCode", "ACode", "CForm", "CName", "Freq", "Max", "Avg", "Median", "Min", "SD", "Variance",
             "PassFreq", "Pass%", "Skewness"]
        ]
    elif i == 2 and not dfExamMarkS.empty:
        dfExamMarkG_NoRep = dfExamMarkG[dfExamMarkG["SCodeRep"] == True]
        dfExamMarkS_NoRep = dfExamMarkS[dfExamMarkS["SCodeRep"] == True]

        dfStat11 = pd.DataFrame(
            dfExamMarkS_NoRep.groupby(["YCodeSel", "JCode", "ACode", "CFormSel"], as_index=False)
            .agg({"MarkS": ["count", "max", "mean", "median", "min", "std", "var", "skew"]})
        )
        dfStat11.columns = [
            "YCodeSel", "JCode", "ACode", "CFormSel", "Freq", "Max", "Avg", "Median", "Min", "SD", "Variance",
            "Skewness"
        ]

        dfStat12 = pd.DataFrame(
            dfExamMarkG_NoRep.groupby(["YCodeSel", "JCode", "ACode", "CFormSel"], as_index=False)
            .agg({"GradePass": ["sum"]})
        )
        dfStat12.columns = ["YCodeSel", "JCode", "ACode", "CFormSel", "PassFreq"]

        dfStat13 = pd.merge(
            dfStat11, dfStat12,
            left_on=["YCodeSel", "JCode", "ACode", "CFormSel"], right_on=["YCodeSel", "JCode", "ACode", "CFormSel"]
        )
        dfStat13["Pass%"] = dfStat13["PassFreq"] / dfStat13["Freq"]

        dfStatZ1 = pd.merge(
            dfExamMarkS_NoRep, dfStat11,
            left_on=["YCodeSel", "JCode", "ACode", "CFormSel"], right_on=["YCodeSel", "JCode", "ACode", "CFormSel"]
        )
        dfStatZ1["Z-Score"] = (dfStatZ1["MarkS"] - dfStatZ1["Avg"]) / dfStatZ1["SD"]

        dfOutput1 = dfStat13[
            ["YCodeSel", "JCode", "ACode", "CFormSel", "Freq", "Max", "Avg", "Median", "Min", "SD", "Variance",
             "PassFreq", "Pass%", "Skewness"]
        ]
        dfOutput2 = dfStatZ1[
            ["YCode", "JCode", "ACode", "CForm", "CName", "SCode", "YCodeSel", "CFormSel", "CNameSel", "Z-Score"]
        ]

        runsql = 2
    elif i == 3 and not dfExamMarkS.empty:
        dfExamMarkG_NoRep = dfExamMarkG[dfExamMarkG["SCodeRep"] == True]
        dfExamMarkS_NoRep = dfExamMarkS[dfExamMarkS["SCodeRep"] == True]

        dfStat11 = pd.DataFrame(
            dfExamMarkS_NoRep.groupby(["YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel"], as_index=False)
            .agg({"MarkS": ["count", "max", "mean", "median", "min", "std", "var", "skew"]})
        )
        dfStat11.columns = [
            "YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel", "Freq", "Max", "Avg", "Median", "Min", "SD",
            "Variance", "Skewness"
        ]

        dfStat12 = pd.DataFrame(
            dfExamMarkG_NoRep.groupby(["YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel"], as_index=False)
            .agg({"GradePass": ["sum"]})
        )
        dfStat12.columns = ["YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel", "PassFreq"]

        dfStat13 = pd.merge(
            dfStat11, dfStat12,
            left_on=["YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel"],
            right_on=["YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel"]
        )
        dfStat13["Pass%"] = dfStat13["PassFreq"] / dfStat13["Freq"]

        dfOutput1 = dfStat13[
            ["YCodeSel", "JCode", "ACode", "CFormSel", "CNameSel", "Freq", "Max", "Avg", "Median", "Min", "SD",
             "Variance", "PassFreq", "Pass%", "Skewness"]
        ]
    elif i == 4:
        dfExamMarkG1 = pd.merge(dfExamMarkG, dfCListSubject, left_on=["JCode"], right_on=["JCode"])
        dfExamMarkG1.set_index(["YCode", "ACode", "SCode"])
        dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1.JSubPaper == False]
        dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1.GradeType == "DSE"]
        dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1.JCode != "M1"]
        dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1.JCode != "M2"]
        # dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1["JSubPaper"] == False]
        # dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1["GradeType"] == "DSE"]
        # dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1["JCode"] != "M1"]
        # dfExamMarkG1 = dfExamMarkG1[dfExamMarkG1["JCode"] != "M2"]
        dfExamMarkG1 = dfExamMarkG1.drop(columns=["YCodeSel", "CFormSel", "CNameSel"])
        dfExamMarkG1 = dfExamMarkG1.drop_duplicates()
        dfExamMarkG1["SortKey"] = dfExamMarkG1["GradeDSEPoint"] * 1000 + dfExamMarkG1["JO"]
        dfExamMarkG1["Sort"] = dfExamMarkG1.groupby(
            ["YCode", "ACode", "CForm", "SCode"]
        )["SortKey"].rank(ascending=False)
        dfExamMarkG1["SortC"] = dfExamMarkG1[
            ~dfExamMarkG1.JCode.isin(["Chi", "Eng", "Maths", "Maths-C", "LS"])
        ].groupby(["YCode", "ACode", "CForm", "SCode"])["SortKey"].rank(ascending=False)
        dfExamMarkG1.loc[dfExamMarkG1.JCode.isin(["Chi", "Eng", "Maths", "Maths-C", "LS"]), "SortC"] = 0

        dfBest6 = dfExamMarkG1[dfExamMarkG1["Sort"] <= 6].groupby(
            ["YCode", "ACode", "SCode"]
        ).agg({"GradeDSEPoint": ["sum"]}).reset_index()
        dfBest6.columns = ["YCode", "ACode", "SCode", "Best6"]

        dfBest5 = dfExamMarkG1[dfExamMarkG1["Sort"] <= 5].groupby(
            ["YCode", "ACode", "SCode"]
        ).agg({"GradeDSEPoint": ["sum"]}).reset_index()
        dfBest5.columns = ["YCode", "ACode", "SCode", "Best5"]

        dfBest4C2X = dfExamMarkG1[dfExamMarkG1["SortC"] <= 2].groupby(
            ["YCode", "ACode", "SCode"]
        ).agg({"GradeDSEPoint": ["sum"]}).reset_index()
        dfBest4C2X.columns = ["YCode", "ACode", "SCode", "4C2X"]

        dfBest4C1X = dfExamMarkG1[dfExamMarkG1["SortC"] <= 1].groupby(
            ["YCode", "ACode", "SCode"]
        ).agg({"GradeDSEPoint": ["sum"]}).reset_index()
        dfBest4C1X.columns = ["YCode", "ACode", "SCode", "4C1X"]

        dfPassCheckC3E3Count = dfExamMarkG1[
            (dfExamMarkG1.JCode.isin(["Chi", "Eng"])) & (dfExamMarkG1.GradeDSEPoint >= 3)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckC3E3Count.columns = ["YCode", "ACode", "SCode", "C3E3_Count"]

        dfPassCheckC2E2Count = dfExamMarkG1[
            (dfExamMarkG1.JCode.isin(["Chi", "Eng"])) & (dfExamMarkG1.GradeDSEPoint >= 2)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckC2E2Count.columns = ["YCode", "ACode", "SCode", "C2E2_Count"]

        dfPassCheckM2L2Count = dfExamMarkG1[
            (dfExamMarkG1.JCode.isin(["Maths", "Maths-C", "LS"])) & (dfExamMarkG1.GradeDSEPoint >= 2)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckM2L2Count.columns = ["YCode", "ACode", "SCode", "M2L2_Count"]

        dfPassCheckX3X3Count = dfExamMarkG1[
            (~dfExamMarkG1.JCode.isin(["Chi", "Eng", "Maths", "Maths-C", "LS"])) & (dfExamMarkG1.GradeDSEPoint >= 3)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckX3X3Count.columns = ["YCode", "ACode", "SCode", "X3X3_Count"]

        dfPassCheckX4Count = dfExamMarkG1[
            (~dfExamMarkG1.JCode.isin(["Chi", "Eng", "Maths", "Maths-C", "LS"])) & (dfExamMarkG1.GradeDSEPoint >= 4)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckX4Count.columns = ["YCode", "ACode", "SCode", "X4_Count"]

        dfPassCheckX2Count = dfExamMarkG1[
            (~dfExamMarkG1.JCode.isin(["Chi", "Eng", "Maths", "Maths-C", "LS"])) & (dfExamMarkG1.GradeDSEPoint >= 2)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckX2Count.columns = ["YCode", "ACode", "SCode", "X2_Count"]

        dfPassCheckHDX2X2X2Count = dfExamMarkG1[
            (~dfExamMarkG1.JCode.isin(["Chi", "Eng"])) & (dfExamMarkG1.GradeDSEPoint >= 2)
        ].groupby(["YCode", "ACode", "SCode"]).agg({"GradeDSEPoint": ["count"]}).reset_index()
        dfPassCheckHDX2X2X2Count.columns = ["YCode", "ACode", "SCode", "HDX2X2X2_Count"]

        dfPassCheckList = [
            dfBest6, dfBest5, dfBest4C2X, dfBest4C1X, dfPassCheckC3E3Count, dfPassCheckC2E2Count, dfPassCheckM2L2Count,
            dfPassCheckX3X3Count, dfPassCheckX2Count, dfPassCheckHDX2X2X2Count, dfPassCheckX4Count
        ]

        dfPassCheckF = dfExamMarkG.drop(
            columns=["JCode", "MarkG", "GradePass", "GradeType", "GradeDSEPoint", "GradePriority"]
        )
        dfPassCheckF = dfPassCheckF.drop_duplicates()
        for passcheck in dfPassCheckList:
            dfPassCheckF = pd.merge(dfPassCheckF, passcheck, how="left", on=["YCode", "ACode", "SCode"])
        dfPassCheckF = pd.DataFrame(dfPassCheckF)
        dfPassCheckF = dfPassCheckF.replace(np.nan, 0, regex=True)
        dfPassCheckF.fillna(0)
        dfPassCheckF["332233+"] = ((dfPassCheckF["C3E3_Count"] == 2) &
                                   (dfPassCheckF["M2L2_Count"] == 2) & (dfPassCheckF["X3X3_Count"] >= 2))
        dfPassCheckF["33222+"] = ((dfPassCheckF["C3E3_Count"] == 2) &
                                  (dfPassCheckF["M2L2_Count"] == 2) & (dfPassCheckF["X2_Count"] >= 1))
        dfPassCheckF["3322+"] = ((dfPassCheckF["C3E3_Count"] == 2) & (dfPassCheckF["M2L2_Count"] == 2))
        dfPassCheckF["22222+"] = ((dfPassCheckF["C2E2_Count"] == 2) & (dfPassCheckF["HDX2X2X2_Count"] >= 3))
        dfPassCheckF["332222+"] = ((dfPassCheckF["C3E3_Count"] == 2) &
                                   (dfPassCheckF["M2L2_Count"] == 2) & (dfPassCheckF["X2_Count"] >= 2))
        dfPassCheckF["33224+"] = ((dfPassCheckF["C3E3_Count"] == 2) &
                                  (dfPassCheckF["M2L2_Count"] == 2) & (dfPassCheckF["X4_Count"] >= 1))
        dfPassCheckF["332244+"] = ((dfPassCheckF["C3E3_Count"] == 2) &
                                   (dfPassCheckF["M2L2_Count"] == 2) & (dfPassCheckF["X4_Count"] >= 2))

        dfOutput1 = dfPassCheckF[
            ["YCode", "ACode", "SCode", "CForm", "CName", "YCodeSel", "CFormSel", "CNameSel", "Best6", "Best5", "4C2X",
             "4C1X", "332233+", "33222+", "3322+", "22222+", "332222+", "33224+", "332244+"]
        ]
        dfOutput1.set_index([
            "YCode", "ACode", "SCode", "CForm", "CName", "YCodeSel", "CFormSel", "CNameSel", "Best6", "Best5", "4C2X",
            "4C1X", "332233+", "33222+", "3322+", "22222+", "332222+", "33224+", "332244+"
        ])
    elif i == 5 and not dfExamMarkS.empty and not dfExamMarkG.empty and not dfExamMarkG[dfExamMarkG["ACode"].str[-5:] == "HKDSE"].empty:
        # This Step Generates Data to Compare DSE Results and Internal Assessments

        dfDSE = dfExamMarkG[dfExamMarkG["ACode"].str[-5:] == "HKDSE"]
        dfDSE = dfDSE.replace("Maths-C", "Maths")
        dfDSE = dfDSE.drop(["YCodeSel", "CFormSel", "CNameSel", "SCodeRep"], axis=1)

        dfGIn = dfExamMarkG
        dfGIn = dfGIn.replace("Maths-C", "Maths")
        dfGIn = dfGIn.drop(["YCodeSel", "CFormSel", "CNameSel", "SCodeRep"], axis=1)

        dfSIn = dfExamMarkS
        dfSIn = dfSIn.replace("Maths-C", "Maths")
        dfSIn = dfSIn.drop(["YCodeSel", "CFormSel", "CNameSel", "SCodeRep"], axis=1)

        dfZIn = dfStatZ1for5[["YCode", "JCode", "ACode", "CForm", "CName", "SCode", "Z-Score"]]
        dfZIn = dfZIn.replace("Maths-C", "Maths")
        # REMARK: dfZIn["Z-Score"] = dfZIn.round({"Z-Score":6})

        dfIn = pd.merge(
            dfGIn, dfSIn,
            left_on=["SCode", "YCode", "JCode", "ACode", "CForm", "CName"],
            right_on=["SCode", "YCode", "JCode", "ACode", "CForm", "CName"]
        )
        dfIn = pd.merge(
            dfIn, dfZIn,
            left_on=["SCode", "YCode", "JCode", "ACode", "CForm", "CName"],
            right_on=["SCode", "YCode", "JCode", "ACode", "CForm", "CName"]
        )
        dfIn = dfIn.rename(columns={
            "YCode": "YCodeIn", "ACode": "ACodeIn", "CForm": "CFormIn", "CName": "CNameIn", "GradePass": "GradePassIn",
            "GradePriority": "GradePriorityIn", "GradeType": "GradeTypeIn", "GradeDSEPoint": "GradeDSEPointIn"
        })
        dfDSE = dfDSE.rename(columns={
            "YCode": "YCodeDSE", "ACode": "ACodeDSE", "CForm": "CFormDSE", "CName": "CNameDSE", "MarkG": "MarkDSE"
        })

        dfDSEIn = pd.merge(dfDSE, dfIn, left_on=["JCode", "SCode"], right_on=["JCode", "SCode"])

        print("----- dfIn -----")
        print(dfIn)
        print("----- dfDSE -----")
        print(dfDSE)
        print("----- dfDSEIn -----")
        print(dfDSEIn)

        dfDSEIn.columns = [
            "SCode", "YCodeDSE", "JCode", "ACodeDSE", "MarkDSE", "CFormDSE", "CNameDSE", "GradePass", "GradePriority",
            "GradeType", "GradeDSEPoint", "YCodeIn", "ACodeIn", "MarkG", "CFormIn", "CNameIn", "GradePassIn",
            "GradePriorityIn", "GradeTypeIn", "GradeDSEPointIn", "MarkS", "Z-Score"
        ]

        dfOutput1 = dfDSEIn.fillna(np.nan).replace([np.nan], [None])
        dfOutput1.set_index([
            "SCode", "YCodeDSE", "JCode", "ACodeDSE", "MarkDSE", "CFormDSE", "CNameDSE", "GradePass", "GradePriority",
            "GradeType", "GradeDSEPoint", "YCodeIn", "ACodeIn", "MarkG", "CFormIn", "CNameIn", "GradePassIn",
            "GradePriorityIn", "GradeTypeIn", "GradeDSEPointIn", "MarkS", "Z-Score"
        ])

        dfDSEInCorrGG = dfDSEIn.groupby(["JCode", "ACodeDSE", "ACodeIn"]).apply(
            lambda dfDSEInGp: dfDSEInGp["GradeDSEPoint"].astype('float64').corr(
                dfDSEInGp["GradeDSEPointIn"].astype('float64')
            )
        )
        dfDSEInCorrSG = dfDSEIn.groupby(["JCode", "ACodeDSE", "ACodeIn"]).apply(
            lambda dfDSEInGp: dfDSEInGp["GradeDSEPoint"].astype('float64').corr(dfDSEInGp["MarkS"].astype('float64'))
        )

        dfOutput2 = pd.DataFrame(dfDSEInCorrGG)
        dfOutput2 = dfOutput2.fillna(np.nan).replace([np.nan], [None])

        dfOutput2 = dfOutput2.reset_index()
        dfOutput2 = dfOutput2.rename(columns={0: "DSEInCorrR"})
        dfOutput2.set_index(["JCode", "ACodeDSE", "ACodeIn", "DSEInCorrR"])
        dfOutput2["MarkType"] = "G"

        dfOutput3 = pd.DataFrame(dfDSEInCorrSG)
        dfOutput3 = dfOutput3.fillna(np.nan).replace([np.nan], [None])
        dfOutput3 = dfOutput3.reset_index()
        dfOutput3 = dfOutput3.rename(columns={0: "DSEInCorrR"})
        dfOutput3.set_index(["JCode", "ACodeDSE", "ACodeIn", "DSEInCorrR"])
        dfOutput3["MarkType"] = "S"

        print(dfOutput2)
        print("-----")
        print(dfOutput3)

        runsql = 3
    elif i > 6:
        break

    # # print("*************************************")
    # # print(f" --- Round The Numbers {i + 1} ---")
    # # print("*************************************")
    # # print(" ")
    # print(" --- Round The Numbers ---")

    # REVIEW: need to save to DB?
    # """
    # pyodbc and Access DB Connection - Python Marketer
    # https://pythonmarketer.com/2019/11/30/inserting-new-records-into-a-microsoft-access-database-with-python/ 
    # """
    # def df_to_access(x):
    #     """
    #     use list comprehension to format df rows as a list of tuples. 
    #     rows = [("email@gmail.com", "2019-12-04","Clean"),("email2@gmail.com", "2019-12-01","Junk")] 
    #     """
    #     df_2_a = x.round(decimals=4)
    #     "df_2_a = df_2_a.replace(np.nan, "" , regex=True)"
    #     "df_2_a.fillna("")"
    #     rows = [tuple(cell) for cell in df_2_a.values]
    #     return rows

    # # print("*************************************")
    # # print(f" --- Save to Database (accdb) {i + 1} --- ")
    # # print("*************************************")
    # # print(" ")
    # print(" --- Save to Database --- ")

    # conn1 = pyodbc.connect(
    #     r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\LamPatrick\Teaching\Software New\Python\SAPARC_Python.accdb;")
    # cursor = conn1.cursor()

    # if i == 0 and not dfExamMarkS.empty:
    #     sql = "INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    #     sql2 = "INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,CName,SCode,YCodeSel,CFormSel,CNameSel,[Z-Score],Rank,Rankpc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    #     sql3 = "INSERT INTO tbl_ExamStat_MarkRange (YCode,JCode,ACode,CForm,SCForm,MarkRange,MarkRangeFreqSum) VALUES (?,?,?,?,?,?,?)"
    # elif i == 1 and not dfExamMarkS.empty:
    #     sql = "INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,CName,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    # elif i == 2 and not dfExamMarkS.empty:
    #     sql = "INSERT INTO tbl_ExamStat_STierAll_Pivot (YCodeSel,JCode,ACode,CFormSel,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    #     sql2 = "INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,CName,SCode,YCodeSel,CFormSel,CNameSel,[Z-Score]) VALUES (?,?,?,?,?,?,?,?,?,?)"
    # elif i == 3 and not dfExamMarkS.empty:
    #     sql = "INSERT INTO tbl_ExamStat_STierAll_Pivot (YCodeSel,JCode,ACode,CFormSel,CNameSel,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    # elif i == 4:
    #     sql = "Insert Into tbl_ExamStat_STierAll_Pivot (YCode,ACode,SCode,CForm,CName,YCodeSel,CFormSel,CNameSel,Best6,Best5,4C2X,4C1X,[332233+],[33222+],[3322+],[22222+],[332222+],[33224+],[332244+]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    # elif i == 5 and not dfExamMarkS.empty and not dfExamMarkG.empty:
    #     sql = "Insert Into tbl_ExamMark_DSE_In (SCode,YCodeDSE,JCode,ACodeDSE,MarkDSE,CFormDSE,CNameDSE,GradePass,GradePriority,GradeType,GradeDSEPoint,YCodeIn,ACodeIn,MarkG,CFormIn,CNameIn,GradePassIn,GradePriorityIn,GradeTypeIn,GradeDSEPointIn,MarkS,[Z-Score]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    #     sql2 = "Insert Into tbl_ExamMark_DSE_In_Corr(JCode,ACodeDSE,ACodeIn,DSEInCorrR,MarkType) VALUES (?,?,?,?,?)"
    #     sql3 = "Insert Into tbl_ExamMark_DSE_In_Corr(JCode,ACodeDSE,ACodeIn,DSEInCorrR,MarkType) VALUES (?,?,?,?,?)"

    # if (0 <= i and i <= 3 and not dfExamMarkS.empty) or (i == 4) or (i == 5 and not dfExamMarkS.empty and not dfExamMarkG.empty and not dfExamMarkG[dfExamMarkG["ACode"].str[-5:] == "HKDSE"].empty):
    #     for runsqlx in range(runsql):
    #         if runsqlx == 0:
    #             d2acursor = dfOutput1
    #             sqlcursor = sql
    #         elif runsqlx == 1:
    #             d2acursor = dfOutput2
    #             sqlcursor = sql2
    #         elif runsqlx == 2:
    #             d2acursor = dfOutput3
    #             sqlcursor = sql3

    #         rows = df_to_access(d2acursor)
    #         row_in_check = 1
    #         for row in rows:
    #             if (row_in_check == 1) or (row_in_check % (10**int(np.math.log(row_in_check, 10))) == 0):
    #                 print("Saving Record  #" + str(row_in_check))
    #                 print(row)
    #             row_in_check = row_in_check + 1
    #             conn1.execute(sqlcursor, row)
    #             conn1.commit()
    # conn1.close()
