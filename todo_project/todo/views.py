from django.shortcuts import render
from django.http import HttpResponse
from .models import Todo
    
# Create your views here.
def index(request):
    return HttpResponse("Hello World")

def todo_list(request):
    # add task
    if 'add_task' in request.POST:
        pass
    # edit task
    if 'edit_task' in request.POST:
        pass
    # delete task
    if 'delete_task' in request.POST:
        pass
    # clearall
    if 'clear_all' in request.POST:
        pass

    # return render(request, 'todo_list.html',{
    #     'todos': todos,
    #     'task_count': task_count(),
    # })
