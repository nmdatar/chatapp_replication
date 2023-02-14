from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAccountRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class CreateAccountResponse(_message.Message):
    __slots__ = ["errorMessage", "success"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    errorMessage: str
    success: bool
    def __init__(self, success: bool = ..., errorMessage: _Optional[str] = ...) -> None: ...

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

class DeliverRequest(_message.Message):
    __slots__ = ["recipient"]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    recipient: str
    def __init__(self, recipient: _Optional[str] = ...) -> None: ...

class DeliverResponse(_message.Message):
    __slots__ = ["messages"]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, messages: _Optional[_Iterable[str]] = ...) -> None: ...

class ListAccountsRequest(_message.Message):
    __slots__ = ["wildcard"]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    wildcard: str
    def __init__(self, wildcard: _Optional[str] = ...) -> None: ...

class ListAccountsResponse(_message.Message):
    __slots__ = ["errorMessage", "usernames"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    USERNAMES_FIELD_NUMBER: _ClassVar[int]
    errorMessage: str
    usernames: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, usernames: _Optional[_Iterable[str]] = ..., errorMessage: _Optional[str] = ...) -> None: ...

class SendMessageRequest(_message.Message):
    __slots__ = ["froUser", "message", "toUser"]
    FROUSER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOUSER_FIELD_NUMBER: _ClassVar[int]
    froUser: str
    message: str
    toUser: str
    def __init__(self, message: _Optional[str] = ..., froUser: _Optional[str] = ..., toUser: _Optional[str] = ...) -> None: ...

class SendMessageResponse(_message.Message):
    __slots__ = ["errorMessage", "success"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    errorMessage: str
    success: bool
    def __init__(self, success: bool = ..., errorMessage: _Optional[str] = ...) -> None: ...
