-- I1 Viajes válidos por día en cada mes
SELECT
    periodo,
    taxi,
    round(count(*) / day(last_day(periodo))) AS valor
FROM viajes_validos
GROUP BY periodo, taxi
ORDER BY taxi DESC, periodo
