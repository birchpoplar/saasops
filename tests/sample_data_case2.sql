-- Case 2
-- Single 12-Month Contract, $120k, renewed at end with double ARR $240k

-- Customers
INSERT INTO Customers (Name, City, State) VALUES ('Test Customer', 'City', 'State');

-- Contracts
INSERT INTO Contracts (CustomerID, Reference, ContractDate, TermStartDate, TermEndDate, TotalValue) VALUES (1, 'Test-Contract1', '2022-05-01', '2022-06-01', '2023-05-31', 120000);
INSERT INTO Contracts (CustomerID, Reference, ContractDate, TermStartDate, TermEndDate, TotalValue, RenewalFromContractID) VALUES (1, 'Test-Contract2', '2023-05-01', '2023-06-01', '2024-05-31', 240000, 1);

-- Segments
INSERT INTO Segments (ContractID, Title, SegmentStartDate, SegmentEndDate, Type, SegmentValue) VALUES (1, 'Test-Segment1', '2022-06-01', '2023-05-31', 'Subscription', 120000);
INSERT INTO Segments (ContractID, Title, SegmentStartDate, SegmentEndDate, Type, SegmentValue) VALUES (2, 'Test-Segment2', '2023-06-01', '2024-05-31', 'Subscription', 240000);

-- Invoices
INSERT INTO Invoices (Number, Date, DaysPayable, Amount) VALUES ('Test-Invoice1', '2022-05-01', 0, 120000);
INSERT INTO Invoices (Number, Date, DaysPayable, Amount) VALUES ('Test-Invoice2', '2023-05-01', 0, 240000);

-- InvoiceSegments
INSERT INTO InvoiceSegments (InvoiceID, SegmentID) VALUES (1, 1);
INSERT INTO InvoiceSegments (InvoiceID, SegmentID) VALUES (2, 2);
