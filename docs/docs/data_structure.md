# Data Structure & Definitions

## Database Structure

The application uses a PostgreSQL database to store information on contracts, customers, segments and invoices:

| Object   | Description                                                                                                                                                                                                                                               |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Customer | Customer name, city and state                                                                                                                                                                                                                             |
| Contract | Contract details, referencing customer ID and including information on reference, booked contract date, overall term start and end dates and total value. If the contract is a renewal of prior contract an optional field links to ID of prior contract. |
| Segment  | Represents a single revenue component of the parent contract. May be a Subscription or Service component. Has a total value and a segment start and end date.                                                                                             |
| Invoice  | Linked to one or more segments, and segments may have one or more invoices. Invoices also have typical data such as issue date, amount and days payable.                                                                                                  |




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
