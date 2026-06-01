```python
import pandas as pd
import sqlite3
from sqlalchemy import create_engine , text

```


```python
# Read CSV
pd.read_csv("data/enrolments.csv")

# Datatype conversion 

# we have mixed date format in the course date field - convert course date to date field

df["course_date"] = pd.to_datetime(df["course_date"], errors = "coerce", format ="mixed")
df["course_date"] = df["course_date"].dt.date
# df.info()
```


```python
# if the python verion doesn't support format = "mixed"
# from dateutil.parser import parse

# def parse_date(x):
#     try:
#         return parse(str(x), dayfirst=True).date()
#     except:
#         return None

# df["course_date"] = df["course_date"].apply(parse_date)
```


```python
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
```


```python
pd.read_sql("""
SELECT name
FROM sqlite_master
WHERE type='table'
""", engine)

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>courses</td>
    </tr>
    <tr>
      <th>1</th>
      <td>enrolments</td>
    </tr>
  </tbody>
</table>
</div>




```python
pd.read_sql("""
SELECT *
FROM courses
LIMIT 5
""", conn)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>course_id</th>
      <th>name</th>
      <th>description</th>
      <th>prerequisites</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>CS100 Introduction to Computer Science</td>
      <td>Foundational course covering computational thi...</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>CS101 Data structures</td>
      <td>Study of arrays, linked lists, trees, graphs, ...</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>CS200 Databases</td>
      <td>Covers relational database design, SQL, normal...</td>
      <td>[1,2]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>CS201 Networking</td>
      <td>Explores network protocols, TCP/IP stack, rout...</td>
      <td>[3]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>CS300 Systems</td>
      <td>Advanced course on operating systems, concurre...</td>
      <td>[4]</td>
    </tr>
  </tbody>
</table>
</div>




```python
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
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cid</th>
      <th>name</th>
      <th>type</th>
      <th>notnull</th>
      <th>dflt_value</th>
      <th>pk</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>enrollment_id</td>
      <td>INT</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>participant_id</td>
      <td>TEXT</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>participant_name</td>
      <td>TEXT</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>course_id</td>
      <td>INT</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>course_date</td>
      <td>NUM</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>amount</td>
      <td>REAL</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>subsidy</td>
      <td>REAL</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>credits_used</td>
      <td>REAL</td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>source_file_name</td>
      <td></td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>ingestion_timestamp</td>
      <td></td>
      <td>0</td>
      <td>None</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
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
conn.commit()
```


```python
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
conn.commit()
```


```python
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
conn.commit()
```


