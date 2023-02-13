from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAccountRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class CreateAccountResponse(_message.Message):
    __slots__ = ["created", "errorMessage"]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    created: bool
    errorMessage: str
    def __init__(self, created: bool = ..., errorMessage: _Optional[str] = ...) -> None: ...

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
    __slots__ = ["listAccount"]
    LISTACCOUNT_FIELD_NUMBER: _ClassVar[int]
    listAccount: str
    def __init__(self, listAccount: _Optional[str] = ...) -> None: ...

class ListAccountsResponse(_message.Message):
    __slots__ = ["usernames"]
    USERNAMES_FIELD_NUMBER: _ClassVar[int]
    usernames: _containers.RepeatedCompositeFieldContainer[CreateAccountRequest]
    def __init__(self, usernames: _Optional[_Iterable[_Union[CreateAccountRequest, _Mapping]]] = ...) -> None: ...

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
