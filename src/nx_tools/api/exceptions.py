class NXToolsError(Exception):
    pass


class UserConfigInvalid(NXToolsError):
    pass


class UserConfigNotFound(NXToolsError):
    pass
