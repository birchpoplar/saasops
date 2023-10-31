-- Create Customers table
CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    Name TEXT,
    City TEXT,
    State TEXT
);

-- Create Contracts table
CREATE TABLE Contracts (
    ContractID SERIAL PRIMARY KEY,
    CustomerID INTEGER,
    RenewalFromContractID INTEGER,
    Reference TEXT,
    ContractDate DATE,
    TermStartDate DATE,
    TermEndDate DATE,
    TotalValue REAL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (RenewalFromContractID) REFERENCES Contracts(ContractID)
);

-- Create Segments table
CREATE TABLE Segments (
    SegmentID SERIAL PRIMARY KEY,
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
    InvoiceID SERIAL PRIMARY KEY,
    Number TEXT,
    Date DATE,
    DaysPayable INTEGER,
    Amount REAL
);

-- Create InvoiceSegments table
CREATE TABLE InvoiceSegments (
    InvoiceSegmentID SERIAL PRIMARY KEY,
    InvoiceID INTEGER,
    SegmentID INTEGER,
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID),
    FOREIGN KEY (SegmentID) REFERENCES Segments(SegmentID)
);

