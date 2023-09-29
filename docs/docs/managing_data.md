# Managing Input Data

Using the CLI the various input data can be added to the tables in the database.

!!! note
    The code examples below assume the app is executed with `saasops` achieved by an alias `alias saasops='python main.py'`. This achieves similar usability as if the app had been packaged with PyPI.

## Adding Customers

The help information including argument details can be accessed using:

	$ saasops customer add --help

A typical command to add a customer is below. Note that any arguments containing spaces and other punctuation should be surrounded in quotes to be recognized as a `String`:

	$ saasops customer add 'Customer Name' City State

Then run a command to list the customers to confirm the data added is as intended:

	$ saasops customer list
	
## Adding Contracts

Access the general help info with:

	$ saasops contract add --help
	
Typical command to add a contract would be:

	$ saasops contract add 1 ContractRef 2022-04-01 2022-05-01 2023-04-30 120000
	
Note that a contract that is a renewal of a prior contract can be linked using `renewal-id`:

	$ saasops contract add 2 RenewalRef 2023-04-01 2023-05-01 2024-04-30 180000 --renewal-id 1
	
It's necessary to link renewal contracts to ensure the metrics for expansion or contraction are reported instead of new or churn.

Check the contract was added correctly with:

	$ saasops contract list

## Adding Segments & Reconciling

As with customers and contracts, segments can be added with:

	$ saasops segment add 1 2022-05-01 2023-04-30 'Platform License' Subscription 120000
	
Check the addition with:

	$ saasops segment list
	
An important step in finishing up on contract and segment entry is to confirm reconciliation between a contract and its associated segments. The total value of the contract should match the total aggregate value of the segments. The app includes a reporting command to aid in this reconciliation:

	$ saasops contract reconcile 1
	
This command will output the contract details and then a table with the associated segments. The aggregate value of the segments is calculated and reported after the table.

!!! warning
    The app does not yet include an automated reconciliation feature, and so will not yet highlight instances where the total aggregate segment value is not equal to the contract value. At present this check must be done manually.

## Adding Invoices

To be completed.

!!! note
    The Invoice structure is included for future app expansion. The current metrics and output functions do not require invoice information.

## Amending Data Inputs

Any entry in any of the database tables can be updated to a new value using:

	$ saasops TABLE update ID FIELD VALUE
	
For example:

	$ saasops contract update 1 contractdate 2022-03-01
	
To move the booked date of our example contract above forward one month.

Field names can be found in the `create_tables.sql` script in the `data/` folder.

