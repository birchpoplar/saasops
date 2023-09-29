# Setting up the database and environment

## Creating a database

PostgreSQL is used as the database back-end for the app. Assuming PostgreSQL is installed, the following command will open up the `psql` CLI tool for administering databases:

	$ sudo -u postgres psql

Note this logs into psql as user `postgres`. Some extra commands, explained below, are needed to configure user rights correctly for the app. The following SQL statements will then create the database:

``` sql
CREATE DATABASE dbname;
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE dbname TO username;
```

## Configuring the app environment

### Creating `.env`

A`.env` file in the root folder of the app specifies the various environment variables used to configure the app. The `.env` file should contain:

```
DB_HOST=localhost
DB_USER=username
DB_PASSWORD=password
```

Various authentication solutions can be implemented as well to maintain secrecy of the password as needed.

### Setting `DB_NAME`

The remaining variable is `DB_NAME`, which can be specified in a `bash` shell, for example, as:

	$ export DB_NAME=dbname
	
## Configuring the test database 

The test fixtures and functions included with the app require a test database. The following SQL statements and `psql` commands will create the necessary structure:

``` sql
- CREATE USER testuser with PASSWORD 'testuser';
- CREATE DATABASE template_test_db;
- GRANT ALL PRIVILEGES ON DATABASE template_test_db TO testuser;
```

In `psql` run the following to create the table structure:

	postgres# \i create_tables.sql

Then run the following SQL statements in `psql`:

``` sql
- ALTER USER testuser CREATEDB; to create new DBs
- ALTER DATABASE template_test_db OWNER TO testuser;
- ALTER TABLE (all_tables) OWNER TO testuser: -- Need to do this for the five tables)
```

## Included SQL scripts

The repo includes the following SQL scripts:

- **create_tables.sql** = creates the table structures in the DB
- **show_rows.sql** = shows all rows in all tables
- **delete_data.sql** = delete all rows and tables in the DB

