import grpc
from concurrent import futures
import api_pb2_grpc
import api_pb2
import controller_pb2
import controller_pb2_grpc


def get_handle_news():
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = controller_pb2_grpc.ControllerStub(channel)
        for response in stub.getNews(controller_pb2.google_dot_protobuf_dot_empty__pb2.Empty()):
            yield response


class Service(api_pb2_grpc.ApiServicer):
    def getNews(self, request, context):
        for response in get_handle_news():
            if request.role == api_pb2.RoleType.ACCOUNTANT_ROLE:
                return api_pb2.Article(header=response.header, text=response.text)
            elif request.role == api_pb2.RoleType.DIRECTOR_ROLE:
                return api_pb2.Article(header=response.header, text=response.text)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_ApiServicer_to_server(Service(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
