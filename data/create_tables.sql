CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT,
    quantity INTEGER,
    cost_price REAL,
    supplier TEXT,
    unit TEXT,
    specification TEXT,
    barcode TEXT,
    remark TEXT,
    attribute1 TEXT,
    attribute2 TEXT,
    attribute3 TEXT,
    attribute4 TEXT,
    attribute5 TEXT,
    in_time DATETIME,
    out_time DATETIME
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salesperson TEXT NOT NULL,
    sale_date TEXT NOT NULL,
    price REAL NOT NULL,
    product_id INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES product(id)
);

CREATE TABLE employees (
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    PRIMARY KEY (name)
);

commit;