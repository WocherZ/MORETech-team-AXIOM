from concurrent import futures
import grpc
import parser_pb2
import parser_pb2_grpc
import feedparser


class Service(parser_pb2_grpc.ParserServicer):
    stackNews = []

    feedList = [
        'https://www.kommersant.ru/RSS/news.xml',
        'https://lenta.ru/rss/',
        'https://www.interfax.ru/rss.asp',
        'https://news.rambler.ru/rss/head/?limit=100',
        'https://mirnov.ru/rss/content/10/feed.rss',
        'https://topcor.ru/news/rss.xml'
    ]

    def pullStack(self):
        for feed in self.feedList:
            feed = feedparser.parse(feed)
            for news in feed['items']:
                headline = news.get('title')
                text = news.get('description') if news.get('description') is not None \
                    else news.get('value') \
                    if news.get('value') is not None else news.get('summary')
                self.stackNews.append({'head': headline, 'text': text})

    def getNews(self, request, context):
        if len(self.stackNews) == 0:
            self.pullStack()
        for news in self.stackNews:
            _header = news.get('head')
            _text = news.get('text')
            print(_header)
            print(_text)
            if _text is not None and _header is not None:
                yield parser_pb2.PureArticle(header=_header, text=_text)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    parser_pb2_grpc.add_ParserServicer_to_server(Service(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
