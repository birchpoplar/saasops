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

1. DONE Restructure folders and code as per below:

saas_analyzer/
├── data/
│   ├── create_tables.sql
│   └── sample_data.sql
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── dataframe_computations.py
│   └── visualization.py
├── .env
├── main.py
└── README.md

2. DONE Implement iPython experience for REPL interaction, confirm plot display
3. Implement functions to list available databases and load one
   - Given postgres, may need a config text file or something that lists the various databases available
4. Add in Rich text display for formatting

