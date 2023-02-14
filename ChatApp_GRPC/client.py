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

        # List accounts function - COMPLETE (check wildcard logic)
        elif request == "listAccounts":
            if len(request) > 1:
                wildcard = input("Enter any text: ")
            response = stub.ListAccounts(
                chatApp_pb2.ListAccountsRequest(wildcard=wildcard))
            print("List accounts response: ", response)

        # Send message function - INCOMPLETE
        elif request[0] == "sendMessage":
            message = request[1]
            recipient = request[2]
            sender = request[3]

            send_response = stub.SendMessage([message, recipient, sender])
            print("Send message response: ", send_response)

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
