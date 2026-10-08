-- Cuartiles exactos del total por tipo de taxi
SELECT
    taxi,
    round(quantile_cont(total_amount, 0.25), 2) AS q1,
    round(quantile_cont(total_amount, 0.50), 2) AS mediana,
    round(quantile_cont(total_amount, 0.75), 2) AS q3
FROM viajes_validos
GROUP BY taxi
ORDER BY taxi
