import pytest
import grpc
# from grpc_testing import server_from_descriptor

from proto import chatapp_pb2 as chatapp
from proto import chatapp_pb2_grpc as rpc

address = 'localhost'
port = 11912


@pytest.fixture(scope="module")
def grpc_channel():
    channel = grpc.insecure_channel(address + ':' + str(port))
    print("channel", channel)
    yield channel


@pytest.fixture(scope='module')
def grpc_stub(grpc_channel):
    print("grpc_channel", grpc_channel)
    return rpc.ChatServiceStub(grpc_channel)


def test_login(grpc_stub):
    # Set up test data
    username = 'testuser'

    # Create login request
    request = chatapp.Account(username=username)
    # Call the gRPC login function
    response = grpc_stub.LoginAccount(request)

    # Verify the response is successful
    assert response.success == True


def test_logout(grpc_stub):
    username = "testuser"
    # Create login request
    request = chatapp.Account(username=username)
    # Call the gRPC login function
    response = grpc_stub.LoginAccount(request)

    # Verify the response is successful
    assert response.success == True
