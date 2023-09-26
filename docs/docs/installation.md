# Installing SaaSOps

## Cloning repo
The best approach currently to installing SaaSOps is to clone the repo located [here](https://github.com/birchpoplar/saasops).

Once cloned, run the following in the root folder of the repo:

	$ pipenv shell
	$ pipenv install

## Installing and setting up PostgreSQL

	$ sudo apt install postgresql
	
using psql with sudo
setting up template db for testing copy

## Checking using pytest

Best next step to check everything is working is to run:

	$ pytest
	
and check that everything tested out correctly.

# From original README.md - may need to go in separate .md file here

## Setting up Postgres DB

Log into psql as admin user:

- CREATE DATABASE dbname;
- CREATE USER user WITH PASSWORD 'password';
- GRANT ALL PRIVILEGES ON DATABASE dbname TO user;

Edit the .dir-locals.el file:

;; set SQL login parameters

((sql-mode . ((sql-postgres-login-params 
  '((user :default "user")
    (database :default "dbname")
    (server :default "localhost")
    (port :default 5432))))))
	
Then open the create_tables.sql file, and hit y to load the directory local variables.

## Template DB in Postgres for testing

- CREATE USER testuser with PASSWORD 'testuser';
- CREATE DATABASE template_test_db;
- GRANT ALL PRIVILEGES ON DATABASE template_test_db TO testuser;
- (in psql) ~\i create_tables.sql~
- 
- GRANT ALL PRIVILEGES ON DATABASE postgres TO testuser; (so can connect with an engine)
- ALTER USER testuser CREATEDB; to create new DBs
- ALTER DATABASE template_test_db OWNER TO testuser;
- ALTER TABLE (all_tables) OWNER TO testuser: -- Need to do this for the five tables)
Should have this as an SQL script that user can call into psql to set up correctly

also need template_customer_db - or maybe even just standard db template

## SQL scripts

- create_tables.sql = creates the table structures in the DB
- sample_data.sql = populates tables with the sample data
- show_rows.sql = shows all rows in all tables
- delete_data.sql = delete all rows and tables in the DB

## TODOs

1. Move into a docker container for install
2. make the app call the name only, not python + main.py
3. add in color selection for charts with config load
4. build in sanity/correctness checking on inputs, e.g. end date after start date etc.
5. export pptx function should take input filename as argument
