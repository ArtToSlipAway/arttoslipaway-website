--
-- PostgreSQL database dump
--

\restrict 0wKG2ZeeIk9N1eouIXhuJkCaMWoBcmNjVEqIqjxMN53er0eJV2g3KMW6G5nWlB3

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

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
-- Name: carousel_cards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.carousel_cards (
    id integer NOT NULL,
    target_key character varying(120) NOT NULL,
    label character varying(255) NOT NULL,
    subtitle text,
    link_url text,
    sort_order integer DEFAULT 100 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: carousel_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.carousel_cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: carousel_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.carousel_cards_id_seq OWNED BY public.carousel_cards.id;


--
-- Name: city_slots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.city_slots (
    id integer NOT NULL,
    city character varying(50) NOT NULL,
    date_label character varying(120) NOT NULL,
    slot_date date,
    slot_time character varying(50),
    status character varying(50) DEFAULT 'available'::character varying NOT NULL,
    note text,
    sort_order integer DEFAULT 100 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: city_slots_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.city_slots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: city_slots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.city_slots_id_seq OWNED BY public.city_slots.id;


--
-- Name: client_access_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_access_tokens (
    id integer NOT NULL,
    lead_id integer NOT NULL,
    token_hash character(64) NOT NULL,
    token_hint character varying(24),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    last_opened_at timestamp with time zone
);


--
-- Name: client_access_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.client_access_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: client_access_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.client_access_tokens_id_seq OWNED BY public.client_access_tokens.id;


--
-- Name: lead_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lead_files (
    id integer NOT NULL,
    lead_id integer NOT NULL,
    file_path text NOT NULL,
    original_filename text,
    file_type character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: lead_files_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lead_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lead_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lead_files_id_seq OWNED BY public.lead_files.id;


--
-- Name: leads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.leads (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    contact character varying(255) NOT NULL,
    contact_method character varying(100),
    project_interest character varying(255),
    body_place character varying(255),
    approximate_size character varying(255),
    idea text,
    message text,
    personal_data_agreement boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    project_id integer,
    project_title character varying(255),
    lead_status character varying(50) DEFAULT 'new'::character varying NOT NULL,
    admin_note text,
    category_slug character varying(255),
    category_title character varying(255),
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    lead_source character varying(100),
    entry_page text,
    service_type character varying(100),
    request_type character varying(100),
    city character varying(100),
    style_preference character varying(255),
    is_coverup boolean DEFAULT false,
    product_format character varying(255),
    deadline character varying(255),
    budget_range character varying(255),
    preferred_dates character varying(255),
    selected_media_id integer,
    selected_sketch_title text,
    lead_priority character varying(30) DEFAULT 'normal'::character varying,
    master_note text,
    archived_at timestamp with time zone,
    trashed_at timestamp with time zone
);


--
-- Name: leads_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.leads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: leads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.leads_id_seq OWNED BY public.leads.id;


--
-- Name: legal_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.legal_settings (
    setting_key character varying(120) NOT NULL,
    setting_value text DEFAULT ''::text NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: media_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.media_files (
    id integer NOT NULL,
    owner_type character varying(80),
    owner_id integer,
    block_key character varying(120),
    media_type character varying(50) NOT NULL,
    title character varying(255),
    alt_text text,
    file_path text NOT NULL,
    poster_path text,
    original_filename text,
    mime_type character varying(120),
    file_size bigint,
    sort_order integer DEFAULT 100 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    target_key character varying(120)
);


--
-- Name: media_files_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.media_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: media_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.media_files_id_seq OWNED BY public.media_files.id;


--
-- Name: project_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_categories (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    parent_slug character varying(255),
    category_group character varying(100) DEFAULT 'main'::character varying NOT NULL,
    short_description text,
    image_url character varying(500),
    display_order integer DEFAULT 100 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: project_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.project_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: project_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.project_categories_id_seq OWNED BY public.project_categories.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    project_type character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'available'::character varying NOT NULL,
    short_description text,
    full_description text,
    style character varying(255),
    format character varying(255),
    price character varying(255),
    image_url character varying(500),
    is_featured boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    display_order integer DEFAULT 100 NOT NULL,
    category_slug character varying(255)
);


--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: site_announcement; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_announcement (
    id smallint DEFAULT 1 NOT NULL,
    is_enabled boolean DEFAULT true NOT NULL,
    text text DEFAULT ''::text NOT NULL,
    desktop_seconds integer DEFAULT 85 NOT NULL,
    mobile_seconds integer DEFAULT 75 NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT site_announcement_id_check CHECK ((id = 1))
);


--
-- Name: site_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_events (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    visitor_id character varying(120),
    session_id character varying(120),
    event_type character varying(80) NOT NULL,
    path text,
    page_title text,
    referrer text,
    source text,
    utm_source text,
    utm_medium text,
    utm_campaign text,
    utm_content text,
    utm_term text,
    target_url text,
    target_text text,
    metadata jsonb,
    ip_hash character(64),
    user_agent text,
    is_admin boolean DEFAULT false NOT NULL
);


--
-- Name: site_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.site_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: site_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.site_events_id_seq OWNED BY public.site_events.id;


--
-- Name: site_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_settings (
    setting_key character varying(255) NOT NULL,
    setting_value text
);


--
-- Name: site_visits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site_visits (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    method character varying(12) NOT NULL,
    path text NOT NULL,
    referer text,
    user_agent text,
    ip_hash character(64),
    device_type character varying(32),
    browser character varying(80),
    status_code integer,
    response_time_ms integer,
    is_bot boolean DEFAULT false NOT NULL
);


--
-- Name: site_visits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.site_visits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: site_visits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.site_visits_id_seq OWNED BY public.site_visits.id;


--
-- Name: carousel_cards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carousel_cards ALTER COLUMN id SET DEFAULT nextval('public.carousel_cards_id_seq'::regclass);


--
-- Name: city_slots id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.city_slots ALTER COLUMN id SET DEFAULT nextval('public.city_slots_id_seq'::regclass);


--
-- Name: client_access_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_access_tokens ALTER COLUMN id SET DEFAULT nextval('public.client_access_tokens_id_seq'::regclass);


--
-- Name: lead_files id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lead_files ALTER COLUMN id SET DEFAULT nextval('public.lead_files_id_seq'::regclass);


--
-- Name: leads id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leads ALTER COLUMN id SET DEFAULT nextval('public.leads_id_seq'::regclass);


--
-- Name: media_files id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_files ALTER COLUMN id SET DEFAULT nextval('public.media_files_id_seq'::regclass);


--
-- Name: project_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_categories ALTER COLUMN id SET DEFAULT nextval('public.project_categories_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: site_events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_events ALTER COLUMN id SET DEFAULT nextval('public.site_events_id_seq'::regclass);


--
-- Name: site_visits id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_visits ALTER COLUMN id SET DEFAULT nextval('public.site_visits_id_seq'::regclass);


--
-- Name: carousel_cards carousel_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carousel_cards
    ADD CONSTRAINT carousel_cards_pkey PRIMARY KEY (id);


--
-- Name: carousel_cards carousel_cards_target_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carousel_cards
    ADD CONSTRAINT carousel_cards_target_key_key UNIQUE (target_key);


--
-- Name: city_slots city_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.city_slots
    ADD CONSTRAINT city_slots_pkey PRIMARY KEY (id);


--
-- Name: client_access_tokens client_access_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_access_tokens
    ADD CONSTRAINT client_access_tokens_pkey PRIMARY KEY (id);


--
-- Name: client_access_tokens client_access_tokens_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_access_tokens
    ADD CONSTRAINT client_access_tokens_token_hash_key UNIQUE (token_hash);


--
-- Name: lead_files lead_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lead_files
    ADD CONSTRAINT lead_files_pkey PRIMARY KEY (id);


--
-- Name: leads leads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_pkey PRIMARY KEY (id);


--
-- Name: legal_settings legal_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.legal_settings
    ADD CONSTRAINT legal_settings_pkey PRIMARY KEY (setting_key);


--
-- Name: media_files media_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.media_files
    ADD CONSTRAINT media_files_pkey PRIMARY KEY (id);


--
-- Name: project_categories project_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_categories
    ADD CONSTRAINT project_categories_pkey PRIMARY KEY (id);


--
-- Name: project_categories project_categories_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_categories
    ADD CONSTRAINT project_categories_slug_key UNIQUE (slug);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: projects projects_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_slug_key UNIQUE (slug);


--
-- Name: site_announcement site_announcement_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_announcement
    ADD CONSTRAINT site_announcement_pkey PRIMARY KEY (id);


--
-- Name: site_events site_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_events
    ADD CONSTRAINT site_events_pkey PRIMARY KEY (id);


--
-- Name: site_settings site_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_settings
    ADD CONSTRAINT site_settings_pkey PRIMARY KEY (setting_key);


--
-- Name: site_visits site_visits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site_visits
    ADD CONSTRAINT site_visits_pkey PRIMARY KEY (id);


--
-- Name: city_slots_city_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX city_slots_city_status_idx ON public.city_slots USING btree (city, status);


--
-- Name: idx_client_access_tokens_active_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_access_tokens_active_hash ON public.client_access_tokens USING btree (token_hash, is_active);


--
-- Name: idx_client_access_tokens_expires_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_access_tokens_expires_at ON public.client_access_tokens USING btree (expires_at);


--
-- Name: idx_client_access_tokens_lead_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_access_tokens_lead_id ON public.client_access_tokens USING btree (lead_id);


--
-- Name: idx_leads_archived_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leads_archived_at ON public.leads USING btree (archived_at);


--
-- Name: idx_leads_priority; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leads_priority ON public.leads USING btree (lead_priority);


--
-- Name: idx_leads_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leads_status ON public.leads USING btree (lead_status);


--
-- Name: idx_leads_trashed_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leads_trashed_at ON public.leads USING btree (trashed_at);


--
-- Name: idx_leads_updated_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leads_updated_at ON public.leads USING btree (updated_at DESC);


--
-- Name: idx_site_events_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_events_created_at ON public.site_events USING btree (created_at DESC);


--
-- Name: idx_site_events_event_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_events_event_type ON public.site_events USING btree (event_type);


--
-- Name: idx_site_events_path; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_events_path ON public.site_events USING btree (path);


--
-- Name: idx_site_events_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_events_session_id ON public.site_events USING btree (session_id);


--
-- Name: idx_site_events_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_events_source ON public.site_events USING btree (source);


--
-- Name: idx_site_visits_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_visits_created_at ON public.site_visits USING btree (created_at DESC);


--
-- Name: idx_site_visits_path; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_visits_path ON public.site_visits USING btree (path);


--
-- Name: idx_site_visits_referer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_visits_referer ON public.site_visits USING btree (referer);


--
-- Name: media_files_block_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX media_files_block_idx ON public.media_files USING btree (block_key);


--
-- Name: media_files_owner_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX media_files_owner_idx ON public.media_files USING btree (owner_type, owner_id);


--
-- Name: media_files_target_key_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX media_files_target_key_idx ON public.media_files USING btree (target_key);


--
-- Name: media_files_type_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX media_files_type_idx ON public.media_files USING btree (media_type);


--
-- Name: client_access_tokens client_access_tokens_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_access_tokens
    ADD CONSTRAINT client_access_tokens_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id) ON DELETE CASCADE;


--
-- Name: lead_files lead_files_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lead_files
    ADD CONSTRAINT lead_files_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 0wKG2ZeeIk9N1eouIXhuJkCaMWoBcmNjVEqIqjxMN53er0eJV2g3KMW6G5nWlB3
