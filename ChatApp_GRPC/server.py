from concurrent import futures
import time

import grpc

import chat_app_pb2
import chat_app_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_UNDELIVERED_MESSAGES = {}


class ChatAppServicer(chat_app_pb2_grpc.ChatAppServicer):
    def __init__(self):
        self.accounts = {}

    def createAccount(self, request, context):
        username = request.username
        if username in self.accounts:
            return chat_app_pb2.CreateAccountResponse(success=False, message="Username Already Exists")
        self.accounts[username] = []
        return chat_app_pb2.CreateAccountResponse(success=True, message="Account Created Successfully")

    # check syntax for returning a list
    def ListAccounts(self, request, context):
        usernames = []
        for username in self.usernames:
            usernames.append(username)
        chat_app_pb2_grpc.ListAccountsResponse().usernames.extend(usernames)
        return chat_app_pb2_grpc.ListAccountsResponse()

    def SendMessage(self, request, context):
        message = request.message
        recipient = request.froUser
        sender = request.toUser

        if recipient not in self.accounts:
            return chat_app_pb2.SendMessageResponse(
                success=False,
                message='invalid user'
            )
        # BASIC LOGIC
        # recipient_account = self.accounts[recipient]
        # if recipient_account.logged_in:
        #     recipient_account.received_messages.append(message)
        # else:
        #     recipient_account.queued_messages.append(message)

        # return chat_app_pb2.SendMessageResponse(
        #     success=True
        # )

    # BASIC LOGIC
    # def DeliverMessages(self, request, context):
    #     recipient = request.recipient
    #     message = request.message
    #     if recipient in _UNDELIVERED_MESSAGES:
    #         _UNDELIVERED_MESSAGES[recipient].append(message)
    #     else:
    #         _UNDELIVERED_MESSAGES[recipient] = [message]
    #     return chat_app_pb2.DeliveryMessageResponse(success=True)

    def DeleteAccount(self, request, context):
        deleteAccount = chat_app_pb2.DeleteAccountRequest()
        if deleteAccount in self.accounts:
            self.accounts.clear(deleteAccount)
            return chat_app_pb2.DeleteAccountResponse(sucess=True, message="Account Deleted Successfully")
        else:
            return chat_app_pb2.DeleteAccountResponse(sucess=False, message="Account Doesn't Exist")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_app_pb2_grpc.add_ChatAppServicer_to_server(ChatAppServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)  # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
