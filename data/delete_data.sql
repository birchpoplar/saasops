-- Delete all rows and data in the database

DELETE FROM invoicesegments;
DELETE FROM invoices;
DELETE FROM segments;
DELETE FROM contracts;
DELETE FROM customers;

DROP TABLE customers CASCADE;
DROP TABLE contracts CASCADE;
DROP TABLE invoices CASCADE;
DROP TABLE invoicesegments CASCADE;
DROP TABLE segments CASCADE;
