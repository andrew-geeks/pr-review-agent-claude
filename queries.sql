-- Create orders table
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_ref VARCHAR(50),
    customer_name VARCHAR(100),
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create products table (missing created_at, updated_at; keywords lowercase)
create table products (
    id int primary key,
    name varchar(100),
    price decimal(10, 2)
);

-- SELECT * violation + lowercase keywords
select * from orders
where total_amount > 100;

-- lowercase join + SELECT *
select * from orders o
inner join products p on o.order_ref = p.name
where p.price > 50;

-- lowercase insert
insert into orders (order_ref, customer_name, total_amount)
values ('ORD001', 'John Doe', 250.00);

-- lowercase update
update orders
set total_amount = 300.00
where order_ref = 'ORD001';
