from models import Todo
from response import template
from response import response_with_headers
from response import redirect
from utils import log


def route_index(request):
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    todos = Todo.all()
    log('todos', todos)

    def todo_tag(t):
        status = t.status()
        return '<p class="{}">{} {}@{}<a href="/todo/complete?id={}">完成</a><a href="/todo/delete?id={}>删除</a><a href="/todo/edit?id={}>修改</a></p>'.format(
            status,
            t.id,
            t.content,
            t.created_time,
            t.id,
            t.id,
            t.id
        )
    todo_html = '\n'.join([todo_tag(t) for t in todos])
    body = template('todo_index.html', todos=todo_html)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_add(request):
    # headers = {
    #     'Content-Type': 'text/html',
    # }
    form = request.form()
    o = Todo(form)
    o.save()
    return redirect('/todo')


def route_complete(request):
    # headers = {
    #     'Content-Type': 'text/html',
    # }
    id = int(request.query.get('id', -1))
    o = Todo.find(id)
    o.toggleComplete()
    o.save()
    return redirect('/todo')

route_dict = {
    '/todo': route_index,
    '/todo/add': route_add,
    '/todo/complete': route_complete,
}
