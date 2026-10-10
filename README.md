# RFAF: Re-ID Fairness Auditability Framework

This repository contains the implementation and research artifacts for:

**Beyond Benchmark Performance: Fairness and Governance in Person Re-Identification Datasets**

The Re-ID Fairness Auditability Framework (RFAF) is a source-grounded framework for assessing whether the available evidence associated with a person re-identification dataset is sufficient to support a specified fairness analysis.

RFAF does not assign an overall "fair" or "unfair" score to a dataset. Instead, it asks what fairness questions can be responsibly answered from the available evidence.

## RFAF Dimensions

RFAF evaluates seven dimensions:

1. Collection and Purpose
2. Consent and Autonomy
3. Privacy and Identifiability
4. Representation and Label Provenance
5. Fairness Auditability
6. Access and Use Governance
7. Withdrawal and Lifecycle Management

Documentation is coded as:

- **D** — Documented
- **P** — Partially documented
- **ND** — Not documented in the reviewed sources
- **NA** — Not applicable

RFAF then maps available evidence to a question-specific claim boundary:

- **Supported**
- **Conditionally Supported**
- **Unsupported**

Missing information is treated as an evidence limitation rather than inferred from images or assumed to exist.

## Dataset Cases

The study examines four person Re-ID dataset cases:

- DukeMTMC / DukeMTMC-reID
- Market-1501
- CUHK03
- MSMT17

Sony FHIBE is included as a fairness-oriented human-centric comparison case and is not treated as an equivalent Re-ID benchmark.

## Quantitative Analysis

Quantitative demographic analysis is performed only when the relevant annotations and their provenance are documented.

For Market-1501, published age and gender annotation distributions are analyzed. Sensitive demographic attributes are not inferred from images.

## Azure-Assisted Prototype

The repository includes a prototype using `gpt-5-mini` through Microsoft Foundry to assist with source-grounded evidence extraction and preliminary RFAF documentation coding.

The language model is used as a decision-support tool rather than as an autonomous ethics evaluator. All evidence and coding decisions remain subject to human verification.

In one saved Market-1501 pilot run, the prototype matched the human reference judgment on 6 of 7 RFAF dimensions.

## Responsible Use

This repository does not redistribute restricted dataset imagery, credentials, or other materials whose redistribution is prohibited.

Researchers should obtain datasets through their authorized sources and comply with applicable licenses, access agreements, withdrawal notices, and use restrictions.

## Author

Evany Anne Moses  
University of North Carolina at Chapel Hill
