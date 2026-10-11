import json
import os
from openai import OpenAI

SYSTEM = """
You are an evidence-bounded research assistant.
Decide whether a specific fairness analysis is Supported, Conditionally Supported,
or Unsupported by the supplied VERIFIED RFAF audit records.

Do not infer missing demographics. Do not convert annotator-perceived labels into
self-reported identity. Do not declare a dataset fair or unfair.

Return JSON only with:
decision, rationale, required_caveat, missing_evidence.
"""


def assess_claim(dataset: str, fairness_question: str, verified_records: list[dict]) -> dict:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    client = OpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        base_url=f"{endpoint}/openai/v1/",
    )
    model = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    prompt = f"""
Dataset: {dataset}
Fairness question: {fairness_question}

VERIFIED RFAF RECORDS:
{json.dumps(verified_records, indent=2)}

Classify this proposed fairness analysis as one of:
Supported
Conditionally Supported
Unsupported
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
