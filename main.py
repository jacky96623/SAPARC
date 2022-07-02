"""
This is used to calcuate the basic statistics.
Including Frequencey, Mean, Median, Max, Min, SD, Var, Skew, PassingFreq, Pass%
Including Best6, Best5, 4C2X, 4C1X, 332233+, 33222+, 3322+, 22222+
"""

print("****************************************")
print("*                SAPARC                *")
print("****************************************\n")

print("Importing Module...")
# import pyodbc
import pandas_access as mdb
pd = mdb.pd
# import pandas as pd
# import numpy as np
# from scipy.stats import stats
# import math
# import os
print("done\n")

print("Loading DB Data...")
dataDBFilePath = "database/data.accdb"
metadataDBFilePath = "database/metadata.accdb"
# df_tbl_ExamMark_G = pd.read_sql( "select * from tbl_ExamMark_G", conn)
# df_tbl_ExamMark_P = pd.read_sql( "select * from tbl_ExamMark_P", conn)
# df_tbl_ExamMark_S = pd.read_sql( "select * from tbl_ExamMark_S", conn)
# df_clist_Subject = pd.read_sql( "select * from clist_subject", conn)
# TODO: til here
df_tbl_ExamMark_G = mdb.read_table(dataDBFilePath, "tbl_ExamMark_G", dtype={ 'GradeDSEPoint': 'Float64' })
df_tbl_ExamMark_P = mdb.read_table(dataDBFilePath, "tbl_ExamMark_P", low_memory=False)
df_tbl_ExamMark_S = mdb.read_table(dataDBFilePath, "tbl_ExamMark_S")
df_clist_Subject = mdb.read_table(dataDBFilePath, "clist_subject")

print(df_tbl_ExamMark_G)
print(df_tbl_ExamMark_P)
print(df_tbl_ExamMark_S)
print(df_clist_Subject)

raise Exception('tmp')

cursor=conn.cursor()
cursor.execute( "delete * from tbl_ExamMark_Rank")
cursor.execute( "delete * from tbl_ExamStat_STierAll_Pivot")
cursor.execute( "delete * from tbl_ExamMark_DSE_In")
cursor.execute( "delete * from tbl_ExamMark_DSE_In_Corr")
cursor.execute( "delete * from tbl_ExamStat_MarkRange")
conn.commit()
cursor.close()

conn.close()

print("****************************************")
print("Running")
print("****************************************")
print(" ")


