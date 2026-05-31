#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import sqlite3
from sqlalchemy import create_engine , text


# In[ ]:


# Read CSV
pd.read_csv("data/enrolments.csv")

# Datatype conversion 

# we have mixed date format in the course date field - convert course date to date field

df["course_date"] = pd.to_datetime(df["course_date"], errors = "coerce", format ="mixed")
df["course_date"] = df["course_date"].dt.date
# df.info()


# In[ ]:


# if the python verion doesn't support format = "mixed"
# from dateutil.parser import parse

# def parse_date(x):
#     try:
#         return parse(str(x), dayfirst=True).date()
#     except:
#         return None

# df["course_date"] = df["course_date"].apply(parse_date)


# In[ ]:


# To run this code
# Create SQLite database
# Create engine
# engine = create_engine("sqlite:///courses.db")

# conn = engine.connect()

# conn.execute(text("""drop table if exists courses"""))
# conn.execute(text("""drop table if exists enrollments"""))
# conn.execute(text("""drop table if exists enrolment"""))
# conn.execute(text("""drop table if exists silver_courses"""))
# conn.execute(text("""drop table if exists bronze_courses"""))
# conn.execute(text("""drop table if exists rejected_enrolments"""))
# conn.execute(text("""drop table if exists rejected_courses"""))
# conn.execute(text("""drop table if exists enrolments"""))
# conn.execute(text("""drop table if exists bronze_enrolments"""))
# conn.execute(text("""drop table if exists silver_enrolments"""))


# In[ ]:


# Create SQLite database
# Create engine
engine = create_engine("sqlite:///courses.db")

conn = engine.connect()

# conn.execute(text("""create table courses (
#     course_id int,
#     name text,
#     description text,
#     prerequisites text )"""
# ));

conn.execute(text("""drop table if exists enrolments"""))
conn.execute(text("""create table enrolments (
    enrollment_id int,
    participant_id string,
    participant_name string,
    course_id int,
    course_date date,
    amount float,
    subsidy float,
    credits_used float
);"""));

#Load data into sqllite
df.to_sql(
    name = "enrolments",
    con = conn,
    if_exists = "replace",
    index = False )
pd.read_sql("""
PRAGMA table_info(courses)
""", engine)

conn.commit()


# In[ ]:


pd.read_sql("""
SELECT name
FROM sqlite_master
WHERE type='table'
""", engine)


# In[ ]:


pd.read_sql("""
SELECT *
FROM courses
LIMIT 5
""", conn)


# In[ ]:


#BRONZE LAYER - Ingestion Timestamp ,sourcefile 

conn.execute(text("""
CREATE TABLE bronze_courses AS
SELECT
    *,
    'courses.csv' AS source_file_name,
    CURRENT_TIMESTAMP AS ingestion_timestamp
FROM courses
"""))

conn.execute(text("""
CREATE TABLE bronze_enrolments AS
SELECT
    *,
    'enrolments.csv' AS source_file_name,
    CURRENT_TIMESTAMP AS ingestion_timestamp
FROM enrolments
"""))

conn.commit()
pd.read_sql(
    "select * from bronze_enrolments",engine)

pd.read_sql("""
PRAGMA table_info(bronze_enrolments)
""", engine)


# In[ ]:





# In[ ]:


conn.execute (text("""
CREATE TABLE silver_courses (
    course_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    prerequisites TEXT
)"""))

conn.execute(text("""
CREATE TABLE silver_enrolments (
    enrollment_id INTEGER PRIMARY KEY,
    participant_id TEXT NOT NULL,
    participant_name TEXT NOT NULL,
    course_id INTEGER NOT NULL,
    course_date DATE NOT NULL,
    amount REAL CHECK(amount >= 0),
    subsidy REAL CHECK(subsidy >= 0),
    credits_used REAL CHECK(credits_used >= 0),
    FOREIGN KEY (course_id)
        REFERENCES silver_courses(course_id)
);"""))

conn.execute(text("""
CREATE TABLE rejected_enrolments (
    enrollment_id INTEGER,
    participant_id TEXT,
    participant_name TEXT,
    course_id INTEGER,
    course_date TEXT,
    amount REAL,
    subsidy REAL,
    credits_used REAL,
    rejection_reason TEXT,
    ingestion_timestamp TEXT
);"""))

conn.execute(text("""
CREATE TABLE rejected_courses (
    course_id INTEGER,
    name TEXT,
    description TEXT,
    prerequisites TEXT,
    rejection_reason TEXT,
    ingestion_timestamp TEXT
);"""))


# In[ ]:


# conn.execute(text("DELETE FROM silver_courses"))
# conn.execute(text("DELETE FROM silver_enrolments"))

conn.execute(text("""
INSERT INTO rejected_courses
SELECT
    course_id,
    name,
    description,
    prerequisites,
    'Invalid prerequisites JSON',
    CURRENT_TIMESTAMP
FROM bronze_courses
WHERE prerequisites IS NOT NULL
  AND json_valid(prerequisites) = 0
"""))

conn.execute(text("""
INSERT INTO silver_courses
SELECT
    course_id,
    TRIM(name),
    TRIM(description),
    prerequisites
FROM bronze_courses
WHERE course_id IS NOT NULL
  AND name IS NOT NULL
  AND (
        prerequisites IS NULL
        OR json_valid(prerequisites) = 1
      )
"""))


# In[ ]:





# In[ ]:


