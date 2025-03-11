"""
Version comparison utilities for CreepyAI
"""
import re
from typing import Tuple, Optional, Union


def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Parse a version string into a tuple of integers
    
    Args:
        version_str: Version string in format X.Y.Z
        
    Returns:
        Tuple of (major, minor, patch) version numbers
    """
    # Extract version components using regex
    match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    
    # Convert matched groups to integers, treating None as 0
    components = [int(x) if x else 0 for x in match.groups()]
    
    # Ensure at least 3 components (major, minor, patch)
    while len(components) < 3:
        components.append(0)
    
    return tuple(components)


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings
    
    Args:
        version1: First version string
        version2: Second version string
        
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1_components = parse_version(version1)
    v2_components = parse_version(version2)
    
    if v1_components < v2_components:
        return -1
    elif v1_components > v2_components:
        return 1
    else:
        return 0


def version_meets_requirement(version: str, requirement: str) -> bool:
    """
    Check if a version meets a requirement
    
    Args:
        version: Version string
        requirement: Requirement string (e.g. ">=1.0.0", "==2.1.0", "<3.0.0")
        
    Returns:
        True if the version meets the requirement, False otherwise
    """
    # Parse requirement
    match = re.match(r'^([<>=!]{1,2})(.+)$', requirement)
    if not match:
        # Exact version match if no operator
        return compare_versions(version, requirement) == 0
    
    operator, req_version = match.groups()
    comp_result = compare_versions(version, req_version)
    
    if operator == '==':
        return comp_result == 0
    elif operator == '!=':
        return comp_result != 0
    elif operator == '>':
        return comp_result > 0
    elif operator == '>=':
        return comp_result >= 0
    elif operator == '<':
        return comp_result < 0
    elif operator == '<=':
        return comp_result <= 0
    else:
        raise ValueError(f"Invalid version requirement operator: {operator}")
