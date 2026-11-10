--
-- PostgreSQL database dump
--

\restrict l2L8xVFnIOTYzaMvhGscwoTA5XCowIKtdPayLTumaynOU7oVJNO9GwP15vDwaYO

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: noaa_storms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.noaa_storms (
    episode_id bigint,
    event_id bigint NOT NULL,
    year integer,
    month character varying(20),
    state character varying(100),
    state_fips character varying(10),
    event_type character varying(100),
    county_zone_type character varying(10),
    county_zone_fips character varying(10),
    county_zone_name character varying(150),
    weather_forecast_office character varying(20),
    begin_date_time timestamp with time zone,
    end_date_time timestamp with time zone,
    timezone character varying(20),
    injuries_direct integer,
    injuries_indirect integer,
    deaths_direct integer,
    deaths_indirect integer,
    property_damage_usd numeric(18,2),
    crop_damage_usd numeric(18,2),
    source text,
    magnitude double precision,
    magnitude_type character varying(20),
    flood_cause text,
    tornado_scale character varying(20),
    tornado_length double precision,
    tornado_width double precision,
    begin_location text,
    end_location text,
    begin_latitude double precision,
    begin_longitude double precision,
    end_latitude double precision,
    end_longitude double precision,
    episode_narrative text,
    event_narrative text
);


--
-- Name: noaa_storms noaa_storms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.noaa_storms
    ADD CONSTRAINT noaa_storms_pkey PRIMARY KEY (event_id);


--
-- PostgreSQL database dump complete
--

\unrestrict l2L8xVFnIOTYzaMvhGscwoTA5XCowIKtdPayLTumaynOU7oVJNO9GwP15vDwaYO

