
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100),
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



SELECT id, customer_name, total_amount
FROM orders
WHERE total_amount > 100
ORDER BY created_at DESC;



select * from orders where total_amount > 50;



create table products (
    product_name varchar(100),
    price decimal(10, 2)
);



INSERT INTO orders (customer_name, total_amount)
VALUES ('Alice', 250.00);



SELECT * FROM orders;