```python
display(pd.read_sql("select * from silver_courses",conn))
display(pd.read_sql("select * from silver_enrolments",conn))
display(pd.read_sql("select * from rejected_courses",conn))
display(pd.read_sql("select * from rejected_enrolments",conn))
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>course_id</th>
      <th>name</th>
      <th>description</th>
      <th>prerequisites</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>CS100 Introduction to Computer Science</td>
      <td>Foundational course covering computational thi...</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>CS101 Data structures</td>
      <td>Study of arrays, linked lists, trees, graphs, ...</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>CS200 Databases</td>
      <td>Covers relational database design, SQL, normal...</td>
      <td>[1,2]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>CS201 Networking</td>
      <td>Explores network protocols, TCP/IP stack, rout...</td>
      <td>[3]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>CS300 Systems</td>
      <td>Advanced course on operating systems, concurre...</td>
      <td>[4]</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>enrollment_id</th>
      <th>participant_id</th>
      <th>participant_name</th>
      <th>course_id</th>
      <th>course_date</th>
      <th>amount</th>
      <th>subsidy</th>
      <th>credits_used</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>1</td>
      <td>2024-01-15</td>
      <td>500.0</td>
      <td>200.0</td>
      <td>300.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>P002</td>
      <td>Bob Lee</td>
      <td>1</td>
      <td>2024-01-15</td>
      <td>500.0</td>
      <td>250.0</td>
      <td>250.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>P007</td>
      <td>Grace Koh</td>
      <td>1</td>
      <td>2024-01-20</td>
      <td>500.0</td>
      <td>250.0</td>
      <td>250.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>P009</td>
      <td>Irene Chua</td>
      <td>1</td>
      <td>2024-01-25</td>
      <td>500.0</td>
      <td>200.0</td>
      <td>300.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>P003</td>
      <td>Charlie Ng</td>
      <td>2</td>
      <td>2024-01-02</td>
      <td>600.0</td>
      <td>300.0</td>
      <td>300.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>6</td>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>2</td>
      <td>2024-02-01</td>
      <td>600.0</td>
      <td>200.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>7</td>
      <td>P004</td>
      <td>Diana Lim</td>
      <td>1</td>
      <td>2024-02-10</td>
      <td>500.0</td>
      <td>150.0</td>
      <td>350.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>8</td>
      <td>P007</td>
      <td>Grace Koh</td>
      <td>2</td>
      <td>2024-02-15</td>
      <td>600.0</td>
      <td>300.0</td>
      <td>300.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>9</td>
      <td>P009</td>
      <td>Irene Chua</td>
      <td>2</td>
      <td>2024-02-20</td>
      <td>600.0</td>
      <td>250.0</td>
      <td>350.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>10</td>
      <td>P002</td>
      <td>Bob Lee</td>
      <td>3</td>
      <td>2024-03-05</td>
      <td>750.0</td>
      <td>400.0</td>
      <td>350.0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>11</td>
      <td>P005</td>
      <td>Edward Goh</td>
      <td>4</td>
      <td>2024-03-15</td>
      <td>800.0</td>
      <td>350.0</td>
      <td>450.0</td>
    </tr>
    <tr>
      <th>11</th>
      <td>12</td>
      <td>P003</td>
      <td>Charlie Ng</td>
      <td>1</td>
      <td>2024-03-20</td>
      <td>750.0</td>
      <td>300.0</td>
      <td>450.0</td>
    </tr>
    <tr>
      <th>12</th>
      <td>13</td>
      <td>P008</td>
      <td>Henry Teo</td>
      <td>3</td>
      <td>2024-03-25</td>
      <td>750.0</td>
      <td>350.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>13</th>
      <td>14</td>
      <td>P007</td>
      <td>Grace Koh</td>
      <td>3</td>
      <td>2024-04-01</td>
      <td>750.0</td>
      <td>350.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>14</th>
      <td>15</td>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>3</td>
      <td>2024-01-04</td>
      <td>750.0</td>
      <td>200.0</td>
      <td>550.0</td>
    </tr>
    <tr>
      <th>15</th>
      <td>16</td>
      <td>P009</td>
      <td>Irene Chua</td>
      <td>3</td>
      <td>2024-04-05</td>
      <td>750.0</td>
      <td>350.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>16</th>
      <td>17</td>
      <td>P006</td>
      <td>Fiona Wong</td>
      <td>1</td>
      <td>2024-10-04</td>
      <td>500.0</td>
      <td>250.0</td>
      <td>250.0</td>
    </tr>
    <tr>
      <th>17</th>
      <td>18</td>
      <td>P004</td>
      <td>Diana Lim</td>
      <td>2</td>
      <td>2024-04-15</td>
      <td>600.0</td>
      <td>300.0</td>
      <td>300.0</td>
    </tr>
    <tr>
      <th>18</th>
      <td>19</td>
      <td>P006</td>
      <td>Fiona W</td>
      <td>2</td>
      <td>2024-04-22</td>
      <td>600.0</td>
      <td>250.0</td>
      <td>350.0</td>
    </tr>
    <tr>
      <th>19</th>
      <td>20</td>
      <td>P002</td>
      <td>Bob Lee</td>
      <td>4</td>
      <td>2024-05-01</td>
      <td>800.0</td>
      <td>400.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>20</th>
      <td>22</td>
      <td>P008</td>
      <td>Henry Teo</td>
      <td>4</td>
      <td>2024-05-15</td>
      <td>800.0</td>
      <td>400.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>21</th>
      <td>23</td>
      <td>P003</td>
      <td>Charlie Ng</td>
      <td>3</td>
      <td>2024-05-20</td>
      <td>900.0</td>
      <td>450.0</td>
      <td>450.0</td>
    </tr>
    <tr>
      <th>22</th>
      <td>24</td>
      <td>P007</td>
      <td>Grace Koh</td>
      <td>4</td>
      <td>2024-05-25</td>
      <td>800.0</td>
      <td>400.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>23</th>
      <td>25</td>
      <td>P006</td>
      <td>Fiona Wong</td>
      <td>2</td>
      <td>2024-06-01</td>
      <td>600.0</td>
      <td>250.0</td>
      <td>350.0</td>
    </tr>
    <tr>
      <th>24</th>
      <td>26</td>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>4</td>
      <td>1900-06-10</td>
      <td>800.0</td>
      <td>300.0</td>
      <td>500.0</td>
    </tr>
    <tr>
      <th>25</th>
      <td>27</td>
      <td>P004</td>
      <td>Diana Lim</td>
      <td>3</td>
      <td>2024-06-15</td>
      <td>750.0</td>
      <td>350.0</td>
      <td>400.0</td>
    </tr>
    <tr>
      <th>26</th>
      <td>28</td>
      <td>P009</td>
      <td>Irene Chua</td>
      <td>5</td>
      <td>2024-06-20</td>
      <td>900.0</td>
      <td>400.0</td>
      <td>500.0</td>
    </tr>
    <tr>
      <th>27</th>
      <td>29</td>
      <td>P008</td>
      <td>Henry Teo</td>
      <td>5</td>
      <td>2024-01-07</td>
      <td>900.0</td>
      <td>450.0</td>
      <td>450.0</td>
    </tr>
    <tr>
      <th>28</th>
      <td>30</td>
      <td>P002</td>
      <td>Bob Lee</td>
      <td>5</td>
      <td>2024-07-01</td>
      <td>900.0</td>
      <td>400.0</td>
      <td>500.0</td>
    </tr>
    <tr>
      <th>29</th>
      <td>31</td>
      <td>P007</td>
      <td>Grace Koh</td>
      <td>5</td>
      <td>2024-07-05</td>
      <td>900.0</td>
      <td>450.0</td>
      <td>450.0</td>
    </tr>
    <tr>
      <th>30</th>
      <td>32</td>
      <td>P006</td>
      <td>Fiona Wong</td>
      <td>3</td>
      <td>2024-10-07</td>
      <td>750.0</td>
      <td>300.0</td>
      <td>450.0</td>
    </tr>
    <tr>
      <th>31</th>
      <td>33</td>
      <td>P005</td>
      <td>Edward Goh</td>
      <td>1</td>
      <td>2024-07-15</td>
      <td>500.0</td>
      <td>200.0</td>
      <td>300.0</td>
    </tr>
    <tr>
      <th>32</th>
      <td>34</td>
      <td>P003</td>
      <td>Charles Ng</td>
      <td>4</td>
      <td>2024-07-20</td>
      <td>800.0</td>
      <td>350.0</td>
      <td>450.0</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>course_id</th>
      <th>name</th>
      <th>description</th>
      <th>prerequisites</th>
      <th>rejection_reason</th>
      <th>ingestion_timestamp</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>enrollment_id</th>
      <th>participant_id</th>
      <th>participant_name</th>
      <th>course_id</th>
      <th>course_date</th>
      <th>amount</th>
      <th>subsidy</th>
      <th>credits_used</th>
      <th>rejection_reason</th>
      <th>ingestion_timestamp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>21</td>
      <td>P005</td>
      <td>Edward Goh</td>
      <td>5</td>
      <td>None</td>
      <td>900.0</td>
      <td>500.0</td>
      <td>400.0</td>
      <td>Invalid or missing course_date</td>
      <td>2026-06-01 23:16:08</td>
    </tr>
  </tbody>
</table>
</div>



```python
# try:
#     conn.close()
# except:
#     pass
```


```python
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

