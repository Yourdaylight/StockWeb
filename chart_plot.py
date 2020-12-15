
from datetime import datetime
import tushare as ts
import pandas as pd
import plotly as py
import plotly.graph_objs as go
pyplt = py.offline.plot
#读取股票代码与名称字典
ts.set_token('b94ecd1e37a3628890e89b90e0259b6db72b0ae0b17dadd2c28c5c4c')
pro = ts.pro_api()

df=pd.read_csv("stock_code.csv")
# df = pro.daily(ts_code='000001.sz', start_date='20190701', end_date='20190930')#直接保存

class Chart_Plot:
    def __init__(self,start_date,end_date,stock1="000001",stock2="000002"):
        #处理参数格式，符合tushare调用规范
        self.start_date=start_date.replace("-","")
        self.end_date=end_date.replace("-","")
        #获取指定股票代码的名称
        try:
            temp=df.loc[df.ts_code.str.contains(stock1)]
            self.stock1_code=temp["ts_code"].values[0]
            self.stock1=pro.daily(ts_code=self.stock1_code, start_date=start_date, end_date=end_date)
            self.name1=temp['name'].values[0]
            #获取要对比的股票代码的名称
            temp = df.loc[df.ts_code.str.contains(stock2)]
            self.stock2_code = temp["ts_code"].values[0]
            self.stock2=pro.daily(ts_code=self.stock2_code, start_date=start_date, end_date=end_date)
            self.name2=temp['name'].values[0]
            print(self.stock1)
        except:
            return

    def candle_stick(self,period="day"):#日K线图
        #默认获取日k,如果period不为日k，则获取对应值
        if period=="周k":
            self.stock1=pro.weekly(ts_code=self.stock1_code,start_date=self.start_date,end_date=self.end_date)
        elif period=="月k":
            self.stock1 = pro.monthly(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)

        strdate =self.stock1['trade_date'].tolist()
        #日期字符串转时间序列
        date=[]
        for i in strdate:
            X = datetime.strptime(i, '%Y%m%d')           
            date.append(X)         
        candle_trace = go.Candlestick(x = date,
                                      open = self.stock1.open,
                                      high = self.stock1.high,
                                      low = self.stock1.low,
                                      close = self.stock1.close,
                                      increasing=dict(line=dict(color= '#ff0000')),
                                      decreasing=dict(line=dict(color= '#00ff00')),
                                      name = self.name1)
        candle_data = [candle_trace]
        candle_layout = {'title': self.name1,'yaxis': {'title': '价格'}}
        candle_fig = dict(data=candle_data, layout=candle_layout)
        div = pyplt(candle_fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div
    
    
    def twoline_graph(self): #半年线图
        #self.stock1['close']取出来的值都是带有索引值的两列的矩阵，具体看excl表格
        #tolist函数则将他们变为列表，除去索引值

        close = self.stock1['close'].tolist()
        strdate = self.stock1['trade_date'].tolist()
        date=[]
        for i in strdate:
            X = datetime.strptime(i, '%Y%m%d')           
            date.append(X)         

        # 画图语句：go.Scatter
        trace = [go.Scatter(
                            x=date,
                            y=close
                            )]
        #print (trace)  
        #[Scatter({'x': [2019-09-30 00:00:00, 2019-09-27 00:00:00.....
                
        layout = dict(
              title=self.name1,
              xaxis=dict(title='日期'),
              yaxis=dict(title='价格')
              )
        #print (layout)
        #{'title': 'ETF50', 'xaxis': {'title': '日期'}, 'yaxis': {'title': '价格'}}
        fig = dict(data=trace, layout=layout)  
        #print (fig)
        div = pyplt(fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        #print (div)
        return div

    def high_low(self):
        high = self.stock1['high'].tolist()
        low = self.stock1['low'].tolist()
        strdate = self.stock1['trade_date'].tolist()
        date = []
        for i in strdate:
            X = datetime.strptime(i, '%Y%m%d')
            date.append(X)

            # 画图语句：go.Scatter
        trace = [go.Scatter(
            x=date,
            y=high
        ),
            go.Scatter(
                x=date,
                y=low
            )
        ]
        # print (trace)
        # [Scatter({'x': [2019-09-30 00:00:00, 2019-09-27 00:00:00.....

        layout = dict(
            title=self.stock1['ts_code'].values[0]+":"+self.name1,
            xaxis=dict(title='日期'),
            yaxis=dict(title='价格')
        )
        # print (layout)
        # {'title': 'ETF50', 'xaxis': {'title': '日期'}, 'yaxis': {'title': '价格'}}
        fig = dict(data=trace, layout=layout)
        # print (fig)
        div = pyplt(fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div
    
# df=pd.read_csv("stock_code.csv")
# print(df.head())
# print(df.columns)
# print(df.loc[df.ts_code.str.contains("000002")]['ts_code'].values[0])
