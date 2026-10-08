-- Viajes válidos por mes y tipo de taxi
SELECT
    taxi,
    periodo,
    count(*) AS viajes,
    round(count(*) / day(last_day(periodo))) AS viajes_por_dia
FROM viajes_validos
GROUP BY taxi, periodo
ORDER BY taxi DESC, periodo
