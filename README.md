# GovTech CET Assessment – Dhivyadharshni

## Project Overview

This project implements a data ingestion and reporting solution for Course Enrolment data submitted by Continuous Education and Training (CET) centres.

The solution demonstrates:

* Data ingestion into SQLite
* Medallion Architecture (Bronze, Silver, Gold)
* Data quality validation and rejected record handling
* Analytical data modelling
* SQL reporting for prerequisite validation
* Scalable solution design for machine learning inference using AWS SageMaker


## Section 1 – Data Ingestion

The enrolment data is ingested into a SQLite database using Python, Pandas, and SQLAlchemy.

Source tables:

* courses
* enrolments

The ingestion process includes:

* Data type conversion
* Date standardisation
* Validation checks
* Loading into Bronze, Silver, and Gold layers


## Section 2 – Database Design

A Medallion Architecture approach was implemented.

### Bronze Layer

Stores raw source data with ingestion metadata.

Additional fields:

* source_file_name
* ingestion_timestamp

Tables:

* bronze_courses
* bronze_enrolments

### Silver Layer

Stores cleansed and validated data.

Transformations include:

* Data type standardisation
* Null handling
* Duplicate removal
* Business rule validation
* Referential integrity checks

Tables:

* silver_courses
* silver_enrolments

Rejected records are stored separately for auditability:

* rejected_courses
* rejected_enrolments

### Gold Layer

Stores business-ready datasets optimized for analytics.

Tables:

* fact_enrolments
* dim_course
* dim_participant
* gold_course_summary
* gold_monthly_summary


## Section 3 – SQL Reporting

A SQL solution was developed to identify participants who registered for courses without satisfying prerequisite requirements.

The solution uses:

* JSON parsing via SQLite JSON functions
* Self-joins on enrolment history
* Prerequisite validation logic

The SQL script is available under:

sql/prerequisite_report.sql


## Section 4 – Solution Design

The assessment includes a solution design discussion for processing 200 million course records using a machine learning model deployed on AWS SageMaker.

Topics covered:

* Bottleneck identification
* Sequential API invocation challenges
* Batch processing
* Distributed processing with AWS Glue / Spark
* SageMaker endpoint optimization
* SageMaker Batch Transform
* Incremental processing strategies

Detailed discussion is available in:

docs/Solution_Design_AWS_SageMaker

---

## Technologies Used

* Python
* Pandas
* SQLite
* SQLAlchemy
* Jupyter Notebook
* AWS (Conceptual Design)
* AWS Glue (Conceptual Design)
* AWS SageMaker (Conceptual Design)

