# Data Structure & Definitions

## Database Structure

The application uses a PostgreSQL database to store information on contracts, customers, segments and invoices:

| Object   | Description                                                                                                                                                                                                                                               |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Customer | Customer name, city and state                                                                                                                                                                                                                             |
| Contract | Contract details, referencing customer ID and including information on reference, booked contract date, overall term start and end dates and total value. If the contract is a renewal of prior contract an optional field links to ID of prior contract. |
| Segment  | Represents a single revenue component of the parent contract. May be a Subscription or Service component. Has a total value and a segment start and end date.                                                                                             |
| Invoice  | Linked to one or more segments, and segments may have one or more invoices. Invoices also have typical data such as issue date, amount and days payable.                                                                                                  |

This structure is described in greater detail below.

## Understanding Segments

A basic Contract often has two main components:

1. Platform license subscription fee
2. Installation and onboarding

The Segment enables both of these components to be included in the database and helps ensure metrics and analysis output is based correctly on recurring and non-recurring revenue as appropriate.

For each of the above, an individual Segment will be defined:

1. **Platform Subscription**, of type Subscription with start date, end date and total segment value
2. **Installation Services**, of type Services and perhaps just total segment value, depending on whether or not any date information is available.

More complex Contracts may have multiple subscription components, each with different term dates and values. The Segment structure allows this detail to be captured.

## Database Diagram

``` mermaid
classDiagram
	Customer <|-- Contract
	Contract <|-- Segment
	Segment <|-- Invoice
class Customer{
	+int id
	+String name
	+String state
	+String city
}
class Contract{
	+int id
	+String reference
}
```
