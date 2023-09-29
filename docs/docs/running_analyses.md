# Running Metrics Analyses

Each of the revenue and metrics reports can be filtered to specific customer or contract activity by passing flags to the commands as follows:

	--customer ID
	--contract ID
	
Passing either flag will limit the reports generated to the specified customer or contract ID. Both flags can be passed but the contract ID filter will override the customer.

## Recognized Revenue Report

Recognized revenue reports can be run to reconcile with financial statements for consistency. Reports can be configured for end-of-month or middle-of-month timing.

	$ saasops calc rev 2023-01-01 2023-12-31 mid
	$ saasops calc rev 2023-01-01 2023-12-31 end
	
Middle-of-month timing is often a good compromise as any segment with start date in first half of the month has a full month's revenue counted, and any segment with start date in the second half of the month has no revenue counted in that month with first full month recognized the following month. 

Report dates are updated depending on the `mid` or `end` flag passed to the command. Sample revenue report is below:

```
	Revenue, 2023-01-31 to 2023-06-30, type: end-month
---------------------------------------------------------------------------------------------
|                Customer | Jan-2023 | Feb-2023 | Mar-2023 | Apr-2023 | May-2023 | Jun-2023 |
---------------------------------------------------------------------------------------------
¦          CUSTOMER       ¦    23000 ¦    23000 ¦    23000 ¦    23000 ¦    23000 ¦    23000 ¦
+-------------------------+----------+----------+----------+----------+----------+----------¦
¦          CUSTOMER       ¦        0 ¦        0 ¦        0 ¦        0 ¦        0 ¦        0 ¦
+-------------------------+----------+----------+----------+----------+----------+----------¦
¦          CUSTOMER       ¦        0 ¦        0 ¦        0 ¦        0 ¦        0 ¦        0 ¦
+-------------------------+----------+----------+----------+----------+----------+----------¦
¦          CUSTOMER       ¦        0 ¦        0 ¦     5660 ¦     5660 ¦     5660 ¦     5660 ¦
+-------------------------------------------------------------------------------------------+
```

## Bookings, CARR & ARR Report

The report table showing bookings, CARR and ARR on a monthly basis (end-of-month timing) can be generated as follows:

	$ saasops calc bkings 2023-03-01 2023-06-30

Sample report output is below:

```
Bookings, ARR and CARR, 2023-03-01 to 2023-06-30
--------------------------------------------------------
| Customer | Mar-2023 | Apr-2023 | May-2023 | Jun-2023 |
--------------------------------------------------------
¦ Bookings ¦    70000 ¦        0 ¦        0 ¦   400000 ¦
+----------+----------+----------+----------+----------¦
¦      ARR ¦   301114 ¦   301114 ¦   301114 ¦   301114 ¦
+----------+----------+----------+----------+----------¦
¦     CARR ¦   301114 ¦   301114 ¦   301114 ¦   701114 ¦
+------------------------------------------------------+
```

## MRR Inflow/Outflow Report

A table showing inflow and outflows of Monthly Recurring Revenue can be generated using the `metrics` subcommand:

	$ saasops calc metrics 2023-03-01 2023-06-30

Starting MRR applies at the beginning of each month, and Ending MRR at the end of each month. New, Churn, Expansion and Contraction are reported as aggregate over each month. Sample report output is shown below:

```
Metrics, 2023-03-01 to 2023-06-30
---------------------------------------------------------------
|        Customer - Mar-2023 | Apr-2023 | May-2023 | Jun-2023 |
---------------------------------------------------------------
¦         New MRR ¦     5000 ¦        0 ¦        0 ¦        0 ¦
+-----------------+----------+----------+----------+----------¦
¦       Churn MRR ¦        0 ¦     2500 ¦        0 ¦        0 ¦
+-----------------+----------+----------+----------+----------¦
¦   Expansion MRR ¦        0 ¦     2000 ¦        0 ¦        0 ¦
+-----------------+----------+----------+----------+----------¦
¦ Contraction MRR ¦        0 ¦        0 ¦        0 ¦     1000 ¦
+-----------------+----------+----------+----------+----------¦
¦    Starting MRR ¦    10000 ¦    15000 ¦    14500 ¦    14500 ¦
+-----------------+----------+----------+----------+----------¦
¦      Ending MRR ¦    15000 ¦    14500 ¦    14500 ¦    13500 ¦
+-------------------------------------------------------------+
```

## Snapshot CARR & ARR

Point in time reports for CARR and ARR, showing totals by Customer, can be generated as follows:

	$ saasops calc carr 2023-06-30
	$ saasops calc arr 2023-06-30
