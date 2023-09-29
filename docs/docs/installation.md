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

