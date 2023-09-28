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
	
