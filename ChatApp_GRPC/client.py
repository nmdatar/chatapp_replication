import grpc
import chatApp_pb2
import chatApp_pb2_grpc

# create a channel to the server
channel = grpc.insecure_channel('localhost:50051')

# create a stub (client)
stub = chatApp_pb2_grpc.ChatAppStub(channel)

# create a request message
create_request = chatApp_pb2.CreateAccountRequest(username='user1')

# call the create account function
create_response = stub.CreateAccount(create_request)
print("Create account response: ", create_response.response)

# call the list accounts function
list_response = stub.ListAccounts(
    chatApp_pb2.ListAccountsRequest(search_username="user"))
print("List accounts response: ", list_response.usernames)

# create a request message for send message
send_request = chatApp_pb2.SendMessageRequest(
    sender='user1', recipient='user2', message='hello user2')

# call the send message function
send_response = stub.SendMessage(send_request)
print("Send message response: ", send_response.response)

# create a request message for retrieve message
retrieve_request = chatApp_pb2.RetrieveMessagesRequest(username='user2')

# call the retrieve message function
retrieve_response = stub.RetrieveMessages(retrieve_request)
print("Retrieve message response: ", retrieve_response.messages)
