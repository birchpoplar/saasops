-- Case 1
-- Single 12-Month Contract, $120k

-- Customers
INSERT INTO Customers (Name, City, State) VALUES ('Test Customer', 'City', 'State');

-- Contracts
INSERT INTO Contracts (CustomerID, Reference, ContractDate, TermStartDate, TermEndDate, TotalValue) VALUES (1, 'Test-Contract', '2022-05-01', '2022-06-01', '2023-05-31', 120000);

-- Segments
INSERT INTO Segments (ContractID, Title, SegmentStartDate, SegmentEndDate, Type, SegmentValue) VALUES (1, 'Test-Segment', '2022-06-01', '2023-05-31', 'Subscription', 120000);

-- Invoices
INSERT INTO Invoices (Number, Date, DaysPayable, Amount) VALUES ('Test-Invoice', '2022-05-01', 0, 120000);

-- InvoiceSegments
INSERT INTO InvoiceSegments (InvoiceID, SegmentID) VALUES (1, 1);
