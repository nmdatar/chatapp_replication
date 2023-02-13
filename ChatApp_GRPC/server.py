from concurrent import futures
import time

import grpc

import chatApp_pb2
import chatApp_pb2_grpc


class ChatAppServicer(chatApp_pb2_grpc.ChatAppServicer):
    def __init__(self):
        self.accounts = {}
        self.name_connected = {}
        self.message_queue = {}

    def createAccount(self, request, context):
        username = request.username
        if username in self.accounts:
            return chatApp_pb2.CreateAccountResponse(success=False, message="Account Already Exists")
        self.accounts[username] = []
        self.name_connected[username] = 1
        return chatApp_pb2.CreateAccountResponse(success=True, message="Account Created Successfully")

    # check syntax for returning a list
    def ListAccounts(self, request, context):
        usernames = []
        for username in self.usernames:
            usernames.append(username)
        chatApp_pb2_grpc.ListAccountsResponse().usernames.extend(usernames)
        return chatApp_pb2_grpc.ListAccountsResponse()

    def SendMessage(self, request, context):
        message = request.message
        sender = request.froUser
        recipient = request.toUser

        if recipient not in self.accounts:
            return chatApp_pb2.SendMessageResponse(
                success=False,
                message='invalid user'
            )
        if recipient in self.name_connected:
            # TODO: actually send the message
            return chatApp_pb2.SendMessageResponse(
                success=False, message='Message sent successfully')
        else:
            if len(self.message_queue[recipient]) < 1:
                self.message_queue[recipient] = [message]
            else:
                self.message_queue[recipient].append(message)
            return chatApp_pb2.SendMessageResponse(
                success=False, message='User is not logged in, will sed message later')

    def DeliverMessages(self, request, context):
        recipient = request.recipient
        if recipient in self.message_queue:
            return chatApp_pb2.DeliveryMessageResponse(success=True, message=self.message_queue[recipient])
        else:
            return chatApp_pb2.DeliveryMessageResponse(success=False)

    def DeleteAccount(self, request, context):
        deleteAccount = chatApp_pb2.DeleteAccountRequest()
        if deleteAccount in self.accounts:
            self.accounts.clear(deleteAccount)
            return chatApp_pb2.DeleteAccountResponse(sucess=True, message="Account Deleted Successfully")
        else:
            return chatApp_pb2.DeleteAccountResponse(sucess=False, message="Account Doesn't Exist")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chatApp_pb2_grpc.add_ChatAppServicer_to_server(ChatAppServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()


if __name__ == '__main__':
    serve()
