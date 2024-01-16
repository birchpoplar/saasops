-- Create Customers table
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT,
    City TEXT,
    State TEXT
);

-- Create Contracts table
CREATE TABLE Contracts (
    ContractID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    RenewalFromContractID INTEGER,
    Reference TEXT,
    ContractDate DATE,
    TermStartDate DATE,
    TermEndDate DATE,
    TotalValue REAL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Create Segments table
CREATE TABLE Segments (
    SegmentID INTEGER PRIMARY KEY,
    ContractID INTEGER,
    SegmentStartDate DATE,
    SegmentEndDate DATE,
    ARROverrideStartDate DATE,
    ARROverrideNote TEXT,
    Title TEXT,
    Type TEXT,
    SegmentValue REAL,
    FOREIGN KEY (ContractID) REFERENCES Contracts(ContractID)
);

-- Create Invoices table
CREATE TABLE Invoices (
    InvoiceID INTEGER PRIMARY KEY,
    Number TEXT,
    Date DATE,
    DaysPayable INTEGER,
    Amount REAL
);

-- Create InvoiceSegments table
CREATE TABLE InvoiceSegments (
    InvoiceSegmentID INTEGER PRIMARY KEY,
    InvoiceID INTEGER,
    SegmentID INTEGER,
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID),
    FOREIGN KEY (SegmentID) REFERENCES Segments(SegmentID)
);

