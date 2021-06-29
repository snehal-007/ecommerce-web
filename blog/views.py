from django.shortcuts import render
from django.http import HttpResponse
from .models import Blog_post

# Create your views here.

def index(request):

    myposts = Blog_post.objects.all()

    return render(request,'blog/index.html',{'myposts':myposts})

def blogPost(request,id):

    post = Blog_post.objects.filter(post_id=id)[0]

    print("post",post)

    print("id-",id)
    
    next_n = id + 1

    prev_p = id - 1
    


    if prev_p == 0:

        prev_p = 1

        return render(request,'blog/blogpost.html',{'post':post,'next':next_n,'prev':prev_p})

    if next_n == 4:

        next_n = 3

        print("yes its equal")

        return render(request,'blog/blogpost.html',{'post':post,'next':next_n,'prev':prev_p})


    return render(request,'blog/blogpost.html',{'post':post,'next':next_n,'prev':prev_p})

    # return render(request,'blog/blogpost.html',{'post':post})
