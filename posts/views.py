from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Post, Group

User = get_user_model()


def index(request):
    """"Представление главной страницы постов"""
    post_list = Post.objects.order_by('-pub_date')
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядить так:
    # post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    """"Представление страницы сообщества"""
    group = get_object_or_404(Group, slug=slug)
    paginator = Paginator(
        Post.objects.filter(group=group).order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        "group": group, "page": page})


@login_required
def new_post(request):
    """Представление формы новой записи"""
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect("index")
    return render(request, "post_new.html", {'form': form})


def profile(request, username):
    """"Представление страницы профайла"""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    paginator = Paginator(posts.order_by('-pub_date'), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    number_of_posts = posts.count()
    context = {
        'author': user,
        'number_of_posts': number_of_posts,
        'page': page,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    """"Представление страницы отдельной записи"""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post.html", {"author": author, "post": post})


@login_required
def post_edit(request, username, post_id):
    """"Представление страницы редактирования записи"""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('post', post_id=post.id, username=post.author.username)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('post', post_id=post.id, username=post.author.username)
    return render(request, 'post_new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500) 