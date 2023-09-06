# SaaS Analyzer

Track Customers, Contracts, Revenue Segments and Invoices for SaaS finance and revenue metrics administration.

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

1. implement input checking on contracts/segments, sanity check to ensure the EoM and MoM calculations work correctly
2. implement pylatex, to generate PDF via LaTeX, and this could import text from input files as commentary to the images, etc.
3. start using with two clients properly
