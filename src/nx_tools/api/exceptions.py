class NXToolsError(Exception):
    pass


class InvalidConfig(NXToolsError):
    pass


class ConfigNotFound(NXToolsError):
    pass
