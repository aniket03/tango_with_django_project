from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {"categories":category_list,"pages":page_list}
	return render(request, "rango/index.html", context_dict)


def about(request):
	return render(request, "rango/about.html", {})

def show_category(request,category_name_slug):
	context_dict = {}
	try:
		cat = Category.objects.get(slug=category_name_slug)
		pages=Page.objects.filter(category=cat)
		context_dict["pages"]=pages
		context_dict["category"]=cat
	except:
		context_dict["pages"]=None
		context_dict["category"]=None
	return render(request, "rango/category.html",context_dict)

@login_required
def add_category(request):
	form = CategoryForm()

	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors

	return render(request,'rango/add_category.html',{'form':form})

@login_required
def add_page(request,category_name_slug):
## Here we will add category_name_slug cos each page will be added in a category
## category and add_page link must be linked
	try:
		cat=Category.objects.get(slug=category_name_slug)
	except:
		cat=None
	form = PageForm()
	if request.method == "POST":
		form = PageForm(request.POST)
		if form.is_valid():
			page = form.save(commit=False)
			page.category = cat
			page.save()
			return show_category(request,category_name_slug)
		else:
			print form.errors	##These will be printed for console can also skip

	return render(request,"rango/add_page.html",{'form':form,'category':cat})


def register(request):
	registered = False
	if request.method == "POST":
		user_form=UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered=True
		else:
			print user_form.errors, profile_form.errors
	else:
		user_form=UserForm()
		profile_form = UserProfileForm()

	return render(request,'rango/register.html',{'registered':registered,'user_form':user_form,'profile_form':profile_form})


def user_login(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request,user)
				return HttpResponseRedirect(reverse('index'))

			else:
				return HttpResponse("Your rango account is disabled")
		else:
			error_msg = "Invalid login details. Please Enter the details again !!!"
			return render(request,'rango/login.html',{'error_msg':error_msg})
	else:
		return render(request,'rango/login.html',{'error_msg':None})

@login_required
def restricted(request):
	return render(request,'rango/restricted.html',{})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

