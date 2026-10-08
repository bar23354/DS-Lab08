-- Registros que rompen reglas de fecha, duración, distancia, montos o zona
WITH viajes AS (
    SELECT
        'yellow' AS taxi,
        regexp_extract(filename, '(\d{4}-\d{2})\.parquet', 1) AS mes_archivo,
        tpep_pickup_datetime AS inicio,
        tpep_dropoff_datetime AS fin,
        trip_distance, fare_amount, total_amount, passenger_count, PULocationID, DOLocationID
    FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true, filename = true)
    UNION ALL
    SELECT
        'green',
        regexp_extract(filename, '(\d{4}-\d{2})\.parquet', 1),
        lpep_pickup_datetime,
        lpep_dropoff_datetime,
        trip_distance, fare_amount, total_amount, passenger_count, PULocationID, DOLocationID
    FROM read_parquet('data/raw/green/*/*.parquet', union_by_name = true, filename = true)
)
SELECT
    taxi,
    count(*) AS viajes,
    count(*) FILTER (WHERE strftime(inicio, '%Y-%m') <> mes_archivo) AS inicio_fuera_del_mes,
    count(*) FILTER (WHERE fin <= inicio) AS duracion_cero_o_negativa,
    count(*) FILTER (WHERE fin - inicio > INTERVAL 3 HOUR) AS duracion_mayor_3h,
    count(*) FILTER (WHERE trip_distance = 0) AS distancia_cero,
    count(*) FILTER (WHERE trip_distance > 100) AS distancia_mayor_100,
    count(*) FILTER (WHERE fin > inicio AND trip_distance / (epoch(fin - inicio) / 3600) > 80) AS velocidad_mayor_80,
    count(*) FILTER (WHERE fare_amount < 0) AS tarifa_negativa,
    count(*) FILTER (WHERE total_amount <= 0) AS total_cero_o_negativo,
    count(*) FILTER (WHERE passenger_count = 0) AS pasajeros_cero,
    count(*) FILTER (WHERE PULocationID IN (264, 265) OR DOLocationID IN (264, 265)) AS zona_desconocida
FROM viajes
GROUP BY taxi
ORDER BY taxi DESC
