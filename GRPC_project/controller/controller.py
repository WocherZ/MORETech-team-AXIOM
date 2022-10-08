from concurrent import futures
import grpc
import controller_pb2
import controller_pb2_grpc
import parser_pb2
import parser_pb2_grpc
import pymorphy2
import pickle
import sklearn
import catboost
import numpy as np
import pandas as pd
import scipy
import re
import random


class Service(controller_pb2_grpc.ControllerServicer):

    def getNews(self, request, context):
        for response in put_news():
            role = handle(text=response.text)
            if role == controller_pb2.Role.DIRECTOR or role == controller_pb2.Role.ACCOUNTANT:
                yield controller_pb2.HandleArticle(header=response.header, text=response.text, role=role)


def text_prepare(text):
    text = clear_text(text)
    txt = lemmatize1(text)
    return [txt]


def model_result(text, vectorizer, model):
    txt = text_prepare(text)
    vect_text = vectorizer.transform(txt)
    return model.predict(vect_text)[0][0]


def clear_text(text):
    prom = re.sub(r'[^a-zA-Zа-яА-Я]', ' ', text).split()
    return ' '.join(prom)


def lemmatize1(text):
    morph = pymorphy2.MorphAnalyzer()
    words = text.split()  # разбиваем текст на слова
    res = list()
    for word in words:
        p = morph.parse(word)[0]
    res.append(p.normal_form)
    return " ".join(res)


def handle(text):
    with open('tf_idf.pkl', 'rb') as f:
        v = pickle.load(f)
        with open('cat.pkl', 'rb') as ff:
            m = pickle.load(ff)
            i = model_result(text=text, vectorizer=v, model=m)
            print(text)
            if (i == 1):
                return controller_pb2.Role.DIRECTOR
            elif (i == 0):
                return controller_pb2.Role.ACCOUNTANT


def put_news():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = parser_pb2_grpc.ParserStub(channel)

        for response in stub.getNews(controller_pb2.google_dot_protobuf_dot_empty__pb2.Empty()):
            yield response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    controller_pb2_grpc.add_ControllerServicer_to_server(Service(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
