
-- creat the database
CREATE DATABASE Reporting_DB

USE Reporting_DB

-- creat the first stageing for the data
CREATE SCHEMA stg


-- create the data table
CREATE TABLE stg.Audited_Data_Raw
(Client_ID      VARCHAR(20),
 User_ID        VARCHAR(20),
 Audit_Date     DATE,
 Audit_Status   VARCHAR(50),
 Score          DECIMAL(5,2),
 Comments       NVARCHAR(500),

 File_Name      VARCHAR(255),
 Load_Date      DATETIME2 DEFAULT GETDATE() )