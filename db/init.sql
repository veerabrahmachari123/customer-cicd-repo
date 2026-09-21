CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL
);

INSERT INTO customers (name, email)
SELECT 'John Doe', 'john@example.com'
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE email = 'john@example.com');

INSERT INTO customers (name, email)
SELECT 'Jane Smith', 'jane@example.com'
WHERE NOT EXISTS (SELECT 1 FROM customers WHERE email = 'jane@example.com');
