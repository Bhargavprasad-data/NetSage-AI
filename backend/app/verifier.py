from typing import Any, Dict, List, Union

def verify_evidence(diagnosis_evidence: Union[List[str], Dict[str, Any], None], show_outputs: dict) -> dict:
    """
    Verifies that the evidence claims made by the AI actually exist
    verbatim in the original show_outputs.
    Never modifies the original evidence, just returns a verification mapping.
    Handles evidence as either a list of strings or a dictionary.
    """
    if not diagnosis_evidence or not show_outputs:
        return {}

    verification_results = {}
    
    # Flatten all show_outputs values to a single string for easier substring matching
    all_output = " ".join([str(v) for v in show_outputs.values()])

    if isinstance(diagnosis_evidence, list):
        for idx, claim in enumerate(diagnosis_evidence):
            claim_str = str(claim)
            if claim_str and claim_str in all_output:
                verification_results[str(idx)] = "VERIFIED"
            else:
                verification_results[str(idx)] = "UNVERIFIED"
    elif isinstance(diagnosis_evidence, dict):
        for key, claim in diagnosis_evidence.items():
            if isinstance(claim, str) and claim in all_output:
                verification_results[key] = "VERIFIED"
            else:
                verification_results[key] = "UNVERIFIED"

    return verification_results
