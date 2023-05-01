from fastapi import HTTPException, status


class RepeatingIdentityPid(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are repeating identity pid, please make sur that there are different to each other"
        )


class PhoneNumberExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This phone number is already used by another user, please provide an other"
        )


class EmailExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already used by another user, please provide an other"
        )


class IdentityPidExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This pid is already used by another user, please provide an other"
        )


class IdentityPidNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user you trying to update does not exist, the operation cannot be achieved"
        )