# README

This README describes details for the SAPARC (Raimondi College Student Academic Performance Analysis) program.

## Directory Structure

    .
    ├── database                # Microsoft Access database files
    │   ├── data.accdb          # Database storing actual score data
    │   └── metadata.accdb      # Database storing metadata e.g. subject info
    ├── main.py                 # Main program
    └── README.md               # Documentations

## Pre-requisites for MacOS

1. Homebrew
    - See First Step in <https://pythonviz.com/basic/install-python3-macos-homebrew/> for installation guide
2. python3
    - Suggested Minimum Version: 3.9.13
    - See Second Step in <https://pythonviz.com/basic/install-python3-macos-homebrew/> for installation guide
3. mdbtools
    - See <https://github.com/mdbtools/mdbtools#installation> for installation guide

## General Pre-requisites

1. Python packages
    - Run `pip install -r requirements.txt` to install all required packages
    - Run `pip list` to check if the packages are installed

## Database Schemata

### tbl_ExamMark_G

| Column Name   | Data Type | Nullable? |
| ------------- | --------- | --------- |
| SCode         |           |           |
| YCode         |           |           |
| JCode         |           |           |
| ACode         |           |           |
| MarkG         |           |           |
| CForm         |           |           |
| CName         |           |           |
| GradePass     | Boolean   |           |
| GradePriority |           |           |
| GradeType     |           |           |
| YCodeSel      |           |           |
| CFormSel      |           |           |
| CNameSel      |           |           |
| GradeDSEPoint | Float64   | True      |
| SCodeRep      |           |           |

### tbl_ExamMark_P

| Column Name    | Data Type | Nullable? |
| -------------- | --------- | --------- |
| SCode          |           |           |
| YCode          |           |           |
| ACode          |           |           |
| 001SAVG        |           |           |
| 001GAVG        |           |           |
| 002SOMC        |           |           |
| 003SOMF        |           |           |
| 101GEng        |           |           |
| 101SEng        |           |           |
| 102GEng I      |           |           |
| 102SEng I      |           |           |
| 103GEng II     |           |           |
| 103SEng II     |           |           |
| 104GEng III    |           |           |
| 104SEng III    |           |           |
| 105GEng IV     |           |           |
| 105SEng IV     |           |           |
| 110GChi        |           |           |
| 110SChi        |           |           |
| 111GChi I      |           |           |
| 111SChi I      |           |           |
| 112GChi II     |           |           |
| 112SChi II     |           |           |
| 113GChi III    |           |           |
| 113SChi III    |           |           |
| 114GChi IV     |           |           |
| 114SChi IV     |           |           |
| 115GChi V      |           |           |
| 115SChi V      |           |           |
| 120GChiA       |           |           |
| 120SChiA       |           |           |
| 121GChiA I     |           |           |
| 121SChiA I     |           |           |
| 122GChiA II    |           |           |
| 122SChiA II    |           |           |
| 123GChiA III   |           |           |
| 123SChiA III   |           |           |
| 124GChiA IV    |           |           |
| 124SChiA IV    |           |           |
| 130GMaths      |           |           |
| 130SMaths      |           |           |
| 131GMaths-C    |           |           |
| 131SMaths-C    |           |           |
| 132GM1         |           |           |
| 132SM1         |           |           |
| 133GM2         |           |           |
| 133SM2         |           |           |
| 140GLS         |           |           |
| 140SLS         |           |           |
| 150GSci        |           |           |
| 150SSci        |           |           |
| 151GPhy        |           |           |
| 151SPhy        |           |           |
| 152GChem       |           |           |
| 152SChem       |           |           |
| 153GBio        |           |           |
| 153SBio        |           |           |
| 154GICT        |           |           |
| 154SICT        |           |           |
| 156GCBSci      |           |           |
| 156SCBSci      |           |           |
| 158GCBSciC     |           |           |
| 158SCBSciC     |           |           |
| 159GCBSciB     |           |           |
| 159SCBSciB     |           |           |
| 161GHist       |           |           |
| 161SHist       |           |           |
| 162GGeog       |           |           |
| 162SGeog       |           |           |
| 163GL&S        |           |           |
| 163SL&S        |           |           |
| 163GEPA        |           |           |
| 163SEPA        |           |           |
| 164GC_Hist     |           |           |
| 164SC_Hist     |           |           |
| 165GEF         |           |           |
| 165SEF         |           |           |
| 166GBAFS       |           |           |
| 166SBAFS       |           |           |
| 167GBAFS(Acc)  |           |           |
| 167SBAFS(Acc)  |           |           |
| 168GBAFS(BM)   |           |           |
| 168SBAFS(BM)   |           |           |
| 169GEcon       |           |           |
| 169SEcon       |           |           |
| 170GERS(DSE)   |           |           |
| 170SERS(DSE)   |           |           |
| 171GPE(DSE)    |           |           |
| 171SPE(DSE)    |           |           |
| 172GVA(DSE)    |           |           |
| 172SVA(DSE)    |           |           |
| 173GMusic(DSE) |           |           |
| 173SMusic(DSE) |           |           |
| 180GERS        |           |           |
| 180SERS        |           |           |
| 181GCL         |           |           |
| 182GVA         |           |           |
| 183GMusic      |           |           |
| 184GPTH        |           |           |
| 185GPE         |           |           |
| 203GFrench     |           |           |
| 203SFrench     |           |           |
| 204GFrench IV  |           |           |
| 204SFrench IV  |           |           |
| GB640          |           |           |
| SB640          |           |           |
| 201GJapanese   |           |           |
| 202GJapan IV   |           |           |

### tbl_ExamMark_S

| Column Name | Data Type | Nullable? |
| ----------- | --------- | --------- |
| SCode       |           |           |
| YCode       |           |           |
| JCode       |           |           |
| ACode       |           |           |
| MarkS       | Float64   |           |
| CForm       |           |           |
| CName       |           |           |
| YCodeSel    |           |           |
| CFormSel    |           |           |
| CNameSel    |           |           |
| SCodeRep    |           |           |

### CList_Subject

| Column Name | Data Type | Nullable? |
| ----------- | --------- | --------- |
| JCode       |           |           |
| JNameC      |           |           |
| JNameE      |           |           |
| JO          | Int64     | True      |
| JSubPaper   |           |           |
| jDSEJCode   |           |           |

## Guide

1. Install python packages:

   `pip install -r requirements.txt`
