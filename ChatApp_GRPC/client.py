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
            userAccount = input("Enter a username: ")
            # create a request message
            response = stub.CreateAccount(
                chatApp_pb2.CreateAccountRequest(username=userAccount))
            # call the create account function
            print(response, "response")
            if response.success:
                print("Account created successfully")
            else:
                print("Account failed to create")

        elif request == "login":
            username = input("Enter your username:")
            response = stub.Login(chatApp_pb2.LoginRequest(username=username))
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
            if len(request) > 1:
                wildcard = input("Enter any text: ")
            response = stub.ListAccounts(
                chatApp_pb2.ListAccountsRequest(wildcard=wildcard))
            print("List accounts response: ", response)

        # Send message function - INCOMPLETE
        elif request == "sendMessage":
            recipient = input("Recipient:")
            message = input("Message:")
            sender = input("Your name:")

            response = stub.SendMessage(chatApp_pb2.SendMessageRequest(
                message=message, toUser=recipient, froUser=sender))
            print("Response Send Message:", response)

        # Deliver undelivered message - INCOMPLETE
        elif request[0] == "deliverMessage":
            print("hello")

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
