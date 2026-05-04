#!/usr/bin/env python3
"""Test safe_float with NaN"""

import math

def safe_float(v):
    try:
        return float(v) if str(v).strip() not in ["nan","NaN","","None"] else None
    except:
        return None

# Test with NaN
nan_val = float('nan')
print(f'safe_float(nan): {safe_float(nan_val)}')
print(f'str(nan): {repr(str(nan_val))}')
print(f'str(nan).strip(): {repr(str(nan_val).strip())}')
print(f'Is nan in excluded list: {str(nan_val).strip() in ["nan","NaN","","None"]}')

# Test with "Nonemm"
print(f'\nsafe_float("Nonemm"): {safe_float("Nonemm")}')