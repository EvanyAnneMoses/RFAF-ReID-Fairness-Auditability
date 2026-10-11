import json
import os
import tempfile
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.azure_audit import audit_documents
from src.compare_audits import compare
from src.document_loader import load_path
from src.claim_boundary import assess_claim

load_dotenv()

st.set_page_config(page_title="RFAF Prototype", layout="wide")
st.title("RFAF — Re-ID Fairness Auditability Framework")
st.caption("Evidence-bounded audit prototype. The system does not infer demographics from images.")

with st.expander("RFAF coding rules", expanded=False):
    st.markdown(
        """
- **D** — Documented
- **P** — Partially documented
- **ND** — Not documented in reviewed evidence
- **NA** — Not applicable

`ND` is not evidence that something never happened.
        """
    )

dataset = st.text_input("Dataset name", value="Market-1501")
question = st.text_input(
    "Optional fairness question",
    placeholder="Example: Can I evaluate age representation in this dataset?",
)

uploads = st.file_uploader(
    "Upload dataset documentation",
    type=["txt", "md", "pdf"],
    accept_multiple_files=True,
)

documents = []
if uploads:
    for upload in uploads:
        suffix = "." + upload.name.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.getvalue())
            tmp_path = tmp.name
        doc = load_path(tmp_path)
        doc["name"] = upload.name
        documents.append(doc)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

if st.button("Run RFAF audit with Azure", type="primary", disabled=not documents):
    try:
        result = audit_documents(dataset, documents)
        st.session_state["rfaf_result"] = result
    except Exception as exc:
        st.error(f"Audit failed: {exc}")

result = st.session_state.get("rfaf_result")
if result:
    st.subheader("Azure-assisted RFAF audit")
    df = pd.DataFrame(result["records"])
    df.insert(0, "dataset", result.get("dataset", dataset))
    st.dataframe(
        df[[
            "dimension", "status", "evidence", "source",
            "rationale", "supported_analysis", "unsupported_analysis"
        ]],
        use_container_width=True,
    )

    st.download_button(
        "Download audit JSON",
        data=json.dumps(result, indent=2),
        file_name=f"{dataset.replace(' ', '_')}_rfaf_audit.json",
        mime="application/json",
    )
    st.download_button(
        "Download audit CSV",
        data=df.to_csv(index=False),
        file_name=f"{dataset.replace(' ', '_')}_rfaf_audit.csv",
        mime="text/csv",
    )

    if question and st.button("Assess fairness question"):
        try:
            decision = assess_claim(dataset, question, result["records"])
            st.subheader("Fairness-question boundary")
            st.json(decision)
        except Exception as exc:
            st.error(f"Claim assessment failed: {exc}")

st.divider()
st.subheader("Human vs Azure comparison")
st.caption("Upload CSV files with dataset, dimension, and status columns.")

human_file = st.file_uploader("Human reference CSV", type=["csv"], key="human")
llm_file = st.file_uploader("Azure audit CSV", type=["csv"], key="llm")

if human_file and llm_file:
    try:
        comparison = compare(pd.read_csv(human_file), pd.read_csv(llm_file))
        c1, c2, c3 = st.columns(3)
        c1.metric("Exact agreement", f"{comparison['exact_agreement']:.1%}")
        c2.metric("Cohen's kappa", f"{comparison['cohen_kappa']:.3f}")
        c3.metric("Potential overclaim rate", f"{comparison['potential_overclaim_rate']:.1%}")
        if comparison["disagreements"]:
            st.dataframe(pd.DataFrame(comparison["disagreements"]), use_container_width=True)
    except Exception as exc:
        st.error(f"Comparison failed: {exc}")
