from models import Todo
from response import template
from response import response_with_headers
from response import redirect
from utils import log


def route_index():
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    todos = Todo.all()
    log('todos', todos)

    def todo_tag(t):
        status = t.status()
        return '<p class="{}">{} {}@{}<a href="/todo/complete?id={}">完成</a></p>'.format(
            status,
            t.id,
            t.content,
            t.created_time,
            t.id,
        )
    todo_html = '\n'.join([todo_tag(t) for t in todos])
    body = template('todo_index.html', todos=todo_html)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_add(request):
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    form = request.form()
    o = Todo(form)
    o.save()
    body = o.json_str()
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_complete(request):
    id = int(request.query.get('id', -1))
    o = Todo.find(id)
    o.toggleComplete()
    o.save()
    return redirect('/todo')

route_dict = {
    '/api/todo': route_index,
    '/api/todo/add': route_add,
    '/api/todo/complete': route_complete,
}
