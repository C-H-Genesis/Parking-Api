import re
from fast_alpr import ALPR

# Load once when server starts
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="global-plates-mobile-vit-v2-model",
)


def extract_plate(image_path: str):
    """Use fast-alpr to detect and read license plate."""
    debug_info = []

    results = alpr.predict(image_path)

    best = None
    best_conf = 0

    for plate in results:
        if plate.ocr and plate.ocr.text:
            text = plate.ocr.text.upper()
            clean = re.sub(r'[^A-Z0-9]', '', text)

            confidence = plate.ocr.confidence
            if isinstance(confidence, list):
                confidence = float(confidence[0]) if confidence else 0.0
            else:
                confidence = float(confidence)

            debug_info.append(
                {"text": clean, "confidence": round(confidence, 2)})

            # fast-alpr already confirmed a plate region exists
            # so accept any length — even 1-3 chars for personalized plates
            # but require at least 60% confidence to avoid garbage
            if len(clean) >= 1 and confidence >= 0.6 and confidence > best_conf:
                best = correct_plate(clean)
                best_conf = confidence

    print(f"ALPR result: {best} | All: {debug_info}")
    return best, debug_info


def correct_plate(plate: str) -> str:
    """Fix common OCR confusions using plate pattern analysis."""

    LETTER_FIXES = {'0': 'O', '1': 'I', '4': 'A',
                    '8': 'B', '6': 'G', '5': 'S', '2': 'Z'}
    NUMBER_FIXES = {'O': '0', 'I': '1', 'A': '4', 'I': 'T',
                    'B': '8', 'G': '6', 'X': 'K', 'Z': '2', 'S': '5'}

    plate = plate.upper().strip()
    corrected = list(plate)

    # Rwandan standard plate: LLL NNN L (7 chars)
    # e.g. RAG779I, RDF896K, RAB666P
    if len(plate) == 7:
        PATTERN = ['L', 'L', 'L', 'N', 'N', 'N', 'L']
        for i, (char, ptype) in enumerate(zip(corrected, PATTERN)):
            if ptype == 'L' and char in LETTER_FIXES:
                corrected[i] = LETTER_FIXES[char]
            elif ptype == 'N' and char in NUMBER_FIXES:
                corrected[i] = NUMBER_FIXES[char]

    # Rwandan old plate: LL NNN L (6 chars)
    # e.g. GP981A
    elif len(plate) == 6:
        PATTERN = ['L', 'L', 'N', 'N', 'N', 'L']
        for i, (char, ptype) in enumerate(zip(corrected, PATTERN)):
            if ptype == 'L' and char in LETTER_FIXES:
                corrected[i] = LETTER_FIXES[char]
            elif ptype == 'N' and char in NUMBER_FIXES:
                corrected[i] = NUMBER_FIXES[char]

    # RDF style: LLL NNN (6 chars no suffix)
    elif len(plate) == 5:
        PATTERN = ['L', 'L', 'N', 'N', 'N']
        for i, (char, ptype) in enumerate(zip(corrected, PATTERN)):
            if ptype == 'L' and char in LETTER_FIXES:
                corrected[i] = LETTER_FIXES[char]
            elif ptype == 'N' and char in NUMBER_FIXES:
                corrected[i] = NUMBER_FIXES[char]

    else:
        # Unknown pattern — use position-based detection
        char_types = ['L' if c.isalpha() else 'N' for c in plate]
        for i, (char, ptype) in enumerate(zip(corrected, char_types)):
            if ptype == 'L' and char in LETTER_FIXES:
                corrected[i] = LETTER_FIXES[char]
            elif ptype == 'N' and char in NUMBER_FIXES:
                corrected[i] = NUMBER_FIXES[char]

    result = ''.join(corrected)
    if result != plate:
        print(f"Plate corrected: {plate} → {result}")
    return result
