-- Cost per model
SELECT model, SUM(cost_usd) AS total_cost
FROM inference_logs
GROUP BY model
ORDER BY total_cost DESC;
