from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
  return render(request, 'todo/home.html')

# функция которая производит регистрацию и аутентификацию пользователя на сайте со своей собственной страницей
def signupuser(request):
    if request.method == 'GET': # определяем какой тут запрос GET или POST. Если метод GET то возвращаем (определяем происходит получение страницы сайта или отправка данных в форму)
      return render(request, 'todo/signupuser.html', {'form':UserCreationForm()}) # страницу signupuser.html
    else: # иначе (если метод POST)
      if request.POST['password1'] == request.POST['password2']: # если пароль 1 совпадает с паролем 2
      # пытаемся создать нового пользователя
        try:
          # записываем в переменную user полученный при отправке логин и пароль
          user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
          user.save() # созраняем их
          login(request, user) # пробуем залогинится с помощью функции логин, которая принимает в себя запрос и сохраненные логин и пароль
          return redirect('currenttodos') # и в итоге возвращаем другую функцию currenttodos, которая возращает нам другую страницу (страницу пользователя)
        except IntegrityError: # при возникновении ошибки когда такой пользователь уже существует, возвращаем
          return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Пользователь уже был использован, попробуйте другой пароль'}) # ту же страницу, только с надписью ошибки
      else: # если пароль 1 НЕ совпадает с паролем 2
         return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Password didnt match'}) # возвращаем ту же страницу с надписью ошибки что пароль не совпадает

# функция входа в свой аккаунт
def loginuser(request):
  if request.method == 'GET': # определяем какой тут запрос GET или POST. Если метод GET то возвращаем (определяем происходит получение страницы сайта или отправка данных в форму)
    return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()}) # страницу loginuser.html
  else: # иначе (если метод POST)
    user = authenticate(request, username=request.POST['username'], password=request.POST['password']) # проверяем совпадает ли наш пользователь и пароль с имеющимися
    if user is None: # если такие НЕ имеются, то возвращаем тот же шаблон с надписью что пользователь не найден
      return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Пользователь не найден'})
    else: # иначе вызваем функцию логин, которая входит на страницу пользователя со всеми его задачами
      login(request, user) 
      return redirect('currenttodos')

# функция выхода из страницы пользователя
@login_required
def logoutuser(request):
  if request.method == 'POST':
    logout(request)
    return redirect('home')

@login_required
def createtodo(request):
  if request.method == 'GET':
    return render(request, 'todo/createtodo.html', {'form':TodoForm()})
  else:
    try:
      form = TodoForm(request.POST)
      newtodo = form.save(commit=False)
      newtodo.user = request.user
      newtodo.save()
      return redirect('currenttodos')
    except ValueError:
      return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'error':'Bad data passed in'})
  
@login_required
# функция возвращающая страницу пользователя со всеми его заметками      
def currenttodos(request):
  # вывод только тех записей, которые принадлежать пользователю (и вывод задач у которых дата завершения пустая)
  todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
  return render(request, 'todo/currenttodos.html', {'todos': todos})

@login_required
def completedtodos(request):
  todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
  return render(request, 'todo/completedtodos.html', {'todos':todos})

@login_required
def viewtodo(request, todo_pk):
  todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
  if request.method == 'GET':
    form = TodoForm(instance=todo)
    return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
  else:
    try:
      form = TodoForm(request.POST, instance=todo)
      form.save()
      return redirect('currenttodos')
    except ValueError:
      return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form, 'error':'Bad info'})

@login_required
def completetodo(request, todo_pk):
  todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
  if request.method == 'POST':
    todo.datecompleted = timezone.now()
    todo.save()
    return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
  todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
  if request.method == 'POST':
    todo.delete()
    return redirect('currenttodos')