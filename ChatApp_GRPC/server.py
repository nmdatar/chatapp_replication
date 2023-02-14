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

    def CreateAccount(self, request, context):
        newUser = request.username
        if newUser in self.accounts:
            return chatApp_pb2.CreateAccountResponse(success=False, errorMessage="Account Already Exists")
        self.accounts[newUser] = []
        self.name_connected[newUser] = 1
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
        deleteAccount = request.username
        if deleteAccount in self.accounts:
            self.accounts.pop(deleteAccount)
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
