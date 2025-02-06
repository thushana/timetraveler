--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15 (Homebrew)
-- Dumped by pg_dump version 14.15 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO thushan;

--
-- Name: days_of_week; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.days_of_week (
    id integer NOT NULL,
    day character varying(50) NOT NULL
);


ALTER TABLE public.days_of_week OWNER TO thushan;

--
-- Name: days_of_week_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.days_of_week_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.days_of_week_id_seq OWNER TO thushan;

--
-- Name: days_of_week_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.days_of_week_id_seq OWNED BY public.days_of_week.id;


--
-- Name: journey_legs; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journey_legs (
    id integer NOT NULL,
    journey_measurement_id integer NOT NULL,
    sequence_number smallint NOT NULL,
    start_waypoint_id integer NOT NULL,
    end_waypoint_id integer NOT NULL,
    duration_seconds integer NOT NULL,
    distance_meters numeric(10,2) NOT NULL,
    speed_kph numeric(5,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journey_legs OWNER TO thushan;

--
-- Name: journey_legs_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journey_legs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journey_legs_id_seq OWNER TO thushan;

--
-- Name: journey_legs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journey_legs_id_seq OWNED BY public.journey_legs.id;


--
-- Name: journey_measurements; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journey_measurements (
    id integer NOT NULL,
    journey_id integer NOT NULL,
    transit_mode_id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    local_timestamp timestamp with time zone NOT NULL,
    day_of_week_id integer NOT NULL,
    time_slot_id integer NOT NULL,
    duration_seconds integer NOT NULL,
    distance_meters numeric(10,2) NOT NULL,
    speed_kph numeric(5,2) NOT NULL,
    raw_response jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journey_measurements OWNER TO thushan;

--
-- Name: journey_measurements_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journey_measurements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journey_measurements_id_seq OWNER TO thushan;

--
-- Name: journey_measurements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journey_measurements_id_seq OWNED BY public.journey_measurements.id;


--
-- Name: journey_processing_history; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journey_processing_history (
    id integer NOT NULL,
    journey_id integer NOT NULL,
    processor_version character varying(50),
    success boolean NOT NULL,
    error_message text,
    processing_time_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journey_processing_history OWNER TO thushan;

--
-- Name: journey_processing_history_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journey_processing_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journey_processing_history_id_seq OWNER TO thushan;

--
-- Name: journey_processing_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journey_processing_history_id_seq OWNED BY public.journey_processing_history.id;


--
-- Name: journey_statuses; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journey_statuses (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.journey_statuses OWNER TO thushan;

--
-- Name: journey_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journey_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journey_statuses_id_seq OWNER TO thushan;

--
-- Name: journey_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journey_statuses_id_seq OWNED BY public.journey_statuses.id;


--
-- Name: journey_time_slice_stats; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journey_time_slice_stats (
    id integer NOT NULL,
    journey_id integer NOT NULL,
    transit_mode_id integer NOT NULL,
    day_of_week_id integer NOT NULL,
    time_slot_id integer NOT NULL,
    analysis_period integer NOT NULL,
    sample_start_date date NOT NULL,
    sample_end_date date NOT NULL,
    sample_count integer NOT NULL,
    avg_duration_seconds integer NOT NULL,
    min_duration_seconds integer NOT NULL,
    max_duration_seconds integer NOT NULL,
    std_dev_duration numeric(10,2) NOT NULL,
    p50_duration_seconds integer NOT NULL,
    p75_duration_seconds integer NOT NULL,
    p90_duration_seconds integer NOT NULL,
    p95_duration_seconds integer NOT NULL,
    avg_speed_kph numeric(5,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journey_time_slice_stats OWNER TO thushan;

--
-- Name: journey_time_slice_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journey_time_slice_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journey_time_slice_stats_id_seq OWNER TO thushan;

--
-- Name: journey_time_slice_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journey_time_slice_stats_id_seq OWNED BY public.journey_time_slice_stats.id;


--
-- Name: journey_waypoints; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journey_waypoints (
    id integer NOT NULL,
    journey_id integer NOT NULL,
    sequence_number smallint NOT NULL,
    place_id character varying(255) NOT NULL,
    plus_code character varying(20) NOT NULL,
    formatted_address text NOT NULL,
    latitude numeric(9,7) NOT NULL,
    longitude numeric(10,7) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journey_waypoints OWNER TO thushan;

--
-- Name: journey_waypoints_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journey_waypoints_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journey_waypoints_id_seq OWNER TO thushan;

--
-- Name: journey_waypoints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journey_waypoints_id_seq OWNED BY public.journey_waypoints.id;


--
-- Name: journeys; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.journeys (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    country character varying(100) NOT NULL,
    timezone text NOT NULL,
    status_id integer DEFAULT 1 NOT NULL,
    error_message text,
    maps_url text,
    raw_data jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journeys OWNER TO thushan;

--
-- Name: journeys_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.journeys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journeys_id_seq OWNER TO thushan;

--
-- Name: journeys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.journeys_id_seq OWNED BY public.journeys.id;


--
-- Name: mileage_rates; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.mileage_rates (
    id integer NOT NULL,
    rate_cents integer NOT NULL,
    effective_date date NOT NULL,
    end_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mileage_rates OWNER TO thushan;

--
-- Name: mileage_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.mileage_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mileage_rates_id_seq OWNER TO thushan;

--
-- Name: mileage_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.mileage_rates_id_seq OWNED BY public.mileage_rates.id;


--
-- Name: time_periods; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.time_periods (
    id integer NOT NULL,
    period character varying(50) NOT NULL
);


ALTER TABLE public.time_periods OWNER TO thushan;

--
-- Name: time_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.time_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.time_periods_id_seq OWNER TO thushan;

--
-- Name: time_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.time_periods_id_seq OWNED BY public.time_periods.id;


--
-- Name: time_slots; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.time_slots (
    id integer NOT NULL,
    slot character varying(50) NOT NULL
);


ALTER TABLE public.time_slots OWNER TO thushan;

--
-- Name: time_slots_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.time_slots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.time_slots_id_seq OWNER TO thushan;

--
-- Name: time_slots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.time_slots_id_seq OWNED BY public.time_slots.id;


--
-- Name: transit_modes; Type: TABLE; Schema: public; Owner: thushan
--

CREATE TABLE public.transit_modes (
    id integer NOT NULL,
    mode character varying(50) NOT NULL
);


ALTER TABLE public.transit_modes OWNER TO thushan;

--
-- Name: transit_modes_id_seq; Type: SEQUENCE; Schema: public; Owner: thushan
--

CREATE SEQUENCE public.transit_modes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transit_modes_id_seq OWNER TO thushan;

--
-- Name: transit_modes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: thushan
--

ALTER SEQUENCE public.transit_modes_id_seq OWNED BY public.transit_modes.id;


--
-- Name: days_of_week id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.days_of_week ALTER COLUMN id SET DEFAULT nextval('public.days_of_week_id_seq'::regclass);


--
-- Name: journey_legs id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_legs ALTER COLUMN id SET DEFAULT nextval('public.journey_legs_id_seq'::regclass);


--
-- Name: journey_measurements id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements ALTER COLUMN id SET DEFAULT nextval('public.journey_measurements_id_seq'::regclass);


--
-- Name: journey_processing_history id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_processing_history ALTER COLUMN id SET DEFAULT nextval('public.journey_processing_history_id_seq'::regclass);


--
-- Name: journey_statuses id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_statuses ALTER COLUMN id SET DEFAULT nextval('public.journey_statuses_id_seq'::regclass);


--
-- Name: journey_time_slice_stats id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats ALTER COLUMN id SET DEFAULT nextval('public.journey_time_slice_stats_id_seq'::regclass);


--
-- Name: journey_waypoints id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_waypoints ALTER COLUMN id SET DEFAULT nextval('public.journey_waypoints_id_seq'::regclass);


--
-- Name: journeys id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journeys ALTER COLUMN id SET DEFAULT nextval('public.journeys_id_seq'::regclass);


--
-- Name: mileage_rates id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.mileage_rates ALTER COLUMN id SET DEFAULT nextval('public.mileage_rates_id_seq'::regclass);


--
-- Name: time_periods id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.time_periods ALTER COLUMN id SET DEFAULT nextval('public.time_periods_id_seq'::regclass);


--
-- Name: time_slots id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.time_slots ALTER COLUMN id SET DEFAULT nextval('public.time_slots_id_seq'::regclass);


--
-- Name: transit_modes id; Type: DEFAULT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.transit_modes ALTER COLUMN id SET DEFAULT nextval('public.transit_modes_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.alembic_version (version_num) FROM stdin;
19ce8a520020
\.


--
-- Data for Name: days_of_week; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.days_of_week (id, day) FROM stdin;
1	Sunday
2	Monday
3	Tuesday
4	Wednesday
5	Thursday
6	Friday
7	Saturday
\.


--
-- Data for Name: journey_legs; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journey_legs (id, journey_measurement_id, sequence_number, start_waypoint_id, end_waypoint_id, duration_seconds, distance_meters, speed_kph, created_at) FROM stdin;
1	1	1	32	37	7061	8608.00	4.39	2025-02-05 05:36:17.200131-08
2	2	1	32	33	385	2215.00	20.71	2025-02-05 05:36:17.200131-08
3	2	2	33	34	380	3318.00	31.43	2025-02-05 05:36:17.200131-08
4	2	3	34	35	189	1699.00	32.36	2025-02-05 05:36:17.200131-08
5	2	4	35	36	82	591.00	25.95	2025-02-05 05:36:17.200131-08
6	2	5	36	37	169	1213.00	25.84	2025-02-05 05:36:17.200131-08
9	6	1	32	37	1839	9416.00	18.43	2025-02-05 06:03:31.820646-08
10	7	1	32	37	2176	12528.00	20.73	2025-02-05 06:03:31.820646-08
11	8	1	27	31	2215	11531.00	18.74	2025-02-05 06:03:32.174682-08
12	9	1	27	31	1213	10202.00	30.28	2025-02-05 06:03:32.174682-08
13	10	1	27	31	8109	9828.00	4.36	2025-02-05 06:03:32.174682-08
14	9	2	28	29	267	2591.00	34.93	2025-02-05 06:03:32.174682-08
15	9	3	29	30	312	1906.00	21.99	2025-02-05 06:03:32.174682-08
16	9	4	30	31	145	1075.00	26.69	2025-02-05 06:03:32.174682-08
17	11	1	27	31	3558	15590.00	15.77	2025-02-05 06:03:32.174682-08
\.


--
-- Data for Name: journey_measurements; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journey_measurements (id, journey_id, transit_mode_id, "timestamp", local_timestamp, day_of_week_id, time_slot_id, duration_seconds, distance_meters, speed_kph, raw_response, created_at) FROM stdin;
11	3	5	2025-02-06 11:13:49.347888-08	2025-02-06 11:13:49.347888-08	3	1	3809	11387.00	10.76	{"metrics": {"speed_kph": 10.762194801785245, "distance_meters": 11387, "duration_seconds": 3809}, "leg_details": [{"speed_kph": 10.762194801785245, "end_address": "2700 5th St, Alameda, CA 94501, USA", "start_address": "152 Sweet Rd, Alameda, CA 94502, USA", "distance_meters": 11387, "duration_seconds": 3809}]}	2025-02-05 06:03:32.174682-08
7	4	5	2025-02-06 11:13:48.804876-08	2025-02-06 11:13:48.804876-08	3	1	2446	14481.00	21.31	{"metrics": {"speed_kph": 21.31300081766149, "distance_meters": 14481, "duration_seconds": 2446}, "leg_details": [{"speed_kph": 21.31300081766149, "end_address": "2 Saratoga St, Alameda, CA 94501, USA", "start_address": "Fruitvale, 3401 E 12th St, Oakland, CA 94601, USA", "distance_meters": 14481, "duration_seconds": 2446}]}	2025-02-05 06:03:31.820646-08
1	4	4	2025-02-06 11:13:48.804876-08	2025-02-06 11:13:48.804876-08	3	23	7031	8573.00	4.39	{"metrics": {"speed_kph": 4.389532072251458, "distance_meters": 8573, "duration_seconds": 7031}, "leg_details": [{"speed_kph": 4.389532072251458, "end_address": "2 Saratoga St, Alameda, CA 94501, USA", "start_address": "Fruitvale, 3401 E 12th St, Oakland, CA 94601, USA", "distance_meters": 8573, "duration_seconds": 7031}]}	2025-02-05 05:36:17.200131-08
6	4	3	2025-02-06 11:13:48.804876-08	2025-02-06 11:13:48.804876-08	3	1	1839	9418.00	18.44	{"metrics": {"speed_kph": 18.43654159869494, "distance_meters": 9418, "duration_seconds": 1839}, "leg_details": [{"speed_kph": 18.43654159869494, "end_address": "2 Saratoga St, Alameda, CA 94501, USA", "start_address": "Fruitvale, 3401 E 12th St, Oakland, CA 94601, USA", "distance_meters": 9418, "duration_seconds": 1839}]}	2025-02-05 06:03:31.820646-08
8	3	3	2025-02-06 11:13:49.347888-08	2025-02-06 11:13:49.347888-08	3	1	2217	11535.00	18.73	{"metrics": {"speed_kph": 18.730717185385657, "distance_meters": 11535, "duration_seconds": 2217}, "leg_details": [{"speed_kph": 18.730717185385657, "end_address": "2700 5th St, Alameda, CA 94501, USA", "start_address": "152 Sweet Rd, Alameda, CA 94502, USA", "distance_meters": 11535, "duration_seconds": 2217}]}	2025-02-05 06:03:32.174682-08
10	3	4	2025-02-06 11:13:49.347888-08	2025-02-06 11:13:49.347888-08	3	1	8108	9828.00	4.36	{"metrics": {"speed_kph": 4.363690182535767, "distance_meters": 9828, "duration_seconds": 8108}, "leg_details": [{"speed_kph": 4.363690182535767, "end_address": "2700 5th St, Alameda, CA 94501, USA", "start_address": "152 Sweet Rd, Alameda, CA 94502, USA", "distance_meters": 9828, "duration_seconds": 8108}]}	2025-02-05 06:03:32.174682-08
2	4	1	2025-02-06 11:13:48.804876-08	2025-02-06 11:13:48.804876-08	3	23	985	11139.00	40.71	{"metrics": {"speed_kph": 40.71106598984771, "distance_meters": 11139, "duration_seconds": 985}, "leg_details": [{"speed_kph": 40.71106598984771, "end_address": "2 Saratoga St, Alameda, CA 94501, USA", "start_address": "Fruitvale, 3401 E 12th St, Oakland, CA 94601, USA", "distance_meters": 11139, "duration_seconds": 985}]}	2025-02-05 05:36:17.200131-08
9	3	1	2025-02-06 11:13:49.347888-08	2025-02-06 11:13:49.347888-08	3	1	1213	10202.00	30.28	{"metrics": {"speed_kph": 30.277988458367684, "distance_meters": 10202, "duration_seconds": 1213}, "leg_details": [{"speed_kph": 30.277988458367684, "end_address": "2700 5th St, Alameda, CA 94501, USA", "start_address": "152 Sweet Rd, Alameda, CA 94502, USA", "distance_meters": 10202, "duration_seconds": 1213}]}	2025-02-05 06:03:32.174682-08
\.


--
-- Data for Name: journey_processing_history; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journey_processing_history (id, journey_id, processor_version, success, error_message, processing_time_ms, created_at) FROM stdin;
\.


--
-- Data for Name: journey_statuses; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journey_statuses (id, status) FROM stdin;
1	active
2	error
3	disabled
\.


--
-- Data for Name: journey_time_slice_stats; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journey_time_slice_stats (id, journey_id, transit_mode_id, day_of_week_id, time_slot_id, analysis_period, sample_start_date, sample_end_date, sample_count, avg_duration_seconds, min_duration_seconds, max_duration_seconds, std_dev_duration, p50_duration_seconds, p75_duration_seconds, p90_duration_seconds, p95_duration_seconds, avg_speed_kph, created_at) FROM stdin;
\.


--
-- Data for Name: journey_waypoints; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journey_waypoints (id, journey_id, sequence_number, place_id, plus_code, formatted_address, latitude, longitude, created_at) FROM stdin;
27	3	1	ChIJm7F2UQSEj4ARSeNPlO18Yss	PPQR+8V	152 Sweet Rd, Alameda, CA 94502, USA	37.7383125	-122.2578125	2025-02-04 21:08:59.062722-08
28	3	2	ChIJC2CJVLuGj4ARlK_Wn1-4cEc	QQ52+4G	Otis Dr & Park St, Alameda, CA 94501, USA	37.7578125	-122.2486875	2025-02-04 21:08:59.062722-08
29	3	3	ChIJMSpy3DGBj4ARcIodBUFiMqE	QP9G+HV	8th St & Portola Av, Alameda, CA 94501, USA	37.7689375	-122.2728125	2025-02-04 21:08:59.062722-08
30	3	4	ChIJR_7sS9mAj4ARBU8T4yEpt-4	QPH9+X5	501 Atlantic Ave, Alameda, CA 94501, USA	37.7799375	-122.2820625	2025-02-04 21:08:59.062722-08
31	3	5	ChIJOwp5iEaBj4ARZRjmiUzfyh8	QPQ9+GW	2700 5th St, Alameda, CA 94501, USA	37.7888125	-122.2801875	2025-02-04 21:08:59.062722-08
32	4	1	ChIJz4AExvSGj4ARvOzq5KnZgTw	QQFG+W9	Fruitvale, 3401 E 12th St, Oakland, CA 94601, USA	37.7748125	-122.2240625	2025-02-04 21:09:02.129695-08
33	4	2	ChIJv6XAdpWGj4ARLYtATaUEOKA	QQ85+R7	2315 Lincoln Ave Unit 2, Alameda, CA 94501, USA	37.7670625	-122.2418125	2025-02-04 21:09:02.129695-08
34	4	3	ChIJPxBd0yeBj4ARIQOABo6mkfE	QPGF+44	Lincoln Av & Webster St, Alameda, CA 94501, USA	37.7753125	-122.2771875	2025-02-04 21:09:02.129695-08
35	4	4	ChIJN7VQrmmBj4ARN4OovH__Qv0	QPJ5+37	53 W Atlantic Ave, Alameda, CA 94501, USA	37.7801875	-122.2918125	2025-02-04 21:09:02.129695-08
36	4	5	ChIJJ2HkI5OBj4ARByz4oyMtJcA	QPJ2+27	Alameda Waterfront Park, 2151 Ferry Point, Alameda, CA 94501, USA	37.7800625	-122.2993125	2025-02-04 21:09:02.129695-08
37	4	6	ChIJB-A5B_OAj4ARsljzBO-WG0E	QMPW+PR	2 Saratoga St, Alameda, CA 94501, USA	37.7868125	-122.3029375	2025-02-04 21:09:02.129695-08
\.


--
-- Data for Name: journeys; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.journeys (id, name, description, city, state, country, timezone, status_id, error_message, maps_url, raw_data, created_at, updated_at) FROM stdin;
4	Transcontinental Railroad	Fruitvale BART down the Frutivale Bridge and the historic path of the Transcontinal Railroad to the historic marker at the Alameda Point	Oakland	California	United States	America/Los_Angeles	1	\N	https://www.google.com/maps/place/Alameda+Waterfront+Park/@37.7786853,-122.303658,15.83z/data=!4m51!1m44!4m43!1m6!1m2!1s0x80857d8b28aaed03:0xdfdc5a060b97fbe9!2sQQFG%2BW9,+Oakland,+CA!2m2!1d-122.2240625!2d37.7748125!1m6!1m2!1s0x808f80d8f2cf1595:0x4f44ab6dc65761af!2sQQ85%2BR7,+Alameda,+CA!2m2!1d-122.2418125!2d37.7670625!1m6!1m2!1s0x808f80d8f2cf1595:0x9c5f520d9ac5b1d4!2sQPGF%2B44,+Alameda,+CA!2m2!1d-122.2771875!2d37.7753125!1m6!1m2!1s0x808f80d8f2cf1595:0xe3ac9b2019a56c1!2sQPJ5%2B37,+Alameda,+CA!2m2!1d-122.2918125!2d37.7801875!1m6!1m2!1s0x808f80d8f2cf1595:0xdc3b03b0873794d4!2sQPJ2%2B27,+Alameda,+CA!2m2!1d-122.2993125!2d37.7800625!1m6!1m2!1s0x808f80d8f2cf1595:0xa51943f2b82cf30e!2sQMPW%2BPR,+Alameda,+CA!2m2!1d-122.3029375!2d37.7868125!3e0!3m5!1s0x808f819323e46127:0xc0252d23a3f82c07!8m2!3d37.7801217!4d-122.2993004!16s%2Fg%2F11rtmr6ybq!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D	{"url": "https://www.google.com/maps/place/Alameda+Waterfront+Park/@37.7786853,-122.303658,15.83z/data=!4m51!1m44!4m43!1m6!1m2!1s0x80857d8b28aaed03:0xdfdc5a060b97fbe9!2sQQFG%2BW9,+Oakland,+CA!2m2!1d-122.2240625!2d37.7748125!1m6!1m2!1s0x808f80d8f2cf1595:0x4f44ab6dc65761af!2sQQ85%2BR7,+Alameda,+CA!2m2!1d-122.2418125!2d37.7670625!1m6!1m2!1s0x808f80d8f2cf1595:0x9c5f520d9ac5b1d4!2sQPGF%2B44,+Alameda,+CA!2m2!1d-122.2771875!2d37.7753125!1m6!1m2!1s0x808f80d8f2cf1595:0xe3ac9b2019a56c1!2sQPJ5%2B37,+Alameda,+CA!2m2!1d-122.2918125!2d37.7801875!1m6!1m2!1s0x808f80d8f2cf1595:0xdc3b03b0873794d4!2sQPJ2%2B27,+Alameda,+CA!2m2!1d-122.2993125!2d37.7800625!1m6!1m2!1s0x808f80d8f2cf1595:0xa51943f2b82cf30e!2sQMPW%2BPR,+Alameda,+CA!2m2!1d-122.3029375!2d37.7868125!3e0!3m5!1s0x808f819323e46127:0xc0252d23a3f82c07!8m2!3d37.7801217!4d-122.2993004!16s%2Fg%2F11rtmr6ybq!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D"}	2025-02-04 20:25:58.318019-08	2025-02-04 21:09:02.129695-08
3	Target Run	Furthest reach of Bay Farm, over Bay Farm Bridge, down Otis, and then on to Target	Alameda	California	United States	America/Los_Angeles	1	\N	https://www.google.com/maps/place/Shoreline+Park/@37.7622754,-122.279488,14z/data=!4m44!1m37!4m36!1m6!1m2!1s0x808f80d8f2cf1595:0xdf3815440c2316a8!2sPPQR%2B8V,+Alameda,+CA!2m2!1d-122.2578125!2d37.7383125!1m6!1m2!1s0x808f80d8f2cf1595:0xa0535ce0470d94a0!2sQQ52%2B4G,+Alameda,+CA!2m2!1d-122.2486875!2d37.7578125!1m6!1m2!1s0x808f80d8f2cf1595:0xf8fd790e72f5df59!2sQP9G%2BHV,+Alameda,+CA!2m2!1d-122.2728125!2d37.7689375!1m6!1m2!1s0x808f80d8f2cf1595:0xec9c663130539b34!2sQPH9%2BX5,+Alameda,+CA!2m2!1d-122.2820625!2d37.7799375!1m6!1m2!1s0x808f80d8f2cf1595:0x1684cd7f70336f0a!2sQPQ9%2BGW,+Alameda,+CA!2m2!1d-122.2801875!2d37.7888125!3e0!3m5!1s0x808f84043e16cf93:0x7b079dc2c1863ff8!8m2!3d37.7382887!4d-122.2577644!16s%2Fg%2F1tq8jsss!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D	{"url": "https://www.google.com/maps/place/Shoreline+Park/@37.7622754,-122.279488,14z/data=!4m44!1m37!4m36!1m6!1m2!1s0x808f80d8f2cf1595:0xdf3815440c2316a8!2sPPQR%2B8V,+Alameda,+CA!2m2!1d-122.2578125!2d37.7383125!1m6!1m2!1s0x808f80d8f2cf1595:0xa0535ce0470d94a0!2sQQ52%2B4G,+Alameda,+CA!2m2!1d-122.2486875!2d37.7578125!1m6!1m2!1s0x808f80d8f2cf1595:0xf8fd790e72f5df59!2sQP9G%2BHV,+Alameda,+CA!2m2!1d-122.2728125!2d37.7689375!1m6!1m2!1s0x808f80d8f2cf1595:0xec9c663130539b34!2sQPH9%2BX5,+Alameda,+CA!2m2!1d-122.2820625!2d37.7799375!1m6!1m2!1s0x808f80d8f2cf1595:0x1684cd7f70336f0a!2sQPQ9%2BGW,+Alameda,+CA!2m2!1d-122.2801875!2d37.7888125!3e0!3m5!1s0x808f84043e16cf93:0x7b079dc2c1863ff8!8m2!3d37.7382887!4d-122.2577644!16s%2Fg%2F1tq8jsss!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D"}	2025-02-04 20:25:55.424696-08	2025-02-04 21:08:59.062722-08
\.


--
-- Data for Name: mileage_rates; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.mileage_rates (id, rate_cents, effective_date, end_date, created_at) FROM stdin;
\.


--
-- Data for Name: time_periods; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.time_periods (id, period) FROM stdin;
1	overnight
2	dawn
3	morning
4	afternoon
5	evening
6	night
\.


--
-- Data for Name: time_slots; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.time_slots (id, slot) FROM stdin;
1	00_00_overnight
2	00_15_overnight
3	00_30_overnight
4	00_45_overnight
5	01_00_overnight
6	01_15_overnight
7	01_30_overnight
8	01_45_overnight
9	02_00_overnight
10	02_15_overnight
11	02_30_overnight
12	02_45_overnight
13	03_00_overnight
14	03_15_overnight
15	03_30_overnight
16	03_45_overnight
17	04_00_dawn
18	04_15_dawn
19	04_30_dawn
20	04_45_dawn
21	05_00_dawn
22	05_15_dawn
23	05_30_dawn
24	05_45_dawn
25	06_00_dawn
26	06_15_dawn
27	06_30_dawn
28	06_45_dawn
29	07_00_dawn
30	07_15_dawn
31	07_30_dawn
32	07_45_dawn
33	08_00_morning
34	08_15_morning
35	08_30_morning
36	08_45_morning
37	09_00_morning
38	09_15_morning
39	09_30_morning
40	09_45_morning
41	10_00_morning
42	10_15_morning
43	10_30_morning
44	10_45_morning
45	11_00_morning
46	11_15_morning
47	11_30_morning
48	11_45_morning
49	12_00_afternoon
50	12_15_afternoon
51	12_30_afternoon
52	12_45_afternoon
53	13_00_afternoon
54	13_15_afternoon
55	13_30_afternoon
56	13_45_afternoon
57	14_00_afternoon
58	14_15_afternoon
59	14_30_afternoon
60	14_45_afternoon
61	15_00_afternoon
62	15_15_afternoon
63	15_30_afternoon
64	15_45_afternoon
65	16_00_evening
66	16_15_evening
67	16_30_evening
68	16_45_evening
69	17_00_evening
70	17_15_evening
71	17_30_evening
72	17_45_evening
73	18_00_evening
74	18_15_evening
75	18_30_evening
76	18_45_evening
77	19_00_evening
78	19_15_evening
79	19_30_evening
80	19_45_evening
81	20_00_night
82	20_15_night
83	20_30_night
84	20_45_night
85	21_00_night
86	21_15_night
87	21_30_night
88	21_45_night
89	22_00_night
90	22_15_night
91	22_30_night
92	22_45_night
93	23_00_night
94	23_15_night
95	23_30_night
96	23_45_night
\.


--
-- Data for Name: transit_modes; Type: TABLE DATA; Schema: public; Owner: thushan
--

COPY public.transit_modes (id, mode) FROM stdin;
1	driving
2	driving_routed
3	bicycling
4	walking
5	transit
\.


--
-- Name: days_of_week_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.days_of_week_id_seq', 7, true);


--
-- Name: journey_legs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journey_legs_id_seq', 17, true);


--
-- Name: journey_measurements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journey_measurements_id_seq', 11, true);


--
-- Name: journey_processing_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journey_processing_history_id_seq', 1, false);


--
-- Name: journey_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journey_statuses_id_seq', 3, true);


--
-- Name: journey_time_slice_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journey_time_slice_stats_id_seq', 1, false);


--
-- Name: journey_waypoints_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journey_waypoints_id_seq', 37, true);


--
-- Name: journeys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.journeys_id_seq', 6, true);


--
-- Name: mileage_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.mileage_rates_id_seq', 1, false);


--
-- Name: time_periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.time_periods_id_seq', 6, true);


--
-- Name: time_slots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.time_slots_id_seq', 96, true);


--
-- Name: transit_modes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: thushan
--

SELECT pg_catalog.setval('public.transit_modes_id_seq', 5, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: days_of_week days_of_week_day_key; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.days_of_week
    ADD CONSTRAINT days_of_week_day_key UNIQUE (day);


--
-- Name: days_of_week days_of_week_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.days_of_week
    ADD CONSTRAINT days_of_week_pkey PRIMARY KEY (id);


--
-- Name: journey_legs journey_legs_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_legs
    ADD CONSTRAINT journey_legs_pkey PRIMARY KEY (id);


--
-- Name: journey_measurements journey_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements
    ADD CONSTRAINT journey_measurements_pkey PRIMARY KEY (id);


--
-- Name: journey_processing_history journey_processing_history_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_processing_history
    ADD CONSTRAINT journey_processing_history_pkey PRIMARY KEY (id);


--
-- Name: journey_statuses journey_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_statuses
    ADD CONSTRAINT journey_statuses_pkey PRIMARY KEY (id);


--
-- Name: journey_statuses journey_statuses_status_key; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_statuses
    ADD CONSTRAINT journey_statuses_status_key UNIQUE (status);


--
-- Name: journey_time_slice_stats journey_time_slice_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats
    ADD CONSTRAINT journey_time_slice_stats_pkey PRIMARY KEY (id);


--
-- Name: journey_waypoints journey_waypoints_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_waypoints
    ADD CONSTRAINT journey_waypoints_pkey PRIMARY KEY (id);


--
-- Name: journeys journeys_name_key; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journeys
    ADD CONSTRAINT journeys_name_key UNIQUE (name);


--
-- Name: journeys journeys_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journeys
    ADD CONSTRAINT journeys_pkey PRIMARY KEY (id);


--
-- Name: mileage_rates mileage_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.mileage_rates
    ADD CONSTRAINT mileage_rates_pkey PRIMARY KEY (id);


--
-- Name: time_periods time_periods_period_key; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.time_periods
    ADD CONSTRAINT time_periods_period_key UNIQUE (period);


--
-- Name: time_periods time_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.time_periods
    ADD CONSTRAINT time_periods_pkey PRIMARY KEY (id);


--
-- Name: time_slots time_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT time_slots_pkey PRIMARY KEY (id);


--
-- Name: time_slots time_slots_slot_key; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.time_slots
    ADD CONSTRAINT time_slots_slot_key UNIQUE (slot);


--
-- Name: transit_modes transit_modes_mode_key; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.transit_modes
    ADD CONSTRAINT transit_modes_mode_key UNIQUE (mode);


--
-- Name: transit_modes transit_modes_pkey; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.transit_modes
    ADD CONSTRAINT transit_modes_pkey PRIMARY KEY (id);


--
-- Name: mileage_rates uq_effective_date; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.mileage_rates
    ADD CONSTRAINT uq_effective_date UNIQUE (effective_date);


--
-- Name: journey_legs uq_journey_leg; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_legs
    ADD CONSTRAINT uq_journey_leg UNIQUE (journey_measurement_id, sequence_number);


--
-- Name: journey_measurements uq_journey_measurement; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements
    ADD CONSTRAINT uq_journey_measurement UNIQUE (journey_id, transit_mode_id);


--
-- Name: journey_waypoints uq_journey_place; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_waypoints
    ADD CONSTRAINT uq_journey_place UNIQUE (journey_id, place_id);


--
-- Name: journey_waypoints uq_journey_sequence; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_waypoints
    ADD CONSTRAINT uq_journey_sequence UNIQUE (journey_id, sequence_number);


--
-- Name: journey_time_slice_stats uq_journey_time_slice_stats; Type: CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats
    ADD CONSTRAINT uq_journey_time_slice_stats UNIQUE (journey_id, transit_mode_id, day_of_week_id, time_slot_id, analysis_period);


--
-- Name: journey_legs journey_legs_end_waypoint_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_legs
    ADD CONSTRAINT journey_legs_end_waypoint_id_fkey FOREIGN KEY (end_waypoint_id) REFERENCES public.journey_waypoints(id);


--
-- Name: journey_legs journey_legs_journey_measurement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_legs
    ADD CONSTRAINT journey_legs_journey_measurement_id_fkey FOREIGN KEY (journey_measurement_id) REFERENCES public.journey_measurements(id);


--
-- Name: journey_legs journey_legs_start_waypoint_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_legs
    ADD CONSTRAINT journey_legs_start_waypoint_id_fkey FOREIGN KEY (start_waypoint_id) REFERENCES public.journey_waypoints(id);


--
-- Name: journey_measurements journey_measurements_day_of_week_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements
    ADD CONSTRAINT journey_measurements_day_of_week_id_fkey FOREIGN KEY (day_of_week_id) REFERENCES public.days_of_week(id);


--
-- Name: journey_measurements journey_measurements_journey_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements
    ADD CONSTRAINT journey_measurements_journey_id_fkey FOREIGN KEY (journey_id) REFERENCES public.journeys(id);


--
-- Name: journey_measurements journey_measurements_time_slot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements
    ADD CONSTRAINT journey_measurements_time_slot_id_fkey FOREIGN KEY (time_slot_id) REFERENCES public.time_slots(id);


--
-- Name: journey_measurements journey_measurements_transit_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_measurements
    ADD CONSTRAINT journey_measurements_transit_mode_id_fkey FOREIGN KEY (transit_mode_id) REFERENCES public.transit_modes(id);


--
-- Name: journey_processing_history journey_processing_history_journey_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_processing_history
    ADD CONSTRAINT journey_processing_history_journey_id_fkey FOREIGN KEY (journey_id) REFERENCES public.journeys(id);


--
-- Name: journey_time_slice_stats journey_time_slice_stats_day_of_week_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats
    ADD CONSTRAINT journey_time_slice_stats_day_of_week_id_fkey FOREIGN KEY (day_of_week_id) REFERENCES public.days_of_week(id);


--
-- Name: journey_time_slice_stats journey_time_slice_stats_journey_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats
    ADD CONSTRAINT journey_time_slice_stats_journey_id_fkey FOREIGN KEY (journey_id) REFERENCES public.journeys(id);


--
-- Name: journey_time_slice_stats journey_time_slice_stats_time_slot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats
    ADD CONSTRAINT journey_time_slice_stats_time_slot_id_fkey FOREIGN KEY (time_slot_id) REFERENCES public.time_slots(id);


--
-- Name: journey_time_slice_stats journey_time_slice_stats_transit_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_time_slice_stats
    ADD CONSTRAINT journey_time_slice_stats_transit_mode_id_fkey FOREIGN KEY (transit_mode_id) REFERENCES public.transit_modes(id);


--
-- Name: journey_waypoints journey_waypoints_journey_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journey_waypoints
    ADD CONSTRAINT journey_waypoints_journey_id_fkey FOREIGN KEY (journey_id) REFERENCES public.journeys(id);


--
-- Name: journeys journeys_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: thushan
--

ALTER TABLE ONLY public.journeys
    ADD CONSTRAINT journeys_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.journey_statuses(id);


--
-- PostgreSQL database dump complete
--

