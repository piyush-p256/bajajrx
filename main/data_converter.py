import pandas as pd
from langchain_core.documents import Document

# This script converts the SHL assessment data into a format suitable for vector storage.

def dataconverter():
    assesment_data = pd.read_csv("../data/shl_assessments2.csv")
    data = assesment_data[["job_title", "test_type", "url", "adaptive_support", "duration", "remote_support", "description"]]

    assessment_list = []

    # Iterate over the rows of the DataFrame
    for index, row in data.iterrows():
        obj = {
            "assessment_title": row["job_title"],
            "review": f"Assessment Title: {row['job_title']}.\nURL: {row['url']}.\nThis assessment is designed to evaluate skills in {row['test_type']}.",
            "test_url": row["url"],
            "test_type": [row["test_type"]],
            "adaptive_support": str(row["adaptive_support"]),
            "duration": int(row["duration"]),
            "remote_support": str(row["remote_support"]),
            "description": str(row["description"]) if pd.notna(row["description"]) else ""
        }
        assessment_list.append(obj)

    docs = []

    for i, obj in enumerate(assessment_list):
        # Ensure test_type is always a list
        test_type = obj.get("test_type", [])
        if isinstance(test_type, str):
            test_type = [x.strip() for x in test_type.split(",") if x.strip()]

        # Make sure we're explicitly preserving the data types
        metadata = {
            "url": str(obj.get("test_url", "")),
            "adaptive_support_str": str(obj.get("adaptive_support", "")),
            "description": str(obj.get("description", "")),
            "duration_int": int(obj.get("duration", 0)),
            "remote_support_str": str(obj.get("remote_support", "")),
            "test_type": test_type
        }

        # Create document content with explicit formatting
        page_content = f"""
Assessment Title: {obj.get('assessment_title', '').strip()}
URL: {metadata['url']}
Description: {metadata['description']}
Duration: {metadata['duration_int']}
Adaptive Support: {metadata['adaptive_support_str']}
Remote Support: {metadata['remote_support_str']}
Test Type: {", ".join(test_type)}
""".strip()

        doc = Document(
            page_content=page_content,
            metadata=metadata
        )
        docs.append(doc)

    return docs
