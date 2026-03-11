import re

def extract_property_address(text: str) -> str | None:
    """
    Extract property address from the LLM output.
    Looks for "Property: " at the start of the text.
    """
    if not text:
        print("⚠️ No text provided to extract_property_address")
        return None
    
    print(f"🔍 Searching for address in text (length: {len(text)} chars)")
    print(f"📄 First 300 chars: {text[:300]}")
    
    # Primary pattern: Look for "Property: " followed by address on the first few lines
    # This matches the format we explicitly asked for in the prompt
    lines = text.split('\n')
    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        if 'property:' in line.lower():
            # Extract everything after "Property:"
            match = re.search(r'property:\s*(.+)', line, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # Clean up
                address = re.sub(r'\s+', ' ', address)
                address = address.rstrip('.,;:')
                print(f"✅ Found address on line {i+1}: {address}")
                if len(address) > 5:
                    return address[:500]
    
    # Fallback patterns for other formats
    patterns = [
        r'(?:Subject Property|Property Address):\s*([^\n]+)',
        r'([0-9]+\s+[A-Za-z][^\n,]*,\s*[A-Za-z\s]+[A-Z]{2}[0-9]\s*[0-9][A-Z]{2})',  # UK postcode
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            address = match.group(1).strip()
            address = re.sub(r'\s+', ' ', address)
            address = address.rstrip('.,;:')
            print(f"✅ Fallback pattern {i+1} matched: {address}")
            if len(address) > 5:
                return address[:500]
    
    print("❌ No address pattern matched")
    return None
