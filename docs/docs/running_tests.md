# Running tests

The app includes a set of tests for the report and metrics generation functions. Details can be found in `tests/`. The test framework uses `pytest`, and tests can be run from the root folder as follows:

	$ pytest
	
Adding the `--verbose` flag will print out individual test details.

!!! note
    Successful execution of the tests is reliant upon the test database being set-up as described [here](setting_up.md).

## Testing philosophy

At a high-level, for simply-defined contract inputs, the outputs for the various metrics are deterministic and can be hard-coded into a test fixture.

The test framework includes a series of cases, detailed in `tests/test_cases.xlsx`, that cover various permutations of contract types, renewals, churn and so on.

An initial set of cases is included and the test framework will be expanded in future releases.
