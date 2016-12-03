import socket
import urllib.parse
from utils import log
from routes import route_static

# 导入 路由函数
from routes import route_dict as route_dict_main
from routes_todo import route_dict as route_dict_todo
from routes_api_todo import route_dict as route_dict_api_todo


"""
GET /subject/25662329/?tag=%E5%96%9C%E5%89%A7&from=gaia_video HTTP/1.1
Host: movie.douban.com
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Referer: https://movie.douban.com/
Accept-Encoding: gzip, deflate, sdch, br
Accept-Language: zh-CN,zh;q=0.8
Cookie: bid=g5ruU30n87s; ll="118318"; __utma=223695111.1596537003.1471425964.1471425964.1471425964.1; __utmz=223695111.1471425964.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=30149280.322439000.1471425964.1471425964.1471425964.1; __utmz=30149280.1471425964.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); gr_user_id=9365ee5a-3abc-48a2-8d85-44d18fd0689d; viewed="4866934_6049132_11976406_1886640"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1480447226%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.4cf6=b6155b80fc12ecd5.1470500067.5.1480447267.1472117962.; _pk_ses.100001.4cf6=*
DNT: 1
"""


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        # lines = header.split('\r\n')
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        self.add_cookies()

    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


#
request = Request()


def error(request, code=404):
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def parsed_path(path):
    """
    /subject/25662329/?tag=%E5%96%9C%E5%89%A7&from=gaia_video
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(path):
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    log('path and query', path, query)
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = {
        '/static': route_static,
        # path: route_function
    }
    r.update(route_dict_main)
    r.update(route_dict_todo)
    r.update(route_dict_api_todo)
    response = r.get(path, error)
    print('request', request)
    return response(request)


def run(host='', port=3000):
    """
    启动服务器
    """
    log('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        while True:
            # 监听 接受 读取请求数据 解码成字符串
            s.listen(3)
            connection, address = s.accept()
            r = connection.recv(1000)
            r = r.decode('utf-8')
            if len(r.split()) < 2:
                continue
            path = r.split()[1]
            # 设置 request 的 method
            request.method = r.split()[0]
            request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            # 把 body 放入 request 中
            request.body = r.split('\r\n\r\n', 1)[1]
            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_path(path)
            # 把响应发送给客户端
            connection.sendall(response)
            # 处理完请求, 关闭连接
            connection.close()


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='',
        port=3000,
    )
    run(**config)
