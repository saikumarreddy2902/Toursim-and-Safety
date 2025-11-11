# Type annotations and fixes for Tourist Safety System
from typing import Any, Dict, List, Optional  # type: ignore

# Fix session get method type annotations
def fix_session_get(session_obj: Any, key: str, default: Any = None) -> Any:
    """Type-safe wrapper for session.get()"""
    return session_obj.get(key, default)

# Fix auto_sos_detector and incident_packager None checks
def safe_auto_sos_evaluate(detector: Optional[Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Safe wrapper for auto_sos_detector.evaluate_auto_sos_trigger"""
    if detector and hasattr(detector, 'evaluate_auto_sos_trigger'):
        return detector.evaluate_auto_sos_trigger(data)
    return {'triggered': False, 'confidence': 0.0, 'reason': 'detector_unavailable'}

def safe_incident_package(packager: Optional[Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Safe wrapper for incident_packager.create_incident_package"""
    if packager and hasattr(packager, 'create_incident_package'):
        return packager.create_incident_package(*args, **kwargs)
    return {'package_id': 'unavailable', 'status': 'error', 'message': 'packager_unavailable'}

# Helper functions for type safety
def safe_dict_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Type-safe dictionary get"""
    return d.get(key, default)

def safe_list_append(lst: List[Any], item: Any) -> None:
    """Type-safe list append"""
    lst.append(item)

def safe_len(obj: Any) -> int:
    """Type-safe length calculation"""
    try:
        return len(obj)
    except TypeError:
        return 0