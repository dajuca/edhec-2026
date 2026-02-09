-- Simple but BI-realistic dataset: daily sales by country/product with seasonality + promos
CREATE TABLE IF NOT EXISTS sales (
    sale_date DATE NOT NULL,
    country TEXT NOT NULL,
    channel TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product TEXT NOT NULL,
    units INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    revenue NUMERIC(12,2) NOT NULL
);

-- Dimension-like table for targets (useful for Power BI KPI measures)
CREATE TABLE IF NOT EXISTS sales_targets (
    month_start DATE NOT NULL,
    country TEXT NOT NULL,
    target_revenue NUMERIC(12,2) NOT NULL
);

-- Seed a small initial dataset (students can scale it later)
INSERT INTO sales (sale_date, country, channel, product_category, product, units, unit_price, revenue) VALUES
('2024-01-01','France','Retail','Watches','Aurum One',3,4200.00,12600.00),
('2024-01-02','France','Online','Jewelry','Luna Ring',6,650.00,3900.00),
('2024-01-03','Italy','Retail','Jewelry','Luna Ring',9,650.00,5850.00),
('2024-01-04','USA','Online','Watches','Aurum One',2,4200.00,8400.00),
('2024-01-05','Japan','Retail','Watches','Kintsugi Chrono',1,9800.00,9800.00),
('2024-01-06','France','Retail','Accessories','Silk Strap',15,120.00,1800.00),
('2024-01-07','Italy','Online','Watches','Aurum One',1,4200.00,4200.00),
('2024-01-08','Spain','Online','Jewelry','Sol Necklace',4,1200.00,4800.00);

INSERT INTO sales_targets (month_start, country, target_revenue) VALUES
('2024-01-01','France',50000.00),
('2024-01-01','Italy',35000.00),
('2024-01-01','USA',60000.00),
('2024-01-01','Japan',30000.00);
