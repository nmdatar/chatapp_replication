import grpc
import chatApp_pb2
import chatApp_pb2_grpc


def run():

    # create a channel to the server
    with grpc.insecure_channel('localhost:50051') as channel:
        # create a stub (client)
        stub = chatApp_pb2_grpc.ChatAppStub(channel)
        request = input(
            "Enter request (createAccount, listAccounts, sendMessage, deliverMessage, or deleteAccount): ")

        # Create account function - COMPLETE
        if request == "createAccount":
            username = input("Enter a username: ")
            password = input("Password: ")
            # create a request message
            response = stub.CreateAccount(
                chatApp_pb2.CreateAccountRequest(username=username, password=password))
            # call the create account function
            if response.success:
                print(response)
            else:
                print(response)

        elif request == "login":
            username = input("Enter your username:")
            password = input("Password:")
            response = stub.Login(chatApp_pb2.LoginRequest(
                username=username, password=password))
            if response.success:
                print("Account logged in")
            else:
                print("Invalid account")

        elif request == "logout":
            username = input("Enter your username:")
            response = stub.Logout(
                chatApp_pb2.LogoutRequest(username=username))
            if response.success:
                print("Account logged out")
            else:
                print("Invalid account or not currently logged in")

        # List accounts function - COMPLETE (check wildcard logic)
        elif request == "listAccounts":
            wildcard = input("Enter any text: ")
            response = stub.ListAccounts(
                chatApp_pb2.ListAccountsRequest(wildcard=wildcard))
            print("Response: ", response)

        # Send message function - INCOMPLETE
        elif request == "sendMessage":
            recipient = input("Recipient:")
            message = input("Message:")
            sender = input("Your name:")

            response = stub.SendMessage(chatApp_pb2.Message(
                message=message, recipient=recipient, sender=sender))
            print("Response:", response)

        # Deliver undelivered message - INCOMPLETE
        elif request == "deliverMessage":
            recipient = input("Recipient:")
            response = stub.SendMessage(chatApp_pb2.Message(
                recipient=recipient))
            print("Response Send Message:", response)

        # Delete account - COMPLETE
        elif request == "deleteAccount":
            deleteAccount = input("Enter account: ")
            response = stub.DeleteAccount(
                chatApp_pb2.DeleteAccountRequest(username=deleteAccount))
            # delete the account
            if response.success:
                print("Account deleted successfully")

            else:
                print("Non-existent account")
        else:
            print("Request unaccepted")


run()
# # create a request message for send message
# send_request = chatApp_pb2.SendMessageRequest(
#     sender='user1', recipient='user2', message='hello user2')

# # call the send message function
# send_response = stub.SendMessage(send_request)
# print("Send message response: ", send_response.response)

# # create a request message for retrieve message
# retrieve_request = chatApp_pb2.RetrieveMessagesRequest(username='user2')

# # call the retrieve message function
# retrieve_response = stub.RetrieveMessages(retrieve_request)
# print("Retrieve message response: ", retrieve_response.messages)
