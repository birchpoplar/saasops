# SaaS Analyzer

Track Customers, Contracts, Revenue Segments and Invoices for SaaS finance administration. Generates recognized revenue, MRR, ARR and associated metrics for chosen time period. Output tables and charts to terminal or export to XLSX or PPTX.

## Setting up Postgres DB

Log into psql:

- CREATE DATABASE dbname;
- CREATE USER user WITH PASSWORD 'password';
- GRANT ALL PRIVILEGES ON DATABASE dbame TO user;

Edit the .dir-locals.el file:

;; set SQL login parameters

((sql-mode . ((sql-postgres-login-params 
  '((user :default "user")
    (database :default "dbname")
    (server :default "localhost")
    (port :default 5432))))))
	
Then open the create_tables.sql file, and hit y to load the directory local variables.

## SQL scripts

- create_tables.sql = creates the table structures in the DB
- sample_data.sql = populates tables with the sample data
- show_rows.sql = shows all rows in all tables
- delete_data.sql = delete all rows and tables in the DB

## TODOs

1. add in color selection for charts with config load
2. add first pytests with input dataframes/DB and output revenue/metrics
3. add input checking, or review function to analyze contracts/segments
