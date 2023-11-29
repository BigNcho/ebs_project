from django.shortcuts import render, redirect
from django.http import JsonResponse
#edit
from .models import Question_Answer
from django.http import HttpResponse
from django.template import loader
from ebs.plotly_graph import pie_graph, bar_graph, line_graph


def index(request):
    #edit

    print("첫페이지")
    return render(request, 'main/index.html')

def chart(request):
    #edit
    pie_graph_data = pie_graph()
    bar_graph_data = bar_graph()
    line_graph_data = line_graph()
    
    print("첫페이지")
    return render(request, 'main/chart.html',{'pie_graph_json': pie_graph_data,'bar_graph_json': bar_graph_data,'line_graph_json':line_graph_data,})

def comunity(request):
    #edit

    print("첫페이지")
    return render(request, 'main/comunity.html')