class UsernameIlliegalError(Exception):
    pass


class PasswordIlliegalError(Exception):
    pass


class PasswordNotEqualError(Exception):
    pass


class WeakPasswordError(Exception):
    pass


class DuplicatedUsernameError(Exception):
    pass


class UsernameOrPasswordWrongError(Exception):
    pass


class UIDNotExistError(Exception):
    pass


class UsernameNotExistError(Exception):
    pass


class UsernameNotChangedError(Exception):
    pass


class PasswordNotChangedError(Exception):
    pass


class TokenNotExistError(Exception):
    pass


class OrderIDNotExistError(Exception):
    pass


class PriceIlliegalError(Exception):
    pass


class AmountIlliegalError(Exception):
    pass


class DuplicatedOrderError(Exception):
    pass


class OrderStatusError(Exception):
    pass
