import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Calibrated coordinates for 713x418 image resolution
COL_XS = [
    [46, 64, 82, 100, 118],    # Grup 1 (Q1-20)
    [189, 208, 226, 243, 261], # Grup 2 (Q21-40)
    [330, 348, 365, 383, 400], # Grup 3 (Q41-60)
    [469, 486, 504, 521, 539], # Grup 4 (Q61-80)
    [609, 626, 645, 662, 680], # Grup 5 (Q81-100)
]

ROW_YS = [
    36, 53, 70, 87, 104,       # Sub-blok 1
    135, 152, 169, 187, 204,   # Sub-blok 2
    234, 251, 268, 286, 303,   # Sub-blok 3
    334, 351, 368, 385, 403,   # Sub-blok 4
]

LABELS = ["A", "B", "C", "D", "E"]

# Detection parameters (v5 strategy)
GAP_THRESHOLD = 0.15         # Min gap between max and 2nd
MIN_THRESHOLD = 0.35         # Min ratio for FILLED
INVALID_ABS_THRESHOLD = 0.50 # Both must exceed this for INVALID
BUBBLE_RADIUS = 7
SEARCH_RADIUS = 8
TARGET_WIDTH = 713
TARGET_HEIGHT = 418

def get_bubble_center(thresh_img, approx_x, approx_y, search_radius=8):
    """Snap ke pusat bulatan terdekat via center-of-mass."""
    h, w = thresh_img.shape[:2]
    x1 = max(0, approx_x - search_radius)
    y1 = max(0, approx_y - search_radius)
    x2 = min(w, approx_x + search_radius)
    y2 = min(h, approx_y + search_radius)
    roi = thresh_img[y1:y2, x1:x2]
    coords = cv2.findNonZero(roi)
    if coords is not None and len(coords) > 5:
        M = cv2.moments(roi)
        if M["m00"] > 0:
            return int(M["m10"]/M["m00"]) + x1, int(M["m01"]/M["m00"]) + y1
    return approx_x, approx_y

def evaluate_bubble(thresh_img, cx, cy, radius=7):
    """Return rasio piksel non-zero (0.0 - 1.0) dalam circular mask."""
    h, w = thresh_img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, -1)
    masked = cv2.bitwise_and(thresh_img, mask)
    total = cv2.countNonZero(mask)
    filled = cv2.countNonZero(masked)
    return filled / total if total > 0 else 0.0

def process_omr_answers(image: np.ndarray) -> dict:
    """
    Process cropped image of the answers block.
    Expected image should be the block containing Q1-100 bubbles.
    """
    # 1. Resize to target dimension so the hardcoded grid works perfectly
    resized_img = cv2.resize(image, (TARGET_WIDTH, TARGET_HEIGHT))
    
    # 2. Preprocessing
    gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    paper_gray = np.median(gray)
    
    THRESH_SCALE = 0.62
    thresh_val = int(paper_gray * THRESH_SCALE)
    _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    
    # 3. Detection using Ratio-Gap v5
    detected_answers = {}
    
    for q in range(1, 101):
        grp_idx = (q - 1) // 20
        row_idx = (q - 1) % 20
        cy = ROW_YS[row_idx]
        xs = COL_XS[grp_idx]
        
        row_ratios = []
        
        for opt_idx, cx in enumerate(xs):
            # Snap to actual center slightly
            bx, by = get_bubble_center(thresh, cx, cy, search_radius=SEARCH_RADIUS)
            ratio = evaluate_bubble(thresh, bx, by, radius=BUBBLE_RADIUS)
            row_ratios.append((ratio, LABELS[opt_idx]))
            
        sorted_ratios = sorted(row_ratios, key=lambda x: x[0], reverse=True)
        max_ratio, selected = sorted_ratios[0]
        second_ratio, _ = sorted_ratios[1]
        gap = max_ratio - second_ratio
        
        # v5 DECISION LOGIC
        if gap >= GAP_THRESHOLD and max_ratio >= MIN_THRESHOLD:
            detected_answers[str(q)] = selected
        elif max_ratio >= INVALID_ABS_THRESHOLD and second_ratio >= INVALID_ABS_THRESHOLD:
            detected_answers[str(q)] = "INVALID"
        else:
            detected_answers[str(q)] = ""
            
    return detected_answers
