from concurrent import futures
import time

import grpc

import chatApp_pb2
import chatApp_pb2_grpc


class ChatAppServicer(chatApp_pb2_grpc.ChatAppServicer):
    def __init__(self):
        self.accounts = {}
        self.socket_to_user = {}

    def CreateAccount(self, request, context):
        username = request.username
        password = request.password
        if username in self.accounts:
            return chatApp_pb2.CreateAccountResponse(success=False, status="Account Already Exists")
        else:
            self.accounts[username] = {
                "password": password, "active": False, "received_messages": [], "context": None}
            return chatApp_pb2.CreateAccountResponse(success=True, status="Account successfully created")

    def ListAccounts(self, request, context):
        search_term = request.wildcard
        if search_term:
            matching_accounts = [
                username for username in self.accounts if search_term in username]
        else:
            matching_accounts = list(self.accounts.keys())
        if matching_accounts:
            response = "\n".join(matching_accounts)
            return chatApp_pb2.ListAccountsResponse(usernames=response, status="These are matching accounts")
        else:
            return chatApp_pb2.ListAccountsResponse(usernames="None", status="No matching accounts")

    def Login(self, request, context):
        username = request.username
        password = request.password
        self.socket_to_user[context.peer()] = username
        if username in self.accounts and self.accounts[username]["password"] == password:
            self.accounts[username]["context"] = context
            self.accounts[username]["active"] = True
            return chatApp_pb2.LoginResponse(success=True, status="You are logged in")
        else:
            return chatApp_pb2.LoginResponse(success=False,
                                             status="Invalid User")

    def SendMessage(self, request, context):
        message = request.message
        recipient = request.recipient
        sender = request.sender
        print("context", context)
        print("longer thing", self.accounts[recipient]["context"])

        # if valid username
        if recipient in self.accounts:
            if self.accounts[recipient]["active"]:
                message_send = f"\nFrom {sender}: Message: {message}"
                context.send_initial_metadata([])
                return chatApp_pb2.SendMessageResponse(status=message_send)
            else:
                # recipient is not online, save message for later delivery
                self.accounts[recipient]["received_messages"].append(
                    [sender, message])
                return chatApp_pb2.SendMessageResponse(status="Recipient not online. Will deliver on demand.")
        else:
            return chatApp_pb2.SendMessageResponse(
                status='Invalid User'
            )

    # DeliverMessagesd
    def DeliverMessages(self, request, context):
        username = request.username
        password = request.password
        if username in self.accounts and self.accounts[username]["password"] == password:
            for item in self.accounts[username]["received_messages"]:
                message_send = f"From {item[0]}: Message: {item[1]}\n"
                response = chatApp_pb2.DeliverMessageRequest(
                    status=message_send)
                self.accounts[username]["context"].Send(response)
            self.accounts[username]["received_messages"] = []
            response = chatApp_pb2.DeliverMessageRequest(status="")
            self.accounts[username]["context"].Send(response)
        else:
            response = chatApp_pb2.DeliverMessageRequest(
                status="Nonexistent account or wrong password")
            self.accounts[username]["context"].Send(response)

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
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
