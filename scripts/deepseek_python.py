# ============================================================================
# 5. POSTGRESQL SCHEMA (Based on Kimi's Architecture)
# ============================================================================

# Generate SQL schema as a string for the portfolio
sql_schema = """
-- ============================================================================
-- CLINICAL WORKFLOW SIGNAL AUDIT - PostgreSQL Schema
-- Based on Kimi's Architecture: Signal Fusion → Decision Support → Audit Loop
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "tablefunc";  -- For pivot tables

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- 1. Patients (from Kimi's actor framework)
CREATE TABLE dim_patients (
    patient_id VARCHAR(10) PRIMARY KEY,
    mrn_hash VARCHAR(64),  -- Hashed MRN for privacy
    age_group VARCHAR(10),  -- '18-30', '31-50', '51-70', '71+'
    admission_date TIMESTAMP,
    primary_diagnosis VARCHAR(100),
    comorbidities TEXT[],  -- Array of conditions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Signal Sources (Kimi's data source catalog)
CREATE TABLE dim_signal_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) UNIQUE NOT NULL,  -- 'Bedside Monitor', 'EMR Flowsheet', etc.
    source_category VARCHAR(30),  -- 'Continuous', 'Event-Driven', 'Documented'
    integration_protocol VARCHAR(20),  -- 'HL7', 'FHIR', 'Proprietary'
    typical_frequency VARCHAR(20),  -- 'Continuous', 'Q1H', 'Q4H', 'Event-Driven'
    false_positive_rate DECIMAL(4,3),  -- 0.850 = 85% false alarms
    data_quality_score DECIMAL(3,2) DEFAULT 1.00
);

-- 3. Clinical Actors (Kimi's actor list)
CREATE TABLE dim_clinical_actors (
    actor_id SERIAL PRIMARY KEY,
    actor_role VARCHAR(50) UNIQUE NOT NULL,  -- 'Bedside Nurse', 'ICU Resident', etc.
    role_category VARCHAR(30),  -- 'Nursing', 'Physician', 'Allied Health', 'Emergency'
    typical_cognitive_load INTEGER CHECK (typical_cognitive_load BETWEEN 1 AND 10),
    alerts_per_shift_typical INTEGER,
    primary_data_view TEXT[]  -- Array of dashboards they use
);

-- 4. Bottlenecks (Kimi's 8 bottleneck types)
CREATE TABLE dim_bottlenecks (
    bottleneck_id SERIAL PRIMARY KEY,
    bottleneck_name VARCHAR(50) UNIQUE NOT NULL,
    severity_score INTEGER CHECK (severity_score BETWEEN 1 AND 5),
    mechanism TEXT,  -- How the bottleneck occurs
    typical_impact_minutes INTEGER,  -- Average delay introduced
    mitigation_strategy TEXT
);

-- 5. Outcomes
CREATE TABLE dim_outcomes (
    outcome_id SERIAL PRIMARY KEY,
    outcome_name VARCHAR(50) UNIQUE NOT NULL,
    outcome_category VARCHAR(20),  -- 'Positive', 'Neutral', 'Negative', 'Sentinel'
    preventability_flag BOOLEAN DEFAULT FALSE,
    mortality_risk DECIMAL(3,2)
);

-- 6. Shifts
CREATE TABLE dim_shifts (
    shift_id SERIAL PRIMARY KEY,
    shift_name VARCHAR(20) UNIQUE NOT NULL,  -- 'Day', 'Night', 'Swing'
    start_time TIME,
    end_time TIME,
    typical_staffing_ratio DECIMAL(3,1),  -- Nurse:patient ratio
    handoff_complexity_score INTEGER CHECK (handoff_complexity_score BETWEEN 1 AND 5)
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 7. Main Signal Audit Events (Kimi's core data structure)
CREATE TABLE fact_signal_audit_events (
    -- Primary key
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign keys
    patient_id VARCHAR(10) REFERENCES dim_patients(patient_id),
    source_id INTEGER REFERENCES dim_signal_sources(source_id),
    detecting_actor_id INTEGER REFERENCES dim_clinical_actors(actor_id),
    primary_bottleneck_id INTEGER REFERENCES dim_bottlenecks(bottleneck_id),
    outcome_id INTEGER REFERENCES dim_outcomes(outcome_id),
    shift_id INTEGER REFERENCES dim_shifts(shift_id),
    
    -- Clinical presentation
    sepsis_stage INTEGER CHECK (sepsis_stage BETWEEN 0 AND 3),
    heart_rate DECIMAL(5,1),
    respiratory_rate DECIMAL(4,1),
    spo2 DECIMAL(4,1),
    systolic_bp INTEGER,
    temperature DECIMAL(3,1),
    lactate DECIMAL(3,1),
    gcs INTEGER CHECK (gcs BETWEEN 3 AND 15),
    urine_output_ml_hr DECIMAL(4,1),
    
    -- Kimi's Signal Audit Trail (THE CORE METRICS)
    signal_generated_time TIMESTAMP NOT NULL,
    signal_detected_time TIMESTAMP,
    signal_acknowledged_time TIMESTAMP,
    action_initiated_time TIMESTAMP,
    
    -- Derived latency metrics
    detection_latency_min DECIMAL(6,2),      -- Generation → Detection
    acknowledgment_latency_min DECIMAL(6,2),  -- Detection → Acknowledgment
    action_latency_min DECIMAL(6,2),          -- Acknowledgment → Action
    total_latency_min DECIMAL(6,2),           -- Generation → Action
    
    -- Data visibility metrics (Kimi's concept)
    data_sources_available INTEGER,
    data_sources_viewed INTEGER,
    visibility_gap INTEGER GENERATED ALWAYS AS 
        (data_sources_available - data_sources_viewed) STORED,
    
    -- Contextual factors
    cognitive_load_score INTEGER CHECK (cognitive_load_score BETWEEN 1 AND 10),
    false_alarms_preceding INTEGER DEFAULT 0,
    handoff_occurred BOOLEAN DEFAULT FALSE,
    handoff_quality VARCHAR(20) CHECK (handoff_quality IN ('Adequate', 'Partial', 'Inadequate', 'N/A')),
    lab_tat_minutes INTEGER,
    
    -- Risk scoring
    mews_physiological INTEGER,
    lactate_risk INTEGER,
    latency_risk INTEGER,
    visibility_risk INTEGER,
    bottleneck_risk INTEGER,
    cognitive_risk INTEGER,
    composite_risk_score DECIMAL(5,2),  -- 0-100 scale
    
    -- Risk classification
    risk_classification VARCHAR(20) CHECK (risk_classification IN ('Low', 'Medium', 'High', 'Critical')),
    recommended_action TEXT,
    
    -- AI/ML metadata
    ai_confidence DECIMAL(5,2),
    preventable_deterioration BOOLEAN DEFAULT FALSE,
    model_version VARCHAR(20),
    
    -- Audit metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_sepsis_stage CHECK (sepsis_stage >= 0 AND sepsis_stage <= 3),
    CONSTRAINT positive_latency CHECK (total_latency_min >= 0),
    CONSTRAINT valid_confidence CHECK (ai_confidence BETWEEN 0 AND 100)
);

-- ============================================================================
-- INDEXES (Performance for Kimi's real-time queries)
-- ============================================================================

-- Temporal queries (audit trail reconstruction)
CREATE INDEX idx_signal_generated ON fact_signal_audit_events(signal_generated_time);
CREATE INDEX idx_action_initiated ON fact_signal_audit_events(action_initiated_time);

-- Patient trajectory queries
CREATE INDEX idx_patient_trajectory ON fact_signal_audit_events(patient_id, signal_generated_time);

-- Risk stratification
CREATE INDEX idx_risk_class ON fact_signal_audit_events(risk_classification);
CREATE INDEX idx_composite_risk ON fact_signal_audit_events(composite_risk_score DESC);

-- Bottleneck analysis
CREATE INDEX idx_bottleneck ON fact_signal_audit_events(primary_bottleneck_id);

-- Preventable deterioration (Kimi's key metric)
CREATE INDEX idx_preventable ON fact_signal_audit_events(preventable_deterioration) 
    WHERE preventable_deterioration = TRUE;

-- ============================================================================
-- MATERIALIZED VIEWS (For dashboards)
-- ============================================================================

-- View 1: Shift Performance Dashboard (Kimi's success metrics)
CREATE MATERIALIZED VIEW mv_shift_performance AS
SELECT 
    ds.shift_name,
    COUNT(fae.event_id) AS total_signals,
    ROUND(AVG(fae.total_latency_min), 1) AS avg_signal_to_action_min,
    ROUND(AVG(fae.composite_risk_score), 1) AS avg_risk_score,
    COUNT(CASE WHEN fae.risk_classification IN ('High', 'Critical') THEN 1 END) AS high_risk_cases,
    COUNT(CASE WHEN fae.preventable_deterioration THEN 1 END) AS preventable_events,
    ROUND(AVG(fae.visibility_gap), 2) AS avg_data_gaps,
    ROUND(AVG(fae.cognitive_load_score), 1) AS avg_cognitive_load
FROM fact_signal_audit_events fae
JOIN dim_shifts ds ON fae.shift_id = ds.shift_id
GROUP BY ds.shift_name;

-- View 2: Bottleneck Impact Analysis
CREATE MATERIALIZED VIEW mv_bottleneck_impact AS
SELECT 
    db.bottleneck_name,
    db.severity_score,
    COUNT(fae.event_id) AS occurrence_count,
    ROUND(AVG(fae.total_latency_min), 1) AS avg_latency_caused,
    ROUND(AVG(fae.composite_risk_score), 1) AS avg_resulting_risk,
    COUNT(CASE WHEN fae.preventable_deterioration THEN 1 END) AS preventable_outcomes
FROM fact_signal_audit_events fae
JOIN dim_bottlenecks db ON fae.primary_bottleneck_id = db.bottleneck_id
GROUP BY db.bottleneck_name, db.severity_score
ORDER BY avg_latency_caused DESC;

-- View 3: Patient Risk Trajectory (Kimi's 4-hour trend)
CREATE MATERIALIZED VIEW mv_patient_risk_trajectory AS
SELECT 
    patient_id,
    signal_generated_time,
    composite_risk_score,
    risk_classification,
    total_latency_min,
    LAG(composite_risk_score) OVER (PARTITION BY patient_id ORDER BY signal_generated_time) AS prev_risk_score,
    composite_risk_score - LAG(composite_risk_score) OVER (PARTITION BY patient_id ORDER BY signal_generated_time) AS risk_trend
FROM fact_signal_audit_events
ORDER BY patient_id, signal_generated_time;

-- ============================================================================
-- AUDIT LOG TABLE (For continuous learning)
-- ============================================================================

CREATE TABLE audit_clinician_overrides (
    override_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES fact_signal_audit_events(event_id),
    clinician_id VARCHAR(20),
    override_reason TEXT,  -- 'Disagree - patient has AFib, not sepsis'
    original_recommendation TEXT,
    clinician_action TEXT,
    outcome_correct BOOLEAN,  -- Was the AI right?
    override_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ANALYTICAL QUERIES (Portfolio-Ready Examples)
-- ============================================================================

-- Query 1: Kimi's Core Metric - Signal-to-Action Latency by Risk Level
SELECT 
    risk_classification,
    COUNT(*) AS cases,
    ROUND(AVG(total_latency_min), 1) AS avg_latency,
    ROUND(AVG(detection_latency_min), 1) AS avg_detection_gap,
    ROUND(AVG(acknowledgment_latency_min), 1) AS avg_ack_gap,
    ROUND(AVG(action_latency_min), 1) AS avg_action_gap
FROM fact_signal_audit_events
GROUP BY risk_classification
ORDER BY avg_latency DESC;

-- Query 2: Preventable Deteriorations by Bottleneck
SELECT 
    db.bottleneck_name,
    COUNT(*) AS preventable_count
FROM fact_signal_audit_events fae
JOIN dim_bottlenecks db ON fae.primary_bottleneck_id = db.bottleneck_id
WHERE fae.preventable_deterioration = TRUE
GROUP BY db.bottleneck_name
ORDER BY preventable_count DESC;

-- Query 3: Data Visibility Gap Impact
SELECT 
    CASE 
        WHEN visibility_gap = 0 THEN 'Full Visibility'
        WHEN visibility_gap <= 2 THEN 'Partial Visibility'
        ELSE 'Severe Gap'
    END AS visibility_category,
    COUNT(*) AS cases,
    ROUND(AVG(total_latency_min), 1) AS avg_latency,
    ROUND(AVG(composite_risk_score), 1) AS avg_risk,
    COUNT(CASE WHEN preventable_deterioration THEN 1 END) AS preventable_events
FROM fact_signal_audit_events
GROUP BY visibility_category
ORDER BY avg_latency DESC;

-- Query 4: Cognitive Load vs. Latency Correlation
SELECT 
    cognitive_load_score,
    COUNT(*) AS cases,
    ROUND(AVG(total_latency_min), 1) AS avg_latency,
    ROUND(AVG(ai_confidence), 1) AS avg_ai_confidence
FROM fact_signal_audit_events
GROUP BY cognitive_load_score
ORDER BY cognitive_load_score;

-- Query 5: Shift Handoff Impact
SELECT 
    handoff_occurred,
    handoff_quality,
    COUNT(*) AS cases,
    ROUND(AVG(total_latency_min), 1) AS avg_latency,
    ROUND(AVG(composite_risk_score), 1) AS avg_risk
FROM fact_signal_audit_events
WHERE handoff_occurred = TRUE
GROUP BY handoff_occurred, handoff_quality;

-- ============================================================================
-- TRIGGER FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_fact_signal_audit_updated_at 
    BEFORE UPDATE ON fact_signal_audit_events
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
"""

