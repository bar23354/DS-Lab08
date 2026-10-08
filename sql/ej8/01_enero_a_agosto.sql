-- Indicadores de enero a agosto de cada año, los meses disponibles en los tres años
WITH base AS (
    SELECT
        v.*,
        inicio.distrito = 'Manhattan' AND fin.distrito = 'Manhattan' AS dentro_de_manhattan
    FROM viajes_validos AS v
    JOIN zonas AS inicio ON v.PULocationID = inicio.zona_id
    JOIN zonas AS fin ON v.DOLocationID = fin.zona_id
    WHERE month(v.periodo) <= 8
)
SELECT
    year(periodo) AS anio,
    taxi,
    round(count(*) / count(DISTINCT CAST(pickup_datetime AS DATE))) AS viajes_por_dia,
    round(median(total_amount), 2) AS total_mediano,
    round(100 * avg((coalesce(payment_type, 0) = 0)::INT), 1) AS pct_flex_fare,
    round(100 * avg((coalesce(payment_type, 0) = 2)::INT), 1) AS pct_efectivo,
    round(100 * avg(tip_amount / fare_amount) FILTER (WHERE payment_type = 1 AND fare_amount > 0), 1) AS propina_pct_tarifa,
    round(100 * avg((cbd_congestion_fee > 0)::INT), 1) AS pct_cargo_cbd,
    round(median(trip_distance / (duracion_min / 60)) FILTER (WHERE dentro_de_manhattan), 2) AS velocidad_manhattan,
    round(100 * avg((PULocationID IN (1, 132, 138) OR DOLocationID IN (1, 132, 138))::INT), 1) AS pct_aeropuerto
FROM base
GROUP BY anio, taxi
ORDER BY taxi DESC, anio
