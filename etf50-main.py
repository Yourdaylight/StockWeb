## For more details, please see the example 9-8 in book of
#  "Python Programming" by ChenChunHui.
#  JamesYe 2019-9-10 Happy Teacher's Day
# This is main enterance of project.
# visit http://127.0.0.1:5000/, you can see the graphic

from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from chart_plot import Chart_Plot
import datetime
app = Flask(__name__)

chart = Chart_Plot("20200101","20201101")
context = {}  # 字典

# 获取前1天或N天的日期，beforeOfDay=1：前1天；beforeOfDay=N：前N天
def getdate(beforeOfDay):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-beforeOfDay)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%Y-%m-%d')
    return re_date
def get_value():
    graph_type=request.form.get("graph_type")
    stock_id=request.form.get("stock_id")
    stock_id2=request.form.get("stock_id2")
    start_date=request.form.get("start_date")
    end_date=request.form.get("end_date")
    # 判断用户选择的日期，若没有选择开始日期，默认绘制最近一年的数据
    start_date = getdate(365) if start_date == "" else start_date
    end_date = getdate(1) if end_date == "" else end_date
    #判断用户输入的股票id，如果为空，默认为000001
    stock_id="000001" if stock_id=="" else stock_id
    stock_id2="000002" if stock_id2=="" else stock_id2

    period=request.form.get("period")
    return {
        "graph_type":graph_type,
        "stock_id":stock_id,
        "stock_id2":stock_id2,
        "start_date":start_date,
        "end_date":end_date,
        "period":period
    }


@app.route('/',methods=["POST","GET"])
def index():
    context['graph'] = chart.twoline_graph()
    return render_template("chars.html", title='Home', context=context)

@app.route('/search',methods=["POST","GET"])
def search():
    #获取用户输入值
    values = get_value()
    print(values)
    graph_type=values.get("graph_type")
    #创建绘图对象
    chart = Chart_Plot(start_date=values.get("start_date"), end_date=values.get("end_date"),stock1=values.get("stock_id"), stock2=values.get("stock_id2"))
    if graph_type=="半年线图":
        context['graph'] = chart.twoline_graph()
    elif graph_type=="k线图":
        context['graph'] = chart.candle_stick(values.get("period"))
    elif graph_type=="高低点":
        context['graph'] = chart.high_low()

    return render_template("chars.html", title='Home', context=context)

if __name__ == '__main__':
    app.run(debug=True)
