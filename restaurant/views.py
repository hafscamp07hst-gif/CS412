# File: restaurant/views.py
# Name: Sung Tae Hwang
# BU Email: sthwang@bu.edu
# Description: Display the restaurant pages, select a random daily special,
# and process customer orders to calculate totals and pickup times.
import random
import time

from django.shortcuts import render
from django.templatetags.static import static

# Create your views here.
def main(request):
    '''Display the restaurant's main page with its location, hours, and photo.
    The request here is just the HTTP request sent by the user's brower to the server'''
    template_name = 'restaurant/main.html'
    return render(request, template_name)


special_menus =[
    "Monster Energy Jello : You can feel that ENERGY COMING!",
    "Groot Tree Nutrition Pack : Bet it can't be this FRESH!",
    "Thor Electorlite Soup : Want to feel the power of GOD?",
    "Ironman atom candy : FEEL like MIT",
    "Thanos snap popcorn : When life is tough..",
    "Rocket Fuel Battery bar : Absolute BEAST"
]
def order(request):
    '''Select a random daily special and display the restaurant's order form.
        The request here is just the HTTP request sent by the user's brower to the server'''
    
    template_name = 'restaurant/order.html'
    context ={
        "special_menu": random.choice(special_menus),
    }
    return render(request, template_name, context= context)



def confirmation(request):
    '''Read the submitted order and display an order confirmation.

    Determine the selected menu items and options, calculate the total
    price, and generate a pickup time 30 to 60 minutes after the order.
    Request here is the HTTP request containing the submitted menu selections,
    special instructions, and customer information in request.POST.'''
    if request.POST:
        template_name = 'restaurant/confirmation.html'

        menu1 = ""
        menu1opt = ""
        menu2 = ""
        menu3 = ""
        menu4 = ""
        special_menu = ""
        instruction = request.POST['instruction']
        total = 0
        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST['email']
        if 'menu1' in request.POST:
            menu1 = "Luke's Hot Pot"
            total +=25
            if 'menu1opt' in request.POST:
                total +=5
                menu1opt = "with Extra Meat"


        if 'menu2' in request.POST:
            total+=30
            menu2 = "Luke's Malatang"

        if 'menu3' in request.POST:
            total+=28
            menu3 = "Luke's Shrimp Pasta"

        if 'menu4' in request.POST:
            total+=5
            menu4 = "Luke's Ice Cream"

        if 'special' in request.POST:
            total+=5
            special_menu = request.POST['special']
        context ={
            "current_time" : time.ctime(),
            'ready_time' : time.strftime(
                '%c', time.localtime(time.time()+ random.randint(30,60)*60)),
            'menu1' : menu1,
            'menu2':menu2,
            'menu3':menu3,
            'menu4':menu4,
            'special':special_menu,
            'menu1opt' : menu1opt,
            'instruction' : instruction,
            'total' :total,
            'name' :name,
            'phone':phone,
            'email':email,

        }
        return render(request, template_name, context = context)

    template_name='restaurant/order.html'
    context ={
        "special_menu": random.choice(special_menus),
    }
    return render(request, template_name, context = context)
