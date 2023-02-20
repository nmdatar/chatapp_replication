import threading
from typing import Optional
import os

import grpc

from proto import chatapp_pb2 as chatapp
from proto import chatapp_pb2_grpc as rpc

address = 'localhost'
port = 11912


class Client:

    def __init__(self, username: Optional[str]):
        self.username = username
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServiceStub(channel)

        # create new thread for message streaming
        threading.Thread(target=self.__listen_for_messages,
                         daemon=True).start()

        # start main loop
        self.main_loop()

    def create_or_login_user(self):
        new_username = self.username

        if new_username is None:
            new_username = input("Please enter a username:\n")

        print(f'Logging in {new_username}')

        res1 = self.conn.LoginAccount(chatapp.Account(username=new_username))

        if res1.success:
            self.username = new_username
            return
        else:
            print(f'Account not exist. Creating one...')
            res2 = self.conn.CreateAccount(
                chatapp.Account(username=new_username))

            if res2.success:
                self.username = new_username
            else:
                print(f'Creating account failed...')
                new_username = None

    def delete_account(self):
        print(f'Deleting account: {self.username}')

        res = self.conn.DeleteAccount(chatapp.Account(username=self.username))

        if not res.success:
            print(f'Deleting account failed...')
        else:
            self.username = None

    def logout_account(self):
        print(f'Logging out account: {self.username}')

        res = self.conn.LogoutAccount(chatapp.Account(username=self.username))
        if not res.success:
            print(f'Logging out account failed...')
        else:
            self.username = None
            os._exit(0)

    def list_accounts(self):
        search_term = input("Please enter your search term:\n")

        print(f'Listing accounts that matches search term: {search_term}')

        for account in self.conn.ListAccounts(chatapp.ListAccountQuery(search_term=search_term)):
            print(account)

    def send_message(self):
        toUsername = input('To whom are you sending this message?\n')
        message = input("Write your message below:\n")

        res = self.conn.SendMessage(chatapp.Message(
            fromUsername=self.username, toUsername=toUsername, message=message))
        if not res:
            print(f'Message retry delivery failed...')

    def deliver_messages(self):
        toUsername = input(
            "Which username do you want to retry message delivery:\n")

        res = self.conn.DeliverMessages(chatapp.Account(username=toUsername))
        if not res.success:
            print(f'Message retry delivery failed...')

    def __listen_for_messages(self):
        print('Client is listening for new messages')
        responses = self.conn.ChatStream(chatapp.Empty())

        for msg in responses:
            print(chatapp.Message(msg))

    def main_loop(self):
        while True:
            command = input("Enter your command below:\n")

            if command == 'login':
                self.create_or_login_user()
            elif command == 'delete_account':
                self.delete_account()
            elif command == 'list_accounts':
                self.list_accounts()
            elif command == 'logout':
                self.logout_account()
            elif command == 'send':
                self.send_message()
            elif command == 'retry':
                self.deliver_messages()
            else:
                print("Invalid command. Please try again")


if __name__ == '__main__':
    c = Client(None)
