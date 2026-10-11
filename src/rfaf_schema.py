from dataclasses import dataclass, asdict
from typing import Literal

EvidenceCode = Literal["D", "P", "ND", "NA"]
ClaimDecision = Literal["Supported", "Conditionally Supported", "Unsupported"]

RFAF_DIMENSIONS = [
    "Collection & Purpose",
    "Consent & Autonomy",
    "Privacy & Identifiability",
    "Representation & Label Provenance",
    "Fairness Auditability",
    "Access & Use Governance",
    "Withdrawal & Lifecycle Management",
]

DIMENSION_QUESTIONS = {
    "Collection & Purpose": [
        "Where, when, how, and why was the dataset collected?",
        "What population and setting does the collection represent?",
        "What was the stated intended use?",
    ],
    "Consent & Autonomy": [
        "Is participant notice or informed consent documented?",
        "Is opt-out, correction, or participant withdrawal documented?",
        "Is ethics or IRB review documented where applicable?",
    ],
    "Privacy & Identifiability": [
        "What identity-persistent or identifying information is present?",
        "Are privacy safeguards, redaction, anonymization, or restrictions documented?",
    ],
    "Representation & Label Provenance": [
        "What demographic or group attributes are documented?",
        "How were labels produced: self-reported, annotator-assigned, inferred, external, or unknown?",
        "Are missingness and category definitions documented?",
    ],
    "Fairness Auditability": [
        "Can a specified fairness question be evaluated from the documented evidence?",
        "Can it be evaluated without inferring sensitive attributes from images?",
    ],
    "Access & Use Governance": [
        "Who can access the dataset?",
        "What uses, redistribution, commercial use, or derivatives are permitted or prohibited?",
    ],
    "Withdrawal & Lifecycle Management": [
        "Can participant records be corrected or removed?",
        "Are withdrawal, versioning, downstream copies, or derivative obligations documented?",
    ],
}

@dataclass
class AuditRecord:
    dataset: str
    dimension: str
    status: EvidenceCode
    evidence: str
    source: str
    rationale: str
    supported_analysis: str
    unsupported_analysis: str
    confidence: float = 0.0

    def to_dict(self):
        return asdict(self)
