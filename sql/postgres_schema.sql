-- Clinical Workflow Signal Audit - PostgreSQL Schema
-- Synthetic portfolio demo only.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE dim_patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    mrn_hash VARCHAR(64),
    age_group VARCHAR(20),
    admission_date TIMESTAMP,
    primary_diagnosis VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_signal_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) UNIQUE NOT NULL,
    source_category VARCHAR(30),
    integration_protocol VARCHAR(20),
    typical_frequency VARCHAR(30),
    data_quality_score DECIMAL(3,2) DEFAULT 1.00
);

CREATE TABLE dim_clinical_actors (
    actor_id SERIAL PRIMARY KEY,
    actor_role VARCHAR(50) UNIQUE NOT NULL,
    role_category VARCHAR(30),
    alerts_per_shift_typical INTEGER
);

CREATE TABLE dim_bottlenecks (
    bottleneck_id SERIAL PRIMARY KEY,
    bottleneck_name VARCHAR(50) UNIQUE NOT NULL,
    severity_score INTEGER CHECK (severity_score BETWEEN 1 AND 5),
    mechanism TEXT,
    typical_impact_minutes INTEGER,
    mitigation_strategy TEXT
);

CREATE TABLE fact_signal_audit_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20) REFERENCES dim_patients(patient_id),
    source_id INTEGER REFERENCES dim_signal_sources(source_id),
    detecting_actor_id INTEGER REFERENCES dim_clinical_actors(actor_id),
    primary_bottleneck_id INTEGER REFERENCES dim_bottlenecks(bottleneck_id),

    heart_rate DECIMAL(5,1),
    respiratory_rate DECIMAL(4,1),
    spo2 DECIMAL(4,1),
    systolic_bp INTEGER,
    lactate DECIMAL(3,1),
    sofa_score INTEGER,
    sepsis_flag BOOLEAN,
    ews_version VARCHAR(20) DEFAULT 'NEWS2_v1',

    signal_generated_time TIMESTAMP NOT NULL,
    signal_detected_time TIMESTAMP,
    signal_acknowledged_time TIMESTAMP,
    action_initiated_time TIMESTAMP,
    action_completed_time TIMESTAMP,

    detection_latency_min DECIMAL(6,2),
    acknowledgment_latency_min DECIMAL(6,2),
    action_latency_min DECIMAL(6,2),
    total_latency_min DECIMAL(6,2),

    data_quality_flags TEXT[],
    is_backdated BOOLEAN DEFAULT FALSE,
    clock_sync_status VARCHAR(30) DEFAULT 'synced',

    score_tier VARCHAR(20) CHECK (score_tier IN ('Monitor','Review','Escalate','Activate')),
    escalation_state VARCHAR(30) DEFAULT 'pending',
    sla_target_min INTEGER,
    sla_breached BOOLEAN DEFAULT FALSE,
    routing_attempts INTEGER DEFAULT 1,

    notification_channel VARCHAR(30),
    intervention_type VARCHAR(50),

    model_output JSONB,
    input_snapshot_hash VARCHAR(64),
    ai_confidence DECIMAL(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_clinician_overrides (
    override_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES fact_signal_audit_events(event_id),
    clinician_id VARCHAR(50),
    override_reason TEXT,
    original_recommendation TEXT,
    clinician_action TEXT,
    outcome_correct BOOLEAN,
    override_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signal_generated ON fact_signal_audit_events(signal_generated_time);
CREATE INDEX idx_patient_trajectory ON fact_signal_audit_events(patient_id, signal_generated_time);
CREATE INDEX idx_score_tier ON fact_signal_audit_events(score_tier);
CREATE INDEX idx_sla_breached ON fact_signal_audit_events(sla_breached);
