from concurrent import futures
import time

import grpc

import chatApp_pb2
import chatApp_pb2_grpc


class ChatAppServicer(chatApp_pb2_grpc.ChatAppServicer):
    def __init__(self):
        self.accounts = {}
        self.user_connected = {}
        self.message_queue = {}
        self.message_sent = {}

    def Login(self, request, context):

        user = request.username
        if user in self.accounts:
            self.user_connected[user] = grpc.insecure_channel(
                'localhost:50051')
            return chatApp_pb2.LoginResponse(success=True, errorMessage="You are logged in")
        else:
            return chatApp_pb2.CreateAccountResponse(success=False,
                                                     errorMessage="Invalid User")

    def Logout(self, request, context):
        user = request.username
        if user in self.user_connected:
            connection = self.user_connected[user]
            connection.close()
            del self.user_connected[user]
            return chatApp_pb2.LogoutResponse(success=True, errorMessage="Successfully logged out")
        else:
            return chatApp_pb2.LogoutResponse(success=False, errorMessage="Invalid user")

    def CreateAccount(self, request, context):
        newUser = request.username
        if newUser in self.accounts:
            return chatApp_pb2.CreateAccountResponse(success=False, errorMessage="Account Already Exists")

        return chatApp_pb2.CreateAccountResponse(success=True,
                                                 errorMessage="Account Created Successfully")

    # the wildcard logic may requires more work
    def ListAccounts(self, request, context):
        print(self.accounts, "all accounts")
        search_term = request.wildcard
        if search_term:
            matching_accounts = [
                username for username in self.accounts if search_term in username]
        else:
            matching_accounts = list(self.accounts.keys())
        if matching_accounts:
            response = "\n".join(matching_accounts)
            return chatApp_pb2.ListAccountsResponse(usernames=response, errorMessage="These are matching accounts")
        else:
            return chatApp_pb2.ListAccountsResponse(usernames="None", errorMessage="No matching accounts")

    # DeliverMessage

    def DeliverMessages(self, request, context):
        recipient = request.recipient
        if recipient in self.message_queue and recipient in self.user_connected:
            for sender, message in self.message_queue[recipient]:
                self.user_connected[recipient].send(
                    sender.encode(), message.encode())
            return chatApp_pb2.DeliveryMessageResponse(success=True, message=self.message_queue[recipient])
        else:
            return chatApp_pb2.DeliveryMessageResponse(success=False, message="No messages for this user")

    def SendMessage(self, request, context):
        message = request.message
        sender = request.froUser
        recipient = request.toUser
        if recipient in self.accounts:
            if recipient in self.user_connected:
                stub = chatApp_pb2_grpc.ChatAppStub(
                    self.user_connected[recipient])
                stub.send(message.encode())
                return chatApp_pb2.SendMessageResponse(success=True, errorMessage='Message successfully sent')
            else:
                if recipient not in self.message_queue:
                    self.message_queue[recipient] = []
                else:
                    self.message_queue[recipient].append((sender, message))
                    return chatApp_pb2.SendMessageResponse(
                        success=True,
                        message='User is not currently log in. Message will send when recipient is connected.'
                    )
        else:
            return chatApp_pb2.SendMessageResponse(
                success=True,
                message='Invalid User'
            )

    # Delete Account - COMPLETE
    def DeleteAccount(self, request, context):
        user = request.username
        if user in self.accounts and user in self.user_connected:
            connection = self.user_connected[user]
            connection.close()
            del self.user_connected[user]
            return chatApp_pb2.DeleteAccountResponse(success=True, error="Account Deleted Successfully")
        else:
            return chatApp_pb2.DeleteAccountResponse(success=False, error="Account Doesn't Exist")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chatApp_pb2_grpc.add_ChatAppServicer_to_server(ChatAppServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("server started on port [::]:50051")
    try:
        while True:
            time.sleep(60 * 60 * 24)  # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
