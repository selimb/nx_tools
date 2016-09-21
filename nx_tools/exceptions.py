class NXToolsError(Exception):
    pass


class ConfigError(NXToolsError):
    pass


class UserConfigNotFound(NXToolsError):
    pass
