# post_processing.py
import re

def clean_tenant_name(answer, confidence, min_confidence=0.5):
    """
    Clean and validate tenant name.
    - Reject names containing 'landlord' or similar.
    - Ensure the answer is a plausible name.
    """
    answer = answer.strip()
    if confidence < min_confidence:
        return f"{answer} (Low confidence: {confidence:.2f})"
    landlord_terms = ["landlord", "owner", "lessor", "property management"]
    if any(term in answer.lower() for term in landlord_terms):
        return "Invalid tenant name (contains landlord-related term)"
    if not re.search(r"[a-zA-Z]", answer) or answer.isdigit():
        return "Invalid tenant name (not a name)"
    return answer

def clean_lease_duration(answer, confidence, min_confidence=0.5):
    """
    Clean and validate lease duration.
    - Convert to standardized format (e.g., '7 days', '12 months').
    - Flag unusual durations (e.g., <30 days).
    """
    answer = answer.strip().lower()
    if confidence < min_confidence:
        return f"{answer} (Low confidence: {confidence:.2f})"
    match = re.match(r"(?:[a-zA-Z]+\s*\(\s*(\d+)\s*\)\s*|\b(\d+)\s*)(day|week|month|year)s?", answer)
    if match:
        num = match.group(1) or match.group(2)
        unit = match.group(3) + ("s" if int(num) != 1 else "")
        duration = f"{num} {unit}"
        if unit in ["day", "days"] and int(num) < 30:
            return f"{duration} (Unusually short duration)"
        return duration
    duration_map = {"one": "1", "two": "2", "three": "3", "seven": "7", "twelve": "12"}
    for word, num in duration_map.items():
        if word in answer:
            unit = "year" if "year" in answer else "month" if "month" in answer else "day" if "day" in answer else "week"
            return f"{num} {unit}s"
    return f"{answer} (Unrecognized duration format)"

def clean_rent_amount(answer, confidence, min_confidence=0.5):
    """
    Clean and validate rent amount.
    - Ensure valid currency format (e.g., '$1,200.00').
    """
    answer = answer.strip()
    if confidence < min_confidence:
        return f"{answer} (Low confidence: {confidence:.2f})"
    match = re.search(r"[\$]?([\d,]+\.?\d*)", answer)
    if match:
        amount = float(match.group(1).replace(",", ""))
        return f"${amount:,.2f}"
    return f"{answer} (Invalid rent amount format)"

def clean_property_address(answer, confidence, min_confidence=0.5):
    """
    Clean and validate property address.
    - Ensure the address is complete (e.g., includes street, city, state, or ZIP).
    """
    answer = answer.strip()
    if confidence < min_confidence:
        return f"{answer} (Low confidence: {confidence:.2f})"
    components = answer.split()
    if len(components) < 3 or answer.isdigit():
        return f"{answer} (Incomplete address)"
    if not re.search(r"(street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|\d{5})", answer.lower()):
        return f"{answer} (Possibly incomplete address)"
    return answer