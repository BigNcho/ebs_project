from plotly.io import to_json
import plotly.graph_objects as go
import pandas as pd
import numpy as np






def pie_graph():
    labels = ['Apple', 'Banana', 'Tomato', 'Strawberry', 'Melon']
    values = [4500, 3000, 2500, 3500, 5000]
    

    trace = go.Pie(labels=labels, values=values, textinfo='label+value')


    fig = go.Figure(data=[trace])
    fig.update_layout(
        title = "제목",
    
        autosize=True,
        width=508.5,
        height=366.3,
        margin_l=10,
        margin_r=10,
        margin_b=10,
        margin_t=10,
        paper_bgcolor="rgb(39, 46, 90)",
        xaxis=dict(tickfont=dict(color='white')),  # x축 라벨 색상 변경
        yaxis=dict(tickfont=dict(color='white')),  # y축 라벨 색상 변경
        legend=dict(font=dict(color='white'))
        )
   
    pie_graph_json = to_json(fig)
    # graph_json=fig.show()
    # 그래프를 JSON 문자열로 변환
    return  pie_graph_json


def bar_graph():
    months  = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul','Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = pd.date_range('2023-01-01', periods=12)
    random_1 = np.random.randint(0, 100, 12)
    random_2 = np.random.randint(0, 500, 12)

    colors1 = ['indianred']*12
    colors1[4]='crimson'
    colors2 = ['lightsalmon']*12
    colors2[4] = 'LightSkyBlue'
    trace1 = go.Bar(x = months, y=random_1, name = 'random_1', marker_color =colors1)
    trace2 = go.Bar(x = months, y=random_2, name = 'random_2', marker_color =colors2)

    layout = go.Layout(xaxis_tickangle = -45,paper_bgcolor="rgb(39, 46, 90)",)

    data = [trace1,trace2]

    fig = go.Figure(data=data, layout=layout,)
    fig.update_layout(
        autosize=True,
        width=1186.5,
        height=203.5,
        margin_l=10,
        margin_r=10,
        margin_b=20,
        margin_t=10,
        plot_bgcolor="rgb(39, 46, 90)",
        xaxis=dict(tickfont=dict(color='white')),  # x축 라벨 색상 변경
        yaxis=dict(tickfont=dict(color='white')),  # y축 라벨 색상 변경
        legend=dict(font=dict(color='white'))
        )
    
    bar_graph_json = to_json(fig)
    
    return  bar_graph_json

def line_graph():
    num = 50

    randam_var1 = np.random.randint(0, 100, num)
    random_var2 = np.random.randint(0,100, num)
    random_var3 = np.random.randint(0,100, num)


    index = pd.date_range('2023-01-01', periods= num)
    index

    df = pd.DataFrame([randam_var1, random_var2,random_var3]).T
    df.index= index
    df.columns = ['Random_Var1', 'Random_Var2','Random_Var3']
    

    trace1 = go.Scatter(x = df.index, y = df['Random_Var1'], mode='lines', name = df.columns[0])
    trace2 = go.Scatter(x = df.index, y= df['Random_Var2'], mode = 'lines', name= df.columns[1])
    trace3 = go.Scatter(x = df.index, y= df['Random_Var3'], mode = 'lines', name= df.columns[2])
    data = [trace1, trace2,trace3]

    layout = go.Layout(title= 'Random Variables')

    fig = go.Figure(data = data, layout =layout)
    fig.update_layout(
            
            autosize=True,
            width=1186.5,
            height=203.5,
            margin_l=10,
            margin_r=10,
            margin_b=20,
            margin_t=10,
            plot_bgcolor="rgb(39, 46, 90)",
            xaxis=dict(tickfont=dict(color='white')),  # x축 라벨 색상 변경
            yaxis=dict(tickfont=dict(color='white')),  # y축 라벨 색상 변경
            legend=dict(font=dict(color='white')),
            paper_bgcolor="rgb(39, 46, 90)",
            
            )
    line_graph_json = to_json(fig)
    
    return  line_graph_json


# def drop_out():
#     data1 = [1, 2, 3, 4, 5]
#     data2 = [5, 4, 3, 2, 1]

#     # 초기 플롯 생성
#     fig = go.Figure()

#     # 초기 데이터 플롯 추가
#     # trace1 = go.Scatter(x=[1, 2, 3, 4, 5], y=data1, mode='lines', name='Data 1')
#     # trace2 = go.Scatter(x=[1, 2, 3, 4, 5], y=data2, mode='lines', name='Data 2')
#     # fig.add_trace(trace1)
#     # fig.add_trace(trace2)

#     # Dropdown 메뉴 생성
#     updatemenus = [
#         {
#             'buttons': [
#                 {'label': 'Data 1', 'method': 'update', 'args': [{'y': [1, 2, 3, 4, 5]}]},
#                 {'label': 'Data 2', 'method': 'update', 'args': [{'y': [5, 4, 3, 2, 1]}]}
#             ],
#             'direction': 'down',
#             'showactive': True,
#         }
#     ]

#     # 레이아웃 설정
#     fig.update_layout(
#         updatemenus=updatemenus,
#         title='Dropdown Menu Example',
#         xaxis_title='X-axis',
#         yaxis_title='Y-axis',
#     )
#     drop_out_json = to_json(fig)
#     # graph_json=fig.show()
#     # 그래프를 JSON 문자열로 변환
#     return  drop_out_json

