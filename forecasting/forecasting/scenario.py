def apply_overrides(params: dict, overrides: dict) -> dict:    
    p = params.copy()
    p.update(overrides)    
    return p