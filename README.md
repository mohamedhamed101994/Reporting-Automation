# Reporting-Automation
Reporting Automation using python to check the new reports, validate and load it to SQL 

# Reporting Automation

An automated data validation and reporting pipeline built with
Python, SQL Server, and Power BI.

## Project Overview

This project automates the process of receiving,
validating, processing, and reporting business data.

## Technologies

- Python
- Pandas
- SQL Server
- Power BI
- Git & GitHub

## Workflow

                    Received Files
                          ↓
                    Data Validation
                          ↓
Data Processing           or              File Rejected
     ↓                                         ↓
SQL Server                            Generate an Errors log file 
    ↓
Reporting
    ↓
 Power BI
