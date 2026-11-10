--
-- PostgreSQL database dump
--

\restrict xhxelI7A4Rk5X1Y9itgbAwxFkYrGskEepOJOcvbuqpp2uZ2pDFz3BjmsXWdDdc2

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
-- Name: fema_disasters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fema_disasters (
    id bigint NOT NULL,
    disaster_number integer,
    state character varying(2),
    declaration_type character varying(10),
    declaration_date timestamp with time zone,
    incident_type character varying(100),
    declaration_title text,
    incident_begin_date timestamp with time zone,
    incident_end_date timestamp with time zone,
    fips_state_code character varying(2),
    fips_county_code character varying(3),
    designated_area text,
    place_code character varying(10),
    last_refresh timestamp with time zone
);


--
-- Name: fema_disasters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.fema_disasters ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fema_disasters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: fema_disasters fema_disasters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fema_disasters
    ADD CONSTRAINT fema_disasters_pkey PRIMARY KEY (id);


--
-- Name: fema_disasters fema_disasters_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fema_disasters
    ADD CONSTRAINT fema_disasters_unique UNIQUE (disaster_number, state, place_code);


--
-- PostgreSQL database dump complete
--

\unrestrict xhxelI7A4Rk5X1Y9itgbAwxFkYrGskEepOJOcvbuqpp2uZ2pDFz3BjmsXWdDdc2

