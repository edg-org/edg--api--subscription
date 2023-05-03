from fastapi import HTTPException, status


class ContractNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="We can't found contract according to the providing data"
        )


class ContractStatusError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The status shouldn't be the same with the previous status"
        )


class ContractOrContactNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The contact or contract does not exist or contact isn't the owner of the contract"
        )


class ContractLevelError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The level shouldn't be the same as the previous level"
        )


class ContractExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The contract already exist at the providing delivery point"
        )


class DeleteContractException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This contract is not exist, the delete operation cannot be achieved"
        )


class ContactNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="We can't found the contact, with the providing data"
        )


class RepeatingDeliveryPoint(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are repeating delivery point, please make sur that there are different to each other"
        )


class EditContactWhileNotOwner(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot edit this contract, due you're not the owner"
        )


class ContractDisabled(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to apply any modification, because the contract is disabled"
        )


class BillingRequestException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while getting billing's information, please try later"
        )


class StatusErrorWhenCurrentStatusIsEqualInitial(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current status is Initial, allowed value is Avenant, Suspendu, Clôturé"
        )


class StatusErrorWhenCurrentStatusIsEqualEdited(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current status is Edited, allowed value is Suspendu, Clôturé, Initial, Incomplet"
        )


class ContractIsAlreadyActivated(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The contract is already activated"
        )