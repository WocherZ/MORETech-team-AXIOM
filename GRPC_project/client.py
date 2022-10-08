import grpc
import api_pb2_grpc as pb2_grpc
import api_pb2 as pb2


def run():
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = pb2_grpc.ApiStub(channel)
        print(stub.getNews(pb2.UserRole(role=pb2.RoleType.ACCOUNTANT_ROLE)))


run()
