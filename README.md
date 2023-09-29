# SaaSOps - SaaS Tracking & Metrics Analysis
Track Customers, Contracts, Revenue Segments and Invoices for SaaS administration and metrics reporting. Generates recognized revenue, MRR, ARR and associated metrics for chosen time period. Output tables and charts to terminal or export to XLSX or PPTX.

## Objectives
- **Offer a platform for tracking customer and contract activity.** Intended primarily for early-stage startup execs and finance leaders.
- **Achieve consensus in SaaS metrics reporting across exec, ops and finance functions**, such agreement being critical for reporting to investors.
- **Ensure correct comprehension and use of metrics.** All too often users of metrics, and those who report them, don't comprehend the actual defintion and so report inaccurately to stakeholders and investors.
- **Bring the power of expanded metrics tracking to all users.** Some of the more complex metrics are challenging to produce reliably in spreadsheet environments, and lend themselves well to implementation in a programmed environment.

## Design approach
- **Why Open Source** - finance and finance-related functions in startups are mostly dependent upon either closed-source ledger and workflow tools or spreadsheet platforms. With increased availability of coding support and productivity tools it's possible that open source platforms could emerge for managing various aspects of the finance and operations functions in start-up and high-growth businesses.
- **Why CLI?** - easy to get to a first working app, and for early-stage B2B startups the volume of contract activity tends to be low enough such that CLI poses little impact on productivity. An API and browser UI/UX can be added later once main platform sufficiently developed.
- **Reconciliation to accounting** - standard reports with recognized revenue enable reconciliation to accounting data.

## Future 
To be added.

## Documentation
Current documentation can be found [here](https://birchpoplar.github.io/saasops/) on GitHub Pages.

## Demo: Adding Customers, Contracts and Segments
https://github.com/birchpoplar/saasops/assets/4149682/c59e6287-323c-464e-a986-887f45488c54
## Demo: Generating Metrics Reports
https://github.com/birchpoplar/saasops/assets/4149682/737d23fe-7dd1-4c2a-a443-edd1a7ca68c5
## Standard Analytics
The first three charts are generated from the demonstration contract and segment details entered in the above videos. The fourth chart, showing trailing 12-month cohort analytics for Net and Gross Dollar Retention is on different data.
### Bookings, ARR & CARR
Note: CARR is Contracted ARR.
![bookings_arr_carr](https://github.com/birchpoplar/saasops/assets/4149682/9ae71691-8d04-446b-aac0-241ed902a0c7)
### Monthly MRR
![monthly_mrr](https://github.com/birchpoplar/saasops/assets/4149682/a4a98a00-96ad-4bbc-8b16-9eeaed6d0076)
### MRR Change
Chart shows only the changes in MRR each month, without the starting and ending balances.
![mrr_change](https://github.com/birchpoplar/saasops/assets/4149682/4856e103-72bb-4930-96a0-354cd32bcfcf)
### TTM NDR & GDR
![trailing_12_month_values](https://github.com/birchpoplar/saasops/assets/4149682/cb7508ee-277c-4e4c-b1fd-da19ada0ddc8)
