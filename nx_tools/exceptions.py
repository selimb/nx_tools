class NXToolsError(Exception):
    """Base exception for nx_tools errors"""
    pass


class UserConfigNotFound(NXToolsError):
    """User Configuration file not found"""
    pass
