-- Case 4
-- Single 6-Month Contract, $60k

-- Customers
INSERT INTO Customers (Name, City, State) VALUES ('Test Customer', 'City', 'State');

-- Contracts
INSERT INTO Contracts (CustomerID, Reference, ContractDate, TermStartDate, TermEndDate, TotalValue) VALUES (1, 'Test-Contract', '2022-05-01', '2022-06-01', '2022-11-30', 60000);

-- Segments
INSERT INTO Segments (ContractID, Title, SegmentStartDate, SegmentEndDate, Type, SegmentValue) VALUES (1, 'Test-Segment', '2022-06-01', '2022-11-30', 'Subscription', 60000);

-- Invoices
INSERT INTO Invoices (Number, Date, DaysPayable, Amount) VALUES ('Test-Invoice', '2022-05-01', 0, 60000);

-- InvoiceSegments
INSERT INTO InvoiceSegments (InvoiceID, SegmentID) VALUES (1, 1);