conn.execute(text("""
INSERT INTO rejected_enrolments
SELECT
    enrollment_id,
    participant_id,
    participant_name,
    course_id,
    course_date,
    amount,
    subsidy,
    credits_used,
    CASE
        WHEN enrollment_id IS NULL THEN 'Missing enrollment_id'
        WHEN participant_id IS NULL THEN 'Missing participant_id'
        WHEN participant_name IS NULL THEN 'Missing participant_name'
        WHEN course_id IS NULL THEN 'Missing course_id'
        WHEN course_date IS NULL THEN 'Invalid or missing course_date'
        WHEN amount < 0 THEN 'Negative amount'
        WHEN subsidy < 0 THEN 'Negative subsidy'
        WHEN credits_used < 0 THEN 'Negative credits_used'

    END,
    CURRENT_TIMESTAMP
FROM bronze_enrolments
WHERE enrollment_id IS NULL
   OR participant_id IS NULL
   OR participant_name IS NULL
   OR course_id IS NULL
   OR course_date IS NULL
   OR amount < 0
   OR subsidy < 0
   OR credits_used < 0
"""))

conn.execute(text("""
INSERT INTO silver_enrolments (
    enrollment_id,
    participant_id,
    participant_name,
    course_id,
    course_date,
    amount,
    subsidy,
    credits_used
)
SELECT DISTINCT
    enrollment_id,
    TRIM(participant_id),
    TRIM(participant_name),
    course_id,
    DATE(course_date),
    CAST(amount AS REAL),
    CAST(subsidy AS REAL),
    CAST(credits_used AS REAL)
FROM bronze_enrolments
WHERE enrollment_id IS NOT NULL
  AND participant_id IS NOT NULL
  AND participant_name IS NOT NULL
  AND course_id IS NOT NULL
  AND course_date IS NOT NULL
  AND amount >= 0
  AND subsidy >= 0
  AND credits_used >= 0
"""))


# In[ ]:


display(pd.read_sql("select * from silver_courses",conn))
display(pd.read_sql("select * from silver_enrolments",conn))
display(pd.read_sql("select * from rejected_courses",conn))
display(pd.read_sql("select * from rejected_enrolments",conn))


# In[ ]:


# try:
#     conn.close()
# except:
#     pass


# In[ ]:


# Gold Layer
# Prefer star schema to implement this 

# fact table - Enrolments
# dimension table - courses and participant

conn.execute(text("""Drop Table if exists dim_course"""))
conn.execute(text("""Drop Table if exists dim_participant"""))
conn.execute(text("""Drop Table if exists fact_enrolments"""))

conn.execute(text("""CREATE TABLE dim_course AS
SELECT DISTINCT
    course_id,
    name AS course_name,
    description
FROM silver_courses;"""))

conn.execute(text("""CREATE TABLE dim_participant AS
SELECT DISTINCT
    participant_id,
    participant_name
FROM silver_enrolments;"""))

conn.execute(text("""CREATE TABLE fact_enrolments AS
SELECT
    enrollment_id,
    participant_id,
    course_id,
    course_date,
    amount,
    subsidy,
    credits_used
FROM silver_enrolments;"""))


#indexing to improve query performance 

conn.execute(text("""CREATE INDEX idx_fact_course
ON fact_enrolments(course_id);"""))

conn.execute(text("""CREATE INDEX idx_fact_participant
ON fact_enrolments(participant_id);"""))

conn.execute(text("""CREATE INDEX idx_fact_date
ON fact_enrolments(course_date);"""))


#frequently used reports
conn.execute(text("""
DROP TABLE IF EXISTS gold_course_summary
"""))

conn.execute(text("""CREATE TABLE gold_course_summary AS
SELECT
    course_id,
    COUNT(*) AS total_enrolments,
    SUM(amount) AS total_revenue,
    SUM(subsidy) AS total_subsidy,
    SUM(credits_used) AS total_credits_used
FROM silver_enrolments
GROUP BY course_id;"""))

#Monthly trends
conn.execute(text("""
DROP TABLE IF EXISTS gold_monthly_summary
"""))
conn.execute(text("""CREATE TABLE gold_monthly_summary AS
SELECT
    strftime('%Y-%m', course_date) AS month,
    COUNT(*) AS total_enrolments,
    SUM(amount) AS total_revenue
FROM silver_enrolments
GROUP BY month;"""))





# In[ ]:


display(pd.read_sql("select * from gold_monthly_summary",conn))
display(pd.read_sql("select * from gold_course_summary",conn))


# In[ ]:


#participants that have registered for courses without meeting the prerequisites

pd.read_sql("""WITH prerequisite_courses AS (

    SELECT
        e.enrollment_id,
        e.participant_id,
        e.participant_name,
        e.course_id,
        e.course_date,
        json_each.value AS prerequisite_course_id

    FROM enrolments e

    JOIN courses c
        ON e.course_id = c.course_id

    JOIN json_each(c.prerequisites)

),

missing_prerequisites AS (

    SELECT
        pc.*

    FROM prerequisite_courses pc

    LEFT JOIN enrolments completed

        ON pc.participant_id = completed.participant_id

        AND completed.course_id = pc.prerequisite_course_id

        AND completed.course_date < pc.course_date

    WHERE completed.course_id IS NULL
)

SELECT
    participant_id,
    participant_name,
    course_id,
    prerequisite_course_id AS missing_prerequisite
FROM missing_prerequisites
ORDER BY participant_id, course_id;""",engine)



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




