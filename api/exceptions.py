from fastapi import HTTPException, status


class RepeatingIdentityPid(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are repeating identity pid, please make sur that there are different to each other"
        )


class RepeatingEmail(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are repeating email, please make sur that there are different to each other"
        )


class RepeatingPhoneNumber(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are repeating phone number, please make sur that there are different to each other"
        )


class PhoneNumberExist(HTTPException):

    def __init__(self, phone_number: str = ""):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The phone number " + phone_number + " is already used by another user, please provide an other"
        )


class EmailExist(HTTPException):
    def __init__(self, email: str = ""):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email " + email + " is already used by another user, please provide an other"
        )


class IdentityPidExist(HTTPException):
    def __init__(self, pid: str = ""):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The pid " + pid + " is already used by another user, please provide an other"
        )


class IdentityPidNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user you trying to update does not exist, the operation cannot be achieved"
        )


class ContactNotFound(HTTPException):
    def __init__(self, contact: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact does not found " + contact
        )


class ContactIsDisable(HTTPException):
    def __init__(self, contact: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This contact is disable " + contact
        )


class SearchParamError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of the search query should be provided"
        )


class RoleBasedAccessError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not access to this resource"
        )