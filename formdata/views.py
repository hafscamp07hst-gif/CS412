from django.shortcuts import render
 
 
# Create your views here.
 
 
def show_form(request):
    '''Show the web page with the form.'''
 
 
    template_name = "formdata/show_form.html"
    return render(request, template_name)

def submit(request):
    '''Process the submitted result and generate an output'''

    template_name = "formdata/confirmation.html"
    if request.POST:
        name = request.POST['name']
        favorite_color = request.POST['favorite_color']

        context = {
            'name' : name,
            'favorite_color' : favorite_color,
        }

    return render(request, template_name, context = context)
 