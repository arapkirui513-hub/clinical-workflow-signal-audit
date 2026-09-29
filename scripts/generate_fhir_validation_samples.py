import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.fhir.observation import build_observation_from_event
from app.fhir.patient import FHIRPatient
from app.fhir.task import build_task_from_event
from app.fhir.workflow_bundle import (
    build_fhir_bundle_from_event,
)


OUTPUT_DIR = Path("validation")


EVENT = {
    "event_id": "validation-event-001",
    "patient_id": "synthetic-patient-001",
    "hospital_unit": "ICU",
    "signal_type": "Heart Rate",
    "signal_generated_time": "2026-09-28 20:00:00",
    "signal_detected_time": "2026-09-28 20:02:00",
    "signal_acknowledged_time": "2026-09-28 20:04:00",
    "action_initiated_time": "2026-09-28 20:05:00",
    "action_completed_time": "2026-09-28 20:20:00",
    "detection_latency_min": 2,
    "acknowledgement_latency_min": 2,
    "action_latency_min": 1,
    "total_latency_min": 20,
    "workflow_tier": "Review",
    "escalation_state": "Completed",
    "sla_target_min": 30,
    "sla_breached": False,
    "routing_attempts": 1,
    "data_quality_issue": "No Issue",
}


def write_resource(filename: str, resource: object) -> None:
    path = OUTPUT_DIR / filename
    path.write_text(
        json.dumps(
            resource.model_dump(
                by_alias=True,
                exclude_none=True,
            ),
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    patient = FHIRPatient(
        id=EVENT["patient_id"],
        active=True,
        gender="unknown",
    )

    observation = build_observation_from_event(EVENT)
    task = build_task_from_event(EVENT)
    bundle = build_fhir_bundle_from_event(EVENT)

    write_resource("Patient-validation.json", patient)
    write_resource("Observation-validation.json", observation)
    write_resource("Task-validation.json", task)
    write_resource("Bundle-validation.json", bundle)

    print("FHIR validation samples generated:")

    for path in sorted(OUTPUT_DIR.glob("*-validation.json")):
        print(f"  {path}")


if __name__ == "__main__":
    main()
