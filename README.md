# SaaS Analyzer

Track Customers, Contracts, Revenue Segments and Invoices for SaaS finance administration. Generates recognized revenue, MRR, ARR and associated metrics for chosen time period. Output tables and charts to terminal or export to XLSX or PPTX.

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


## SQL scripts

- create_tables.sql = creates the table structures in the DB
- sample_data.sql = populates tables with the sample data
- show_rows.sql = shows all rows in all tables
- delete_data.sql = delete all rows and tables in the DB

## TODOs

- Move into a docker container for install
- provide easy selection between databases (for multiple clients)
- make status updates consistent and more descriptive on what is going on behind calcs
- add in the docstrings for the typer commands
- make the app call the name only, not python + main.py
- 

MAJOR ONE: dealing with contracts that are not 12 months:
- what contribution to ARR
- how to recognize revenue (divide total by number of months
- need to solve this one next
- perhaps needs annual equivalent
- check the insight partners deck

1. add in color selection for charts with config load
3. finish off typer command definitions plus docstrings
4. add in two level command definition in typer
4. build in database selection command/config (from CLI)
5. sort out standard status update printlines for all functions (maybe Rich with horizontal lines etc.)
6. build sanity check on segments/contracts - match total value and timeline, identify inconsistencies
7. build in sanity/correctness checking on inputs, e.g. end date after start date etc.
8. export pptx function should take input filename as argument
