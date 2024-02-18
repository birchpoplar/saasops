# SaaSops

> **Note:** This application is under constant development, and functionality may vary over time. Users are encouraged to try the app, provide feedback, and help identify any issues. Contributions towards improving SaaSops are highly welcomed.

SaaSops is a comprehensive command-line application tailored for RevOps within Software as a Service (SaaS) businesses, aiming to optimize SaaS administration and metrics reporting. It merges the simplicity of managing customers, contracts, segments, and invoices with the capability to generate recognized revenue, MRR (Monthly Recurring Revenue), ARR (Annual Recurring Revenue), and related metrics for any chosen time period.

Designed with efficiency at its core, SaaSops offers a robust suite of commands for seamless database interactions, dynamic data presentation, in-depth financial calculations, and versatile reporting options. Whether presenting output tables and charts directly in the terminal or exporting them to formats such as XLSX or PPTX, SaaSops is a useful tool for detailed financial analysis and data export functionalities.

## Key Features

- **Customer Management**: List and manage customer information seamlessly.
- **Contract Management**: Efficiently handle contract details, including sorting and filtering capabilities.
- **Segment Management**: Organize and manage segments for targeted analysis and operations.
- **Invoice Management**: Comprehensive invoice handling, from creation to mapping invoices to segments.
- **Financial Calculations**: Generate detailed financial metrics, including bookings, ARR (Annual Recurring Revenue), and ARR changes over specified timeframes.
- **Data Export**: Export data into various formats for analysis, reporting, or external use.
- **Database Flexibility**: Easily switch between databases with simple commands, supporting a dynamic operational environment.

## Installation

SaaSops is available for installation via pip. Ensure you have Python installed on your system and run the following command:

```bash
pip install saasops
```

Alternatively, you can clone the repository to get access to some test databases and explore the tool's full capabilities:

```bash
git clone <repository-url>
```

## Getting Started

After installing SaaSops, you can start using the application by running `saasops` followed by the specific command you wish to execute. Here's a quick overview of some commands:

### Set and Get Database

- Get the current database in use: `saasops get_db`

### Customer Commands

- List all customers: `saasops customer list`

### Contract Commands

- List all contracts: `saasops contract list [--sort_column <column_name>]`

### Financial Calculations

- Print bookings dataframe: `saasops calc bkingsdf <start_date> <end_date> [--customer <id>] [--contract <id>]`
- Print ARR dataframe: `saasops calc arrdf <start_date> <end_date> [--customer <id>] [--contract <id>]`

For a comprehensive list of commands and their descriptions, refer to the help option available with each command group, e.g., `saasops customer --help`.

## Contributing

We welcome contributions from the community! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## Additional Information

### Objectives
SaaSops is designed to streamline operational efficiency for SaaS businesses, focusing on the needs of early-stage startup executives and finance leaders. The core objectives are:
- **Comprehensive tracking** of customer and contract activities to provide a solid platform for operational and financial oversight.
- **Standardization of SaaS metrics reporting** across executive, operations, and finance functions to ensure alignment and accuracy, crucial for investor reporting.
- **Accurate understanding and application of metrics** to prevent misinterpretations that could mislead stakeholders and investors.
- **Access to advanced metrics tracking**, recognizing that complex metrics can be challenging to produce reliably in spreadsheet environments and are well-suited to a programmed environment.

### Design Approach
The foundation of SaaSops is shaped by a commitment to openness and accessibility:
- **Open Source**: The platform supports the transformative potential of open-source solutions for finance and operations functions in startups and high-growth companies, fostering innovation and community collaboration.
- **CLI-first Strategy**: A Command-Line Interface (CLI) enables rapid development of a functional application, suitable for early-stage B2B startups with a manageable contract volume. This approach allows for future expansion to an API and browser interface as the platform evolves.
- **Alignment with Accounting Practices**: Standard reports on recognized revenue facilitate seamless reconciliation with accounting records, ensuring financial integrity and compliance.

The design philosophy emphasizes simplicity, accuracy, and accessibility, aiming to empower startups and finance professionals with effective tools for SaaS management and reporting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.