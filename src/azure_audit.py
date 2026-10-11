import json
import os
from typing import List, Dict
from openai import OpenAI

from .rfaf_schema import RFAF_DIMENSIONS, DIMENSION_QUESTIONS

SYSTEM_PROMPT = """
You are an evidence-extraction assistant for the Re-ID Fairness Auditability Framework (RFAF).

You are NOT an ethics judge and you must not fill documentation gaps by assumption.

Rules:
1. Use only the supplied source text.
2. Never infer demographic attributes from images or descriptions of appearance.
3. If the supplied evidence does not explicitly establish a fact, use status "ND".
4. "ND" means "not documented in the supplied evidence", not "did not happen".
5. Use "P" only when relevant evidence exists but is incomplete, ambiguous, or insufficient.
6. Use "D" when the evidence is explicit and sufficient to characterize the dimension. A documented adverse fact can still be D.
7. Use "NA" only when a criterion genuinely does not apply.
8. Distinguish self-reported, annotator-assigned, algorithmically inferred, externally sourced, and undocumented label provenance.
9. Do not claim that a dataset is fair or unfair.
10. Return valid JSON only.
"""


def _schema() -> dict:
    return {
        "name": "rfaf_audit",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "dataset": {"type": "string"},
                "records": {
                    "type": "array",
                    "minItems": 7,
                    "maxItems": 7,
                    "items": {
                        "type": "object",
                        "properties": {
                            "dimension": {"type": "string", "enum": RFAF_DIMENSIONS},
                            "status": {"type": "string", "enum": ["D", "P", "ND", "NA"]},
                            "evidence": {"type": "string"},
                            "source": {"type": "string"},
                            "rationale": {"type": "string"},
                            "supported_analysis": {"type": "string"},
                            "unsupported_analysis": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": [
                            "dimension", "status", "evidence", "source", "rationale",
                            "supported_analysis", "unsupported_analysis", "confidence",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["dataset", "records"],
            "additionalProperties": False,
        },
    }


def _client() -> OpenAI:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    return OpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        base_url=f"{endpoint}/openai/v1/",
    )


def build_user_prompt(dataset: str, documents: List[Dict[str, str]]) -> str:
    source_blob = "\n\n".join(
        f"--- SOURCE: {d['name']} ---\n{d['text']}" for d in documents
    )
    questions = "\n".join(
        f"{i+1}. {dim}: " + " ".join(DIMENSION_QUESTIONS[dim])
        for i, dim in enumerate(RFAF_DIMENSIONS)
    )
    return f"""
DATASET: {dataset}

Audit the supplied documentation using all seven RFAF dimensions.

RFAF questions:
{questions}

For each dimension:
- choose D, P, ND, or NA;
- quote or closely paraphrase the strongest relevant evidence;
- identify the source file by name;
- explain the coding briefly;
- state what analysis the evidence supports;
- state what analysis the evidence does not support.

If there is no explicit evidence, return ND rather than guessing.

DOCUMENTS:
{source_blob}
"""


def validate_result(result: dict, expected_dataset: str | None = None) -> None:
    if "records" not in result or not isinstance(result["records"], list):
        raise ValueError("Audit output must contain a records list.")
    if len(result["records"]) != 7:
        raise ValueError(f"Expected 7 RFAF records, got {len(result['records'])}.")
    seen = set()
    for rec in result["records"]:
        dim = rec.get("dimension")
        if dim not in RFAF_DIMENSIONS:
            raise ValueError(f"Unexpected dimension: {dim}")
        if dim in seen:
            raise ValueError(f"Duplicate dimension: {dim}")
        seen.add(dim)
        if rec.get("status") not in {"D", "P", "ND", "NA"}:
            raise ValueError(f"Invalid status for {dim}: {rec.get('status')}")
    if expected_dataset and not result.get("dataset"):
        result["dataset"] = expected_dataset


def audit_documents(dataset: str, documents: List[Dict[str, str]]) -> dict:
    """Run a seven-dimension RFAF audit with an Azure OpenAI deployment."""
    if not documents:
        raise ValueError("At least one document is required.")

    client = _client()
    model = os.environ["AZURE_OPENAI_DEPLOYMENT"]
    prompt = build_user_prompt(dataset, documents)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": _schema(),
            },
        )
    except Exception:
        # Compatibility fallback for deployments that support JSON mode but not
        # strict structured outputs.
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + "\nReturn one JSON object exactly matching the requested fields.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

    raw = response.choices[0].message.content
    if not raw:
        raise RuntimeError("Azure returned an empty response.")
    result = json.loads(raw)
    validate_result(result, dataset)
    return result
