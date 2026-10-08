-- Viajes por día de cada mes, para comparar el mismo mes en distintos años
SELECT
    taxi,
    month(periodo) AS mes,
    year(periodo) AS anio,
    round(count(*) / day(last_day(periodo))) AS viajes_por_dia
FROM viajes_validos
GROUP BY taxi, periodo
ORDER BY taxi DESC, mes, anio
