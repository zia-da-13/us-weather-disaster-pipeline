
-- =====================================================
-- U.S. Weather & Disaster Intelligence Pipeline
-- NOAA Storm Events Data Quality Validation
-- =====================================================

-- 1. Total records
SELECT COUNT(*) AS total_records
FROM noaa_storms;

-- 2. Missing timestamps
SELECT COUNT(*) AS missing_timestamps
FROM noaa_storms
WHERE begin_date_time IS NULL
   OR end_date_time IS NULL;

-- 3. Invalid date ranges
SELECT COUNT(*) AS invalid_date_ranges
FROM noaa_storms
WHERE end_date_time < begin_date_time;

-- 4. Duplicate event IDs
SELECT event_id, COUNT(*) AS duplicate_count
FROM noaa_storms
GROUP BY event_id
HAVING COUNT(*) > 1;

-- 5. Missing event IDs
SELECT COUNT(*) AS missing_event_ids
FROM noaa_storms
WHERE event_id IS NULL;

-- 6. Missing event types
SELECT COUNT(*) AS missing_event_types
FROM noaa_storms
WHERE event_type IS NULL
   OR TRIM(event_type) = '';

-- 7. Negative damage values
SELECT COUNT(*) AS negative_damage_records
FROM noaa_storms
WHERE property_damage_usd < 0
   OR crop_damage_usd < 0;

-- 8. Negative casualty values
SELECT COUNT(*) AS negative_casualty_records
FROM noaa_storms
WHERE injuries_direct < 0
   OR injuries_indirect < 0
   OR deaths_direct < 0
   OR deaths_indirect < 0;

-- 9. Missing state names
SELECT COUNT(*) AS missing_state_records
FROM noaa_storms
WHERE state IS NULL
   OR TRIM(state) = '';

-- 10. Invalid geographic coordinates
SELECT COUNT(*) AS invalid_coordinates
FROM noaa_storms
WHERE begin_latitude NOT BETWEEN -90 AND 90
   OR end_latitude NOT BETWEEN -90 AND 90
   OR begin_longitude NOT BETWEEN -180 AND 180
   OR end_longitude NOT BETWEEN -180 AND 180;

-- 11. Missing geographic coordinates
SELECT COUNT(*) AS missing_coordinate_records
FROM noaa_storms
WHERE begin_latitude IS NULL
   OR begin_longitude IS NULL
   OR end_latitude IS NULL
   OR end_longitude IS NULL;

-- 12. Missing coordinates by event type
SELECT event_type, COUNT(*) AS missing_coordinates
FROM noaa_storms
WHERE begin_latitude IS NULL
   OR begin_longitude IS NULL
   OR end_latitude IS NULL
   OR end_longitude IS NULL
GROUP BY event_type
ORDER BY missing_coordinates DESC;

-- 13. Coordinate completeness by event type
SELECT
    event_type,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (
        WHERE begin_latitude IS NOT NULL
          AND begin_longitude IS NOT NULL
          AND end_latitude IS NOT NULL
          AND end_longitude IS NOT NULL
    ) AS complete_coordinates
FROM noaa_storms
GROUP BY event_type
ORDER BY total_events DESC;

-- 14. Missing casualty values
SELECT COUNT(*) AS missing_casualty_records
FROM noaa_storms
WHERE injuries_direct IS NULL
   OR injuries_indirect IS NULL
   OR deaths_direct IS NULL
   OR deaths_indirect IS NULL;

-- 15. Missing damage values
SELECT
    COUNT(*) FILTER (
        WHERE property_damage_usd IS NULL
    ) AS missing_property_damage,
    COUNT(*) FILTER (
        WHERE crop_damage_usd IS NULL
    ) AS missing_crop_damage
FROM noaa_storms;

-- 16. Missing damage by event type
SELECT
    event_type,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (
        WHERE property_damage_usd IS NULL
    ) AS missing_property_damage,
    COUNT(*) FILTER (
        WHERE crop_damage_usd IS NULL
    ) AS missing_crop_damage
FROM noaa_storms
GROUP BY event_type
ORDER BY total_events DESC;

-- 17. Missing year and month
SELECT
    COUNT(*) FILTER (
        WHERE year IS NULL
    ) AS missing_years,
    COUNT(*) FILTER (
        WHERE month IS NULL OR TRIM(month) = ''
    ) AS missing_months
FROM noaa_storms;

-- 18. Year distribution
SELECT year, COUNT(*) AS total_events
FROM noaa_storms
GROUP BY year
ORDER BY year;
