-- Vistas sobre los Parquet de data/raw, sin copiar datos

-- Viajes amarillos y verdes con nombres comunes y periodo como el mes del archivo de origen
-- cbd_congestion_fee vale 0 en los archivos anteriores a 2025, cuando el cargo no existía
CREATE OR REPLACE VIEW viajes AS
SELECT
    'yellow' AS taxi,
    strptime(regexp_extract(filename, '(\d{4}-\d{2})\.parquet', 1), '%Y-%m')::DATE AS periodo,
    tpep_pickup_datetime AS pickup_datetime,
    tpep_dropoff_datetime AS dropoff_datetime,
    * EXCLUDE (tpep_pickup_datetime, tpep_dropoff_datetime, cbd_congestion_fee, filename),
    coalesce(cbd_congestion_fee, 0) AS cbd_congestion_fee
FROM read_parquet('data/raw/yellow/*/*.parquet', union_by_name = true, filename = true)
UNION ALL BY NAME
SELECT
    'green' AS taxi,
    strptime(regexp_extract(filename, '(\d{4}-\d{2})\.parquet', 1), '%Y-%m')::DATE AS periodo,
    lpep_pickup_datetime AS pickup_datetime,
    lpep_dropoff_datetime AS dropoff_datetime,
    * EXCLUDE (lpep_pickup_datetime, lpep_dropoff_datetime, cbd_congestion_fee, filename),
    coalesce(cbd_congestion_fee, 0) AS cbd_congestion_fee
FROM read_parquet('data/raw/green/*/*.parquet', union_by_name = true, filename = true);

-- Viajes que cumplen las reglas de calidad definidas en el ejercicio 3
CREATE OR REPLACE VIEW viajes_validos AS
SELECT
    *,
    epoch(dropoff_datetime - pickup_datetime) / 60 AS duracion_min
FROM viajes
WHERE date_trunc('month', pickup_datetime) = periodo
  AND dropoff_datetime > pickup_datetime
  AND dropoff_datetime - pickup_datetime <= INTERVAL 3 HOUR
  AND trip_distance > 0
  AND trip_distance <= 100
  AND trip_distance / (epoch(dropoff_datetime - pickup_datetime) / 3600) <= 80
  AND fare_amount >= 0
  AND total_amount > 0;

-- Catálogo de zonas de la TLC
CREATE OR REPLACE VIEW zonas AS
SELECT LocationID AS zona_id, Borough AS distrito, Zone AS zona
FROM read_csv('data/raw/zonas/taxi_zone_lookup.csv');
