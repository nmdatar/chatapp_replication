from concurrent import futures
from typing import List

import grpc
import time

from proto import chatapp_pb2 as chatapp
from proto import chatapp_pb2_grpc as rpc


class ChatServer(rpc.ChatServiceServicer):

    def __init__(self):
        # username: list of dict
        # dict: { username: str, online: true}
        self.usernames: dict[str, bool] = {}

        # messages: list of objects
        # dict: { from: str, to: str, message: str }
        self.messages: List = []

        # messages: list of objects
        # dict: { from: str, to: str, message: str }
        self.queued_messages: List = []

        # retry message flag
        # str | None
        self.retry_flag = None

    def CreateAccount(self, request: chatapp.Account, context):
        username = request.username
        print(f'creating account for username: {username}')

        if username in self.usernames:
            return chatapp.CommonResponse(success=False, message="Account Exists Already")

        self.usernames[username] = True
        return chatapp.CommonResponse(success=True, message="Account Created Succesfully")

    def DeleteAccount(self, request: chatapp.Account, context):
        username = request.username
        print(f'deleting username: {username}')

        if username not in self.usernames:
            return chatapp.CommonResponse(success=False, message="Username doesn't exist")

        # deleting username
        del self.usernames[username]

        # delete messages
        for message_obj in self.messages:
            if message_obj['fromUserame'] == username:
                self.messages.remove(message_obj)

        for message_obj in self.queued_messages:
            if message_obj['fromUserame'] == username:
                self.queued_messages.remove(message_obj)

        return chatapp.CommonResponse(success=True, message="Username deleted Succesfully")

    def LoginAccount(self, request: chatapp.Account, context):
        username = request.username
        print(f'login username: {username}')

        if username not in self.usernames:
            return chatapp.CommonResponse(success=False, message="Username doesn't exist")

        self.usernames[username] = True
        return chatapp.CommonResponse(success=True, message='Username logged in Succesfully')

    def LogoutAccount(self, request: chatapp.Account, context):
        username = request.username
        print(f'logout username: {username}')

        if username not in self.usernames:
            return chatapp.CommonResponse(success=False, message="Username doesn't exist")

        self.usernames[username] = False
        return chatapp.CommonResponse(success=True, message="Username logged in Succesfully")

    def ListAccounts(self, request: chatapp.ListAccountQuery, context):
        search_term = request.search_term
        print(f'listing accounts with search term: {search_term}')

        if search_term is not None:
            search_term = request.search_term
            matching_accounts = [
                username for username in self.usernames if search_term in username]

            for account in matching_accounts:
                yield chatapp.Account(username=account)
        else:
            for account in self.usernames:
                yield chatapp.Account(username=account)

    def SendMessage(self, request: chatapp.Message, context):
        fromUsername = request.fromUsername
        toUsername = request.toUsername
        message = request.message

        print(f'{fromUsername} send the following message to {toUsername}: {message}')

        if fromUsername not in self.usernames:
            return chatapp.CommonResponse(success=False, message="From username doesn't exist")

        if toUsername not in self.usernames:
            return chatapp.CommonResponse(success=False, message="To username doesn't exist")

        message_obj = {
            'fromUsername': fromUsername,
            'toUsername': toUsername,
            'message': message
        }

        if (self.usernames[toUsername]):
            self.messages.append(message_obj)
            return chatapp.CommonResponse(success=False, message="Message Queued")
        else:
            self.queued_messages.append(message_obj)
        return chatapp.CommonResponse(success=True, message="Message sent Succesfully")

    def ChatStream(self, request_iterator, context):
        last_index = 0

        while True:
            # retry undelivered message flag is on
            if self.retry_flag is not None:
                for message_obj in self.queued_messages[:]:

                    # send only to online
                    if (message_obj["toUsername"] == self.retry_flag
                            and self.usernames[message_obj["toUsername"]]):
                        # delete queued message in original queue
                        self.queued_messages.remove(message_obj)
                        yield chatapp.Message(fromUsername=message_obj['fromUsername'], toUsername=message_obj['toUsername'], message=message_obj['message'])

                # reset retry flag
                self.retry_flag = None

            # stream messages to online users
            while len(self.messages) > last_index:
                message_obj = self.messages[last_index]
                last_index += 1
                print(message_obj)
                yield chatapp.Message(fromUsername=message_obj['fromUsername'], toUsername=message_obj['toUsername'], message=message_obj['message'])

    def DeliverMessages(self, request: chatapp.Account, context):
        username = request.username
        print(f'retry message(s) to {username}')

        if username not in self.usernames:
            return chatapp.CommonResponse(success=False, message="Username doesn't exist")

        self.retry_flag = username
        return chatapp.CommonResponse(success=True, message="Retrying messages now")


if __name__ == "__main__":
    port = 11912
    # creating a server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServiceServicer_to_server(ChatServer(), server)

    print(f'✅ Starting server. Listening on port {port}')
    server.add_insecure_port('[::]:' + str(port))
    server.start()

    while True:
        time.sleep(64 * 64 * 100)