for x in range(6):

      print("****************************************")
      print("Calculation Process  ---  " + str(x) + "  ---")
      print("****************************************")
      print(" ")

           
      runsql=1

      if x == 0 and not(df_tbl_ExamMark_S.empty):


            dfstat11=pd.DataFrame(df_tbl_ExamMark_S.groupby(['YCode','JCode','ACode','CForm'],as_index=False).agg({"MarkS":['count','max','mean','median','min','std','var','skew']}))
            dfstat11.columns=['YCode','JCode','ACode','CForm','Freq','Max','Avg', 'Median', 'Min' ,'SD','Variance','Skewness']
            """dfstat11.to_csv(r'D:\LamPatrick\Teaching\Software New\Python\SKEW.csv',index=False,header=True)"""

            dfstat12=pd.DataFrame(df_tbl_ExamMark_G.groupby(['YCode','JCode','ACode','CForm'],as_index=False).agg({"GradePass":['sum']}))
            dfstat12.columns=['YCode','JCode','ACode','CForm','PassFreq']

            dfstat13=pd.merge(dfstat11,dfstat12,left_on=['YCode','JCode','ACode','CForm'],right_on=['YCode','JCode','ACode','CForm'])
            dfstat13['Pass%']=dfstat13['PassFreq']/dfstat13['Freq']

            dfstatZ1=pd.merge(df_tbl_ExamMark_S,dfstat11,left_on=['YCode','JCode','ACode','CForm'],right_on=['YCode','JCode','ACode','CForm'])
            dfstatZ1['Z-Score']=(dfstatZ1['MarkS']-dfstatZ1['Avg'])/dfstatZ1['SD']

            dfstatR= pd.DataFrame(df_tbl_ExamMark_S[['SCode','YCode','JCode','ACode','MarkS','CForm']])
            dfstatR['Rank']=dfstatR.groupby(['YCode','JCode','ACode','CForm'])['MarkS'].rank(method='min',ascending=False)
            dfstatR['Rankpc']=dfstatR[dfstatR['JCode']!="OMF"].groupby(['YCode','JCode','ACode','CForm'])['MarkS'].rank(method='min',ascending=True,pct=True)
            dfstatR['Rankpc2']=dfstatR[dfstatR['JCode']=="OMF"].groupby(['YCode','JCode','ACode','CForm'])['MarkS'].rank(method='min',ascending=False,pct=True)
            dfstatR['Rankpc']=np.where(dfstatR['JCode']=="OMF",dfstatR['Rankpc2'],dfstatR['Rankpc'])
            dfstatR['Rank']=np.where(dfstatR['JCode']=="OMF",dfstatR['MarkS'],dfstatR['Rank'])

            dfstatZ1=pd.merge(dfstatZ1,dfstatR,left_on=['YCode','JCode','ACode','CForm','SCode'],right_on=['YCode','JCode','ACode','CForm','SCode'])

            dfstatMRS= pd.DataFrame(df_tbl_ExamMark_S[['SCode','YCode','JCode','ACode','MarkS','CForm']])
            dfstatMRS=dfstatMRS.drop_duplicates()

            dfStatMRSRangesbins=[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105]
            dfStatMRSRangeslabels=[]
            for dfStatMRSRangesx in dfStatMRSRangesbins:
                  if 0 <= dfStatMRSRangesx < 95:
                        dfStatMRSRangeslabels.append(str(dfStatMRSRangesx).zfill(2) + " ≤ x < " + str(dfStatMRSRangesx+5).zfill(2))
                  elif 95 <= dfStatMRSRangesx <=100 :
                        dfStatMRSRangeslabels.append(str(dfStatMRSRangesx) + " ≤ x ≤ " + str(dfStatMRSRangesx+5))
                        
            dfstatMRS['MarkRange'] = pd.cut(dfstatMRS['MarkS'], bins=dfStatMRSRangesbins, labels=dfStatMRSRangeslabels,include_lowest=True,right=False)
            dfstatMRS['MarkRange'] = np.where(dfstatMRS['MarkRange'] == "100 ≤ x ≤ 105","95 ≤ x ≤ 100",dfstatMRS['MarkRange'])
            dfstatMRS['MarkRange'] = np.where(dfstatMRS['JCode'] == "OMF","",dfstatMRS['MarkRange'])
            dfstatMRS['SCForm'] = "S." + dfstatMRS['CForm']

            
            dfstatMRSC = pd.DataFrame(dfstatMRS.groupby(['YCode','JCode','ACode','CForm','SCForm','MarkRange'],as_index=False).agg({'MarkS':['count']}))
            
            dfstatMRSC.columns = ['YCode','JCode','ACode','CForm','SCForm','MarkRange','MarkRangeFreqSum']

            dfstatMRS1 = pd.DataFrame(dfstatMRSC[['YCode','JCode','ACode','CForm','SCForm']])
            dfstatMRS1 = dfstatMRS1.drop_duplicates()

            dfstatMRS2 = dfstatMRSC[dfstatMRSC['MarkRange']!='']
            dfstatMRS2 = dfstatMRS2.drop(columns=['YCode','JCode','ACode','CForm','SCForm','MarkRangeFreqSum'])
            dfstatMRS2 = dfstatMRS2.drop_duplicates()
            dfstatMRS2['MarkRangeFreqSum']=0

            dfstatMRS1['Temp']=1
            dfstatMRS2['Temp']=1

            dfstatMRS3=pd.merge(dfstatMRS1,dfstatMRS2,on=['Temp'])
            dfstatMRS3=dfstatMRS3.drop('Temp',axis=1)

            dfstatMRS4=pd.concat([dfstatMRSC, dfstatMRS3])

            dfstatMRS5=pd.DataFrame(dfstatMRS4.groupby(['YCode','JCode','ACode','CForm','SCForm','MarkRange'],as_index=False).agg({'MarkRangeFreqSum':['sum']}))
            dfstatMRS5.columns = ['YCode','JCode','ACode','CForm','SCForm','MarkRange','MarkRangeFreqSum']

            dfOutput1 = dfstat13[['YCode','JCode','ACode','CForm','Freq','Max','Avg','Median','Min','SD','Variance','PassFreq','Pass%','Skewness']]
            dfOutput2 = dfstatZ1[['YCode','JCode','ACode','CForm','CName','SCode','YCodeSel','CFormSel','CNameSel','Z-Score','Rank','Rankpc']]
            dfstatZ1forx5 = dfstatZ1            
                      
            dfOutput3 = dfstatMRS5[['YCode','JCode','ACode','CForm','SCForm','MarkRange','MarkRangeFreqSum']]

            runsql=3
           
      elif x == 1 and not(df_tbl_ExamMark_S.empty):

            dfstat11=pd.DataFrame(df_tbl_ExamMark_S.groupby(['YCode','JCode','ACode','CForm','CName'],as_index=False).agg({"MarkS":['count','max','mean','median','min','std','var','skew']}))
            dfstat11.columns=['YCode','JCode','ACode','CForm','CName','Freq','Max','Avg', 'Median', 'Min' ,'SD','Variance','Skewness']

            dfstat12=pd.DataFrame(df_tbl_ExamMark_G.groupby(['YCode','JCode','ACode','CForm','CName'],as_index=False).agg({"GradePass":['sum']}))
            dfstat12.columns=['YCode','JCode','ACode','CForm','CName','PassFreq']

            dfstat13=pd.merge(dfstat11,dfstat12,left_on=['YCode','JCode','ACode','CForm','CName'],right_on=['YCode','JCode','ACode','CForm','CName'])
            dfstat13['Pass%']=dfstat13['PassFreq']/dfstat13['Freq']

            dfOutput1 = dfstat13[['YCode','JCode','ACode','CForm','CName','Freq','Max','Avg','Median','Min','SD','Variance','PassFreq','Pass%','Skewness']]

      elif x == 2 and not(df_tbl_ExamMark_S.empty):

            df_tbl_ExamMark_G_NoRep = df_tbl_ExamMark_G[df_tbl_ExamMark_G['SCodeRep']==True]
            df_tbl_ExamMark_S_NoRep = df_tbl_ExamMark_S[df_tbl_ExamMark_S['SCodeRep']==True]

            dfstat11=pd.DataFrame(df_tbl_ExamMark_S_NoRep.groupby(['YCodeSel','JCode','ACode','CFormSel'],as_index=False).agg({"MarkS":['count','max','mean','median','min','std','var','skew']}))
            dfstat11.columns=['YCodeSel','JCode','ACode','CFormSel','Freq','Max','Avg', 'Median', 'Min' ,'SD','Variance','Skewness']

            dfstat12=pd.DataFrame(df_tbl_ExamMark_G_NoRep.groupby(['YCodeSel','JCode','ACode','CFormSel'],as_index=False).agg({"GradePass":['sum']}))
            dfstat12.columns=['YCodeSel','JCode','ACode','CFormSel','PassFreq']

            dfstat13=pd.merge(dfstat11,dfstat12,left_on=['YCodeSel','JCode','ACode','CFormSel'],right_on=['YCodeSel','JCode','ACode','CFormSel'])
            dfstat13['Pass%']=dfstat13['PassFreq']/dfstat13['Freq']

            dfstatZ1=pd.merge(df_tbl_ExamMark_S_NoRep,dfstat11,left_on=['YCodeSel','JCode','ACode','CFormSel'],right_on=['YCodeSel','JCode','ACode','CFormSel'])
            dfstatZ1['Z-Score']=(dfstatZ1['MarkS']-dfstatZ1['Avg'])/dfstatZ1['SD']

            dfOutput1 = dfstat13[['YCodeSel','JCode','ACode','CFormSel','Freq','Max','Avg','Median','Min','SD','Variance','PassFreq','Pass%','Skewness']]
            dfOutput2 = dfstatZ1[['YCode','JCode','ACode','CForm','CName','SCode','YCodeSel','CFormSel','CNameSel','Z-Score']]
            
            runsql=2
            
      elif x == 3 and not(df_tbl_ExamMark_S.empty):

            df_tbl_ExamMark_G_NoRep = df_tbl_ExamMark_G[df_tbl_ExamMark_G['SCodeRep']==True]
            df_tbl_ExamMark_S_NoRep = df_tbl_ExamMark_S[df_tbl_ExamMark_S['SCodeRep']==True]

            dfstat11=pd.DataFrame(df_tbl_ExamMark_S_NoRep.groupby(['YCodeSel','JCode','ACode','CFormSel','CNameSel'],as_index=False).agg({"MarkS":['count','max','mean','median','min','std','var','skew']}))
            dfstat11.columns=['YCodeSel','JCode','ACode','CFormSel','CNameSel','Freq','Max','Avg', 'Median', 'Min' ,'SD','Variance','Skewness']

            dfstat12=pd.DataFrame(df_tbl_ExamMark_G_NoRep.groupby(['YCodeSel','JCode','ACode','CFormSel','CNameSel'],as_index=False).agg({"GradePass":['sum']}))
            dfstat12.columns=['YCodeSel','JCode','ACode','CFormSel','CNameSel','PassFreq']

            dfstat13=pd.merge(dfstat11,dfstat12,left_on=['YCodeSel','JCode','ACode','CFormSel','CNameSel'],right_on=['YCodeSel','JCode','ACode','CFormSel','CNameSel'])
            dfstat13['Pass%']=dfstat13['PassFreq']/dfstat13['Freq']

            dfOutput1 = dfstat13[['YCodeSel','JCode','ACode','CFormSel','CNameSel','Freq','Max','Avg','Median','Min','SD','Variance','PassFreq','Pass%','Skewness']]

      elif x == 4 and (not(df_tbl_ExamMark_S.empty) or df_tbl_ExamMark_S.empty):

            df_tbl_ExamMark_G1=pd.merge(df_tbl_ExamMark_G,df_clist_Subject,left_on=['JCode'],right_on=['JCode'])
            df_tbl_ExamMark_G1.set_index(['YCode','ACode','SCode'])

            df_tbl_ExamMark_G1= df_tbl_ExamMark_G1[df_tbl_ExamMark_G1.JSubPaper == False]
            df_tbl_ExamMark_G1= df_tbl_ExamMark_G1[df_tbl_ExamMark_G1.GradeType=='DSE']
            df_tbl_ExamMark_G1= df_tbl_ExamMark_G1[df_tbl_ExamMark_G1.JCode != 'M1']
            df_tbl_ExamMark_G1= df_tbl_ExamMark_G1[df_tbl_ExamMark_G1.JCode != 'M2']
            df_tbl_ExamMark_G1= df_tbl_ExamMark_G1.drop(columns=['YCodeSel','CFormSel','CNameSel'])
            df_tbl_ExamMark_G1= df_tbl_ExamMark_G1.drop_duplicates()
            df_tbl_ExamMark_G1['SortKey']=df_tbl_ExamMark_G1['GradeDSEPoint'] * 1000 + df_tbl_ExamMark_G1['JO']

            df_tbl_ExamMark_G1['Sort']=df_tbl_ExamMark_G1.groupby(['YCode','ACode','CForm','SCode'],as_index=True)['SortKey'].rank(ascending=False)

            df_tbl_ExamMark_G1['SortC']=df_tbl_ExamMark_G1[~df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng','Maths','Maths-C','LS'])].groupby(['YCode','ACode','CForm','SCode'],as_index=True)['SortKey'].rank(ascending=False)
            df_tbl_ExamMark_G1.loc[df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng','Maths','Maths-C','LS']),"SortC"]=0

            df_Best6=df_tbl_ExamMark_G1[df_tbl_ExamMark_G1['Sort'] <= 6].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['sum']}).reset_index()
            df_Best6.columns=['YCode','ACode','SCode','Best6']
            
            df_Best5 = df_tbl_ExamMark_G1[df_tbl_ExamMark_G1['Sort'] <= 5].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['sum']}).reset_index()
            df_Best5.columns=['YCode','ACode','SCode','Best5']

            df_Best4C2X = df_tbl_ExamMark_G1[df_tbl_ExamMark_G1['SortC'] <= 2].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['sum']}).reset_index()
            df_Best4C2X.columns=['YCode','ACode','SCode','4C2X']

            df_Best4C1X = df_tbl_ExamMark_G1[df_tbl_ExamMark_G1['SortC'] <= 1].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['sum']}).reset_index()
            df_Best4C1X.columns=['YCode','ACode','SCode','4C1X']

            df_PassCheckC3E3_Count = df_tbl_ExamMark_G1[(df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=3)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckC3E3_Count.columns=['YCode','ACode','SCode','C3E3_Count']

            df_PassCheckC2E2_Count = df_tbl_ExamMark_G1[(df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=2)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckC2E2_Count.columns=['YCode','ACode','SCode','C2E2_Count']

            df_PassCheckM2L2_Count = df_tbl_ExamMark_G1[(df_tbl_ExamMark_G1.JCode.isin(['Maths','Maths-C','LS'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=2)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckM2L2_Count.columns=['YCode','ACode','SCode','M2L2_Count']

            df_PassCheckX3X3_Count = df_tbl_ExamMark_G1[(~df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng','Maths','Maths-C','LS'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=3)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckX3X3_Count.columns=['YCode','ACode','SCode','X3X3_Count']

            df_PassCheckX4_Count = df_tbl_ExamMark_G1[(~df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng','Maths','Maths-C','LS'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=4)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckX4_Count.columns=['YCode','ACode','SCode','X4_Count']

            df_PassCheckX2_Count = df_tbl_ExamMark_G1[(~df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng','Maths','Maths-C','LS'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=2)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckX2_Count.columns=['YCode','ACode','SCode','X2_Count']

            df_PassCheckHDX2X2X2_Count =  df_tbl_ExamMark_G1[(~df_tbl_ExamMark_G1.JCode.isin(['Chi','Eng'])) & (df_tbl_ExamMark_G1.GradeDSEPoint>=2)].groupby(['YCode','ACode','SCode'],as_index=True).agg({"GradeDSEPoint":['count']}).reset_index()
            df_PassCheckHDX2X2X2_Count.columns=['YCode','ACode','SCode','HDX2X2X2_Count']

            df_PassCheck_F = df_tbl_ExamMark_G.drop(columns=['JCode','MarkG','GradePass','GradeType','GradeDSEPoint','GradePriority'])
            df_PassCheck_F= df_PassCheck_F.drop_duplicates()

            df_PassCheck_List = [df_Best6,df_Best5,df_Best4C2X,df_Best4C1X,df_PassCheckC3E3_Count,df_PassCheckC2E2_Count,df_PassCheckM2L2_Count,df_PassCheckX3X3_Count,df_PassCheckX2_Count,df_PassCheckHDX2X2X2_Count,df_PassCheckX4_Count]

            for passcheck in df_PassCheck_List:
                df_PassCheck_F = pd.merge(df_PassCheck_F,passcheck,how='left',on=['YCode','ACode','SCode'])

            df_PassCheck_F=pd.DataFrame(df_PassCheck_F)
            df_PassCheck_F=df_PassCheck_F.replace(np.nan,0,regex=True)
            df_PassCheck_F.fillna(0)

            df_PassCheck_F['332233+'] =((df_PassCheck_F['C3E3_Count']==2) & (df_PassCheck_F['M2L2_Count']==2) & (df_PassCheck_F['X3X3_Count']>=2))
            df_PassCheck_F['33222+']  =((df_PassCheck_F['C3E3_Count']==2) & (df_PassCheck_F['M2L2_Count']==2) & (df_PassCheck_F['X2_Count']>=1))
            df_PassCheck_F['3322+']     =((df_PassCheck_F['C3E3_Count']==2) & (df_PassCheck_F['M2L2_Count']==2) )
            df_PassCheck_F['22222+'] =((df_PassCheck_F['C2E2_Count']==2) & (df_PassCheck_F['HDX2X2X2_Count']>=3))
            df_PassCheck_F['332222+']  =((df_PassCheck_F['C3E3_Count']==2) & (df_PassCheck_F['M2L2_Count']==2) & (df_PassCheck_F['X2_Count']>=2))
            df_PassCheck_F['33224+']  =((df_PassCheck_F['C3E3_Count']==2) & (df_PassCheck_F['M2L2_Count']==2) & (df_PassCheck_F['X4_Count']>=1))
            df_PassCheck_F['332244+']  =((df_PassCheck_F['C3E3_Count']==2) & (df_PassCheck_F['M2L2_Count']==2) & (df_PassCheck_F['X4_Count']>=2))

            dfOutput1 = df_PassCheck_F[['YCode','ACode','SCode','CForm','CName','YCodeSel','CFormSel','CNameSel','Best6','Best5','4C2X','4C1X','332233+','33222+','3322+','22222+','332222+','33224+','332244+']]
            dfOutput1.set_index(['YCode','ACode','SCode','CForm','CName','YCodeSel','CFormSel','CNameSel','Best6','Best5','4C2X','4C1X','332233+','33222+','3322+','22222+','332222+','33224+','332244+'])

      elif x==5  and not(df_tbl_ExamMark_S.empty) and not(df_tbl_ExamMark_G.empty) and not (df_tbl_ExamMark_G[df_tbl_ExamMark_G["ACode"].str[-5:]=="HKDSE"].empty):

            """ To Generate Data for Comparing DSE Results and Internal Assessments """
            
            dfDSE = df_tbl_ExamMark_G[df_tbl_ExamMark_G["ACode"].str[-5:]=="HKDSE"]
            dfDSE = dfDSE.replace("Maths-C","Maths")

            
            dfGIn = df_tbl_ExamMark_G
            dfSIn = df_tbl_ExamMark_S
            dfZIn = dfstatZ1forx5[['YCode','JCode','ACode','CForm','CName','SCode','Z-Score']]


            """dfZIn["Z-Score"]=dfZIn.round({"Z-Score":6})"""
            
            dfGIn = dfGIn.replace("Maths-C","Maths")
            dfSIn = dfSIn.replace("Maths-C","Maths")
            dfZIn = dfZIn.replace("Maths-C","Maths")
            
            dfDSE = dfDSE.drop(['YCodeSel','CFormSel','CNameSel','SCodeRep'], axis=1)
            dfGIn = dfGIn.drop(['YCodeSel','CFormSel','CNameSel','SCodeRep'], axis=1)
            dfSIn = dfSIn.drop(['YCodeSel','CFormSel','CNameSel','SCodeRep'], axis=1)

            dfIn = pd.merge(dfGIn, dfSIn, left_on = ['SCode','YCode','JCode','ACode','CForm','CName'],right_on = ['SCode','YCode','JCode','ACode','CForm','CName'])

            dfIn = pd.merge(dfIn, dfZIn, left_on = ['SCode','YCode','JCode','ACode','CForm','CName'],right_on = ['SCode','YCode','JCode','ACode','CForm','CName'])
          
            dfIn = dfIn.rename(columns={'YCode':'YCodeIn','ACode':'ACodeIn','CForm':'CFormIn','CName':'CNameIn','GradePass':'GradePassIn','GradePriority':'GradePriorityIn','GradeType':'GradeTypeIn','GradeDSEPoint':'GradeDSEPointIn'})
            dfDSE = dfDSE.rename(columns={'YCode':'YCodeDSE','ACode':'ACodeDSE','CForm':'CFormDSE','CName':'CNameDSE','MarkG':"MarkDSE"})

            print("----- dfIn -----")
            print(dfIn)
            print("----- dfDSE -----")
            print(dfDSE)
           
            dfDSEIn = pd.merge(dfDSE, dfIn, left_on=['JCode','SCode'],right_on=['JCode','SCode'])

            print("----- dfDSEIn -----")
            print(dfDSEIn)
                     
            dfDSEIn.columns= ['SCode','YCodeDSE','JCode','ACodeDSE','MarkDSE','CFormDSE','CNameDSE','GradePass','GradePriority','GradeType','GradeDSEPoint','YCodeIn','ACodeIn','MarkG','CFormIn','CNameIn','GradePassIn','GradePriorityIn','GradeTypeIn','GradeDSEPointIn','MarkS','Z-Score']

            dfOutput1=dfDSEIn.fillna(np.nan).replace([np.nan],[None])
            dfOutput1.set_index(['SCode','YCodeDSE','JCode','ACodeDSE','MarkDSE','CFormDSE','CNameDSE','GradePass','GradePriority','GradeType','GradeDSEPoint','YCodeIn','ACodeIn','MarkG','CFormIn','CNameIn','GradePassIn','GradePriorityIn','GradeTypeIn','GradeDSEPointIn','MarkS','Z-Score'])

            dfDSEInCorrGG = dfDSEIn.groupby(['JCode','ACodeDSE','ACodeIn']).apply(lambda dfDSEIn: dfDSEIn['GradeDSEPoint'].corr(dfDSEIn['GradeDSEPointIn']))
            dfDSEInCorrSG = dfDSEIn.groupby(['JCode','ACodeDSE','ACodeIn']).apply(lambda dfDSEIn: dfDSEIn['GradeDSEPoint'].corr(dfDSEIn['MarkS']))

            dfOutput2=pd.DataFrame(dfDSEInCorrGG)
            dfOutput2=dfOutput2.fillna(np.nan).replace([np.nan],[None])

            dfOutput2 = dfOutput2.reset_index()
            dfOutput2 = dfOutput2.rename(columns={0:'DSEInCorrR'})
            dfOutput2.set_index(['JCode',"ACodeDSE","ACodeIn","DSEInCorrR"])

            dfOutput3=pd.DataFrame(dfDSEInCorrSG)
            dfOutput3=dfOutput3.fillna(np.nan).replace([np.nan],[None])
            dfOutput3 = dfOutput3.reset_index()
            dfOutput3 = dfOutput3.rename(columns={0:'DSEInCorrR'})
            dfOutput3.set_index(['JCode',"ACodeDSE","ACodeIn","DSEInCorrR"])

            dfOutput2['MarkType']="G"
            dfOutput3['MarkType']="S"
            
            print(dfOutput2)
            print("-----")
            print(dfOutput3)

            runsql=3
            
      elif x>6:

            break

      print("****************************************")
      print("Round the numbers ---  " + str(x) + "  ---")
      print("****************************************")
      print(" ")

      """
      pyodbc and Access DB Connection - Python Marketer
      https://pythonmarketer.com/2019/11/30/inserting-new-records-into-a-microsoft-access-database-with-python/ 
      """
      def df_to_access(x):
          """
          use list comprehension to format df rows as a list of tuples. 
          rows = [('email@gmail.com', '2019-12-04','Clean'),('email2@gmail.com', '2019-12-01','Junk')] 
          """
          df_2_a = x.round(decimals=4)
          "df_2_a = df_2_a.replace(np.nan, '' , regex=True)"
          "df_2_a.fillna('')"
          rows = [tuple(cell) for cell in df_2_a.values]
          return rows



      print("****************************************")
      print("Save to Database (accdb) ---  " + str(x) + "  ---")
      print("****************************************")
      print(" ")

      conn1 = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\LamPatrick\Teaching\Software New\Python\SAPARC_Python.accdb;')
      cursor = conn1.cursor()

      if x == 0 and not(df_tbl_ExamMark_S.empty):

            sql = ''' INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
            sql2 = ''' INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,CName,SCode,YCodeSel,CFormSel,CNameSel,[Z-Score],Rank,Rankpc) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
            sql3 = ''' INSERT INTO tbl_ExamStat_MarkRange (YCode,JCode,ACode,CForm,SCForm,MarkRange,MarkRangeFreqSum) VALUES(?,?,?,?,?,?,?) '''

      elif x == 1 and not(df_tbl_ExamMark_S.empty):

            sql = ''' INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,CName,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''

      elif x == 2 and not(df_tbl_ExamMark_S.empty):

            sql = ''' INSERT INTO tbl_ExamStat_STierAll_Pivot (YCodeSel,JCode,ACode,CFormSel,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
            sql2 = ''' INSERT INTO tbl_ExamStat_STierAll_Pivot (YCode,JCode,ACode,CForm,CName,SCode,YCodeSel,CFormSel,CNameSel,[Z-Score]) VALUES(?,?,?,?,?,?,?,?,?,?) '''          

      elif x == 3 and not(df_tbl_ExamMark_S.empty):

            sql = ''' INSERT INTO tbl_ExamStat_STierAll_Pivot (YCodeSel,JCode,ACode,CFormSel,CNameSel,Freq,Max,Avg, Median, Min ,SD,Variance,PassFreq,[Pass%],Skewness) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''

      elif x == 4 and (not(df_tbl_ExamMark_S.empty) or df_tbl_ExamMark_S.empty):

            sql = ''' Insert Into tbl_ExamStat_STierAll_Pivot(YCode,ACode,SCode,CForm,CName,YCodeSel,CFormSel,CNameSel,Best6,Best5,4C2X,4C1X,[332233+],[33222+],[3322+],[22222+],[332222+],[33224+],[332244+]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''

      elif x==5    and not(df_tbl_ExamMark_S.empty) and not(df_tbl_ExamMark_G.empty):

            sql = ''' Insert Into tbl_ExamMark_DSE_In(SCode,YCodeDSE,JCode,ACodeDSE,MarkDSE,CFormDSE,CNameDSE,GradePass,GradePriority,GradeType,GradeDSEPoint,YCodeIn,ACodeIn,MarkG,CFormIn,CNameIn,GradePassIn,GradePriorityIn,GradeTypeIn,GradeDSEPointIn,MarkS,[Z-Score]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
            sql2 = ''' Insert Into tbl_ExamMark_DSE_In_Corr(JCode,ACodeDSE,ACodeIn,DSEInCorrR,MarkType) VALUES (?,?,?,?,?) '''
            sql3 = ''' Insert Into tbl_ExamMark_DSE_In_Corr(JCode,ACodeDSE,ACodeIn,DSEInCorrR,MarkType) VALUES (?,?,?,?,?) '''

      if (( 0<=x<=3 and not(df_tbl_ExamMark_S.empty)) or (x==4) or (x==5 and not(df_tbl_ExamMark_S.empty) and not(df_tbl_ExamMark_G.empty))and not (df_tbl_ExamMark_G[df_tbl_ExamMark_G["ACode"].str[-5:]=="HKDSE"].empty)):
            for runsqlx in range(runsql):

                  if runsqlx == 0:
                        d2acursor = dfOutput1
                        sqlcursor = sql
                  elif runsqlx == 1:
                        d2acursor = dfOutput2
                        sqlcursor = sql2
                  elif runsqlx == 2:
                        d2acursor = dfOutput3
                        sqlcursor = sql3
                        
                  rows = df_to_access(d2acursor)
                  row_in_check=1
                  for row in rows:
                        if (row_in_check==1) or (row_in_check%(10**int(math.log(row_in_check,10)))==0 ):
                              print("Saving Record  #" + str(row_in_check))
                              print(row)
                        row_in_check = row_in_check + 1
                        conn1.execute(sqlcursor, row)
                        conn1.commit()

      conn1.close()
