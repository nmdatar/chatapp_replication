from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAccountRequest(_message.Message):
    __slots__ = ["password", "username"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    password: str
    username: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class CreateAccountResponse(_message.Message):
    __slots__ = ["status", "success"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    status: str
    success: bool
    def __init__(self, success: bool = ..., status: _Optional[str] = ...) -> None: ...

class DeleteAccountRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class DeleteAccountResponse(_message.Message):
    __slots__ = ["error", "success"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: str
    success: bool
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class DeliverMessageRequest(_message.Message):
    __slots__ = ["recipient"]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    recipient: str
    def __init__(self, recipient: _Optional[str] = ...) -> None: ...

class DeliveryMessageResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ListAccountsRequest(_message.Message):
    __slots__ = ["wildcard"]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    wildcard: str
    def __init__(self, wildcard: _Optional[str] = ...) -> None: ...

class ListAccountsResponse(_message.Message):
    __slots__ = ["status", "usernames"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    USERNAMES_FIELD_NUMBER: _ClassVar[int]
    status: str
    usernames: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, usernames: _Optional[_Iterable[str]] = ..., status: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ["password", "username"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    password: str
    username: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ["status", "success"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    status: str
    success: bool
    def __init__(self, success: bool = ..., status: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ["status", "success"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    status: str
    success: bool
    def __init__(self, success: bool = ..., status: _Optional[str] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ["message", "recipient", "sender"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    message: str
    recipient: str
    sender: str
    def __init__(self, message: _Optional[str] = ..., recipient: _Optional[str] = ..., sender: _Optional[str] = ...) -> None: ...

class SendMessageResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...