conn.commit()


```


```python
display(pd.read_sql("select * from gold_monthly_summary",conn))
display(pd.read_sql("select * from gold_course_summary",conn))
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>month</th>
      <th>total_enrolments</th>
      <th>total_revenue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1900-06</td>
      <td>1</td>
      <td>800.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2024-01</td>
      <td>7</td>
      <td>4250.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2024-02</td>
      <td>4</td>
      <td>2300.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2024-03</td>
      <td>4</td>
      <td>3050.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2024-04</td>
      <td>4</td>
      <td>2700.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2024-05</td>
      <td>4</td>
      <td>3300.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2024-06</td>
      <td>3</td>
      <td>2250.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2024-07</td>
      <td>4</td>
      <td>3100.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2024-10</td>
      <td>2</td>
      <td>1250.0</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>course_id</th>
      <th>total_enrolments</th>
      <th>total_revenue</th>
      <th>total_subsidy</th>
      <th>total_credits_used</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>8</td>
      <td>4250.0</td>
      <td>1800.0</td>
      <td>2450.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>7</td>
      <td>4200.0</td>
      <td>1850.0</td>
      <td>2350.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>8</td>
      <td>6150.0</td>
      <td>2750.0</td>
      <td>3400.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>6</td>
      <td>4800.0</td>
      <td>2200.0</td>
      <td>2600.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>4</td>
      <td>3600.0</td>
      <td>1700.0</td>
      <td>1900.0</td>
    </tr>
  </tbody>
</table>
</div>



```python
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


```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>participant_id</th>
      <th>participant_name</th>
      <th>course_id</th>
      <th>missing_prerequisite</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>3</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>P001</td>
      <td>Alice Tan</td>
      <td>4</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>P002</td>
      <td>Bob Lee</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>P005</td>
      <td>Edward Goh</td>
      <td>4</td>
      <td>3</td>
    </tr>
    <tr>
      <th>5</th>
      <td>P005</td>
      <td>Edward Goh</td>
      <td>5</td>
      <td>4</td>
    </tr>
    <tr>
      <th>6</th>
      <td>P008</td>
      <td>Henry Teo</td>
      <td>3</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>P008</td>
      <td>Henry Teo</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>8</th>
      <td>P008</td>
      <td>Henry Teo</td>
      <td>5</td>
      <td>4</td>
    </tr>
    <tr>
      <th>9</th>
      <td>P009</td>
      <td>Irene Chua</td>
      <td>5</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>


