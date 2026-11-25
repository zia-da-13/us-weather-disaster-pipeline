
CREATE TABLE IF NOT EXISTS weather_forecasts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location VARCHAR(100) NOT NULL DEFAULT 'Nashville, TN',
    period_name VARCHAR(100),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    is_daytime BOOLEAN,
    temperature INTEGER,
    temperature_unit VARCHAR(5),
    precipitation_chance INTEGER,
    wind_speed VARCHAR(50),
    wind_direction VARCHAR(20),
    short_forecast TEXT,
    detailed_forecast TEXT,
    UNIQUE (location, start_time)
);
