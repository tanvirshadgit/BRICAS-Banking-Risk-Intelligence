-- BRICAS: reproducible analytics against the Day 1 schema
-- Daily volume and high-value transaction counts
SELECT substr(timestamp,1,10) AS day, COUNT(*) AS transaction_count,
 ROUND(SUM(amount_bdt),2) AS total_bdt,
 SUM(CASE WHEN amount_bdt >= 200000 THEN 1 ELSE 0 END) AS high_value_count
FROM transactions GROUP BY substr(timestamp,1,10) ORDER BY day;

-- Accounts with highest transaction value
SELECT a.account_id, c.region, c.kyc_status, a.status AS account_status,
 COUNT(*) AS transaction_count, ROUND(SUM(t.amount_bdt),2) AS total_bdt
FROM transactions t JOIN accounts a ON a.account_id=t.account_id
JOIN customers c ON c.customer_id=a.customer_id
GROUP BY a.account_id ORDER BY total_bdt DESC LIMIT 20;

-- Repeat high-value activity within the same calendar day (illustrative)
SELECT account_id, substr(timestamp,1,10) AS day, COUNT(*) AS high_value_count,
 ROUND(SUM(amount_bdt),2) AS high_value_total_bdt
FROM transactions WHERE amount_bdt >= 200000
GROUP BY account_id, substr(timestamp,1,10) HAVING COUNT(*) >= 2
ORDER BY high_value_count DESC, high_value_total_bdt DESC;
