--
-- PostgreSQL database dump
--

\restrict rUPFI3kzsWOVLCBhFOthp7AUqTelTSarXI6XSAKNUaveXKFVKBDghEQBlsNUe3Q

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
-- Name: earthquakes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.earthquakes (
    earthquake_id text NOT NULL,
    magnitude double precision,
    location text,
    event_time timestamp with time zone,
    longitude double precision,
    latitude double precision,
    depth_km double precision,
    tsunami integer,
    significance integer,
    status text,
    event_type text,
    detail_url text
);


--
-- Name: earthquakes earthquakes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.earthquakes
    ADD CONSTRAINT earthquakes_pkey PRIMARY KEY (earthquake_id);


--
-- PostgreSQL database dump complete
--

\unrestrict rUPFI3kzsWOVLCBhFOthp7AUqTelTSarXI6XSAKNUaveXKFVKBDghEQBlsNUe3Q