print("\n" + "="*70)
print("POSTGRESQL SCHEMA GENERATED")
print("="*70)
print("Tables created:")
print("  • dim_patients")
print("  • dim_signal_sources (Kimi's 6 data sources)")
print("  • dim_clinical_actors (Kimi's 7 actors)")
print("  • dim_bottlenecks (Kimi's 8 bottlenecks)")
print("  • dim_outcomes")
print("  • dim_shifts")
print("  • fact_signal_audit_events (Core signal audit trail)")
print("  • audit_clinician_overrides (Human-in-the-loop)")
print("\nMaterialized views:")
print("  • mv_shift_performance")
print("  • mv_bottleneck_impact")
print("  • mv_patient_risk_trajectory")
print("\n5 analytical queries ready for dashboard integration")

# ============================================================================
# FINAL SUMMARY FOR PORTFOLIO
# ============================================================================

print("\n" + "="*70)
print("PORTFOLIO SUMMARY: Clinical Workflow Signal Audit")
print("="*70)
print(f"Dataset: {len(df_scored)} cleaned records")
print(f"Risk Distribution: {df_scored['risk_classification'].value_counts().to_dict()}")
print(f"Preventable Events Identified: {df_scored['preventable_deterioration'].sum()}")
print(f"Mean Signal-to-Action Latency: {df_scored['total_latency_minutes'].mean():.1f} min")
print(f"Mean AI Confidence: {df_scored['ai_confidence'].mean():.1f}%")
print("\nKey Features Implemented:")
print("  ✓ Multi-source signal fusion")
print("  ✓ Signal audit trail (generation → detection → action)")
print("  ✓ 6-component composite risk scoring")
print("  ✓ Bottleneck identification & impact analysis")
print("  ✓ Preventable deterioration flagging")
print("  ✓ AI confidence scoring")
print("  ✓ Human-in-the-loop override tracking")
print("  ✓ 10 data quality issues detected and resolved")