import traceback
from datetime import datetime

import plotly as py
import plotly.graph_objs as go

import tool

pyplt = py.offline.plot
pro = tool.get_pro()


# 读取基金代码与名称字典
# ts.set_token('b94ecd1e37a3628890e89b90e0259b6db72b0ae0b17dadd2c28c5c4c')
# pro = ts.pro_api()
# df = pd.read_csv("stock_code.csv")
# df = pro.daily(ts_code='000001.sz', start_date='20190701', end_date='20190930')#直接保存

class Chart_Plot:
    global pro, df

    def __init__(self, **params):

        # 处理参数格式，符合tushare调用规范
        # import pdb
        # pdb.set_trace()
        self.start_date = params.get("start_date").replace("-", "")
        self.end_date = params.get("end_date").replace("-", "")
        # 获取指定基金代码的名称
        self.stock1_code = tool.getStockCode(params.get("stock_id", "000001"))
        self.name1 = tool.getName(self.stock1_code)
        self.stock1 = None
        # 获取要对比的基金代码的名称
        self.stock2_code = tool.getStockCode(params.get("stock_id2", "000002"))
        self.stock2 = pro.daily(ts_code=self.stock2_code, start_date=self.start_date, end_date=self.end_date)
        self.name2 = tool.getName(self.stock2_code)
        self.stock2 = None
        self.index_type = params.get("index_type")
        self.graph_type = params.get("graph_type")
        self.a_h = params.get("a_h")
        self.graph_title = "{},{}--{}".format(self.stock1_code, self.name1, self.graph_type)

    def candle_stick(self, period="day"):  # 日K线图
        # 默认获取日k,如果period不为日k，则获取对应值
        try:
            if not self.stock1_code:
                return "该基金代码不存在", self.graph_title
            if period == "周k":
                self.stock1 = pro.weekly(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)
            elif period == "月k":
                self.stock1 = pro.monthly(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)
            else:
                self.stock1 = pro.daily(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)
        except Exception as e:
            traceback.print_exc()
            return str(e),self.graph_title

        strdate = self.stock1['trade_date'].tolist()
        # 日期字符串转时间序列
        date = [datetime.strptime(i, '%Y%m%d') for i in strdate]
        candle_trace = go.Candlestick(x=date,
                                      open=self.stock1.open,
                                      high=self.stock1.high,
                                      low=self.stock1.low,
                                      close=self.stock1.close,
                                      increasing=dict(line=dict(color='#ff0000')),
                                      decreasing=dict(line=dict(color='#00ff00')),
                                      name=self.name1)
        candle_data = [candle_trace]
        candle_layout = {'title': self.name1, 'yaxis': {'title': '价格'}}
        candle_fig = dict(data=candle_data, layout=candle_layout)
        div = pyplt(candle_fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div,self.graph_title

    def twoline_graph(self):  # 半年线图
        # self.stock1['close']取出来的值都是带有索引值的两列的矩阵，具体看excl表格
        # tolist函数则将他们变为列表，除去索引值
        if not self.stock1_code:
            return "该基金代码不存在", self.graph_title
        self.stock1 = pro.daily(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)
        close = self.stock1['close'].tolist()
        strdate = self.stock1['trade_date'].tolist()
        date = [datetime.strptime(i, '%Y%m%d') for i in strdate]

        trace = [go.Scatter(
            x=date,
            y=close
        )]
        layout = dict(
            xaxis=dict(title='日期'),
            yaxis=dict(title='价格')
        )

        fig = dict(data=trace, layout=layout)
        div = pyplt(fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div, self.graph_title

    def high_low(self):
        if not self.stock1_code:
            return "该基金代码不存在", ""
        self.stock1 = pro.daily(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)
        high = self.stock1['high'].tolist()
        low = self.stock1['low'].tolist()
        strdate = self.stock1['trade_date'].tolist()
        date = [datetime.strptime(i, '%Y%m%d') for i in strdate]

        trace = [go.Scatter(
            x=date,
            y=high
        ),
            go.Scatter(
                x=date,
                y=low
            )
        ]
        layout = dict(
            title=self.stock1_code + ":" + self.name1,
            xaxis=dict(title='日期'),
            yaxis=dict(title='价格')
        )
        # print (layout)
        # {'title': 'ETF50', 'xaxis': {'title': '日期'}, 'yaxis': {'title': '价格'}}
        fig = dict(data=trace, layout=layout)
        # print (fig)
        div = pyplt(fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div, self.graph_title

    def plot_pes(self):
        try:
            if not self.stock1_code:
                return "该基金代码不存在", self.graph_title
            if self.index_type == 'LYR':
                self.stock1 = pro.daily_basic(ts_code=self.stock1_code, start_date=self.start_date,
                                              end_date=self.end_date,
                                              fields='trade_date,pe')
            else:
                self.stock1 = pro.daily_basic(ts_code=self.stock1_code, start_date=self.start_date,
                                              end_date=self.end_date,
                                              fields='trade_date,pe_ttm')
        except Exception as e:
            traceback.print_exc()
            return str(e),self.graph_title
        df = self.stock1
        # 处理数据
        dates, pes = [], []
        for idx, row in df.iterrows():
            trade_date, pe = row[0], row[1]
            current_date = datetime.strptime(trade_date, '%Y%m%d')
            dates.append(current_date)
            pes.append(pe)

        # 画图语句：go.Scatter
        trace = [go.Scatter(
            x=dates,
            y=pes
        )]
        layout = dict(
            title=self.name1,
            xaxis=dict(title='日期'),
            yaxis=dict(title='价格')
        )
        fig = dict(data=trace, layout=layout)
        div = pyplt(fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div, self.graph_title

    def plot_amplitude(self):
        graph_title = "{},{};{},{}--{}".format(self.stock1_code, self.name1,
                                             self.stock2_code, self.name2, self.graph_type)
        if not self.stock1_code:
            return "该基金代码不存在", graph_title
        if not self.stock2_code:
            return "该对比基金代码不存在", graph_title
        self.stock1 = pro.daily(ts_code=self.stock1_code, start_date=self.start_date, end_date=self.end_date)
        self.stock2 = pro.daily(ts_code=self.stock2_code, start_date=self.start_date, end_date=self.end_date)

        # 振幅计算公式：A=(high-low)/pre_close
        dates1, dates2, As1, As2 = [], [], [], []
        for idx, row in self.stock1.iterrows():
            date1, high1, low1, preclose1 = row[1], row[3], row[4], row[6]
            A1 = ((high1 - low1) / preclose1) * 100
            current_date = datetime.strptime(date1, '%Y%m%d')
            dates1.append(current_date)
            As1.append(A1)
        for idx, row in self.stock2.iterrows():
            date2, high2, low2, preclose2 = row[1], row[3], row[4], row[6]
            A2 = ((high2 - low2) / preclose2) * 100
            current_date = datetime.strptime(date2, '%Y%m%d')
            dates2.append(current_date)
            As2.append(A2)
        # 计算共同交易日的振幅比较
        Af = dict(zip(dates1, As1))  # dict字典 zip打包为元组
        As = dict(zip(dates2, As2))
        dates, AF, AS = [], [], []
        for key, value in Af.items():
            if key in As:
                AF.append(Af[key])
                AS.append(As[key])
                dates.append(key)

        trace = [go.Scatter(
            x=dates,
            y=AF,
            name="{} {} ".format(self.name1, self.stock1_code)
        ),
            go.Scatter(
                x=dates,
                y=AS,
                name="{} {} ".format(self.name2, self.stock2_code)
            )
        ]
        layout = dict(
            title=self.stock1_code + ":" + self.name1,
            xaxis=dict(title='日期'),
            yaxis=dict(title='价格')
        )
        fig = dict(data=trace, layout=layout)
        # print (fig)
        div = pyplt(fig, output_type='div', include_plotlyjs=False, auto_open=False, show_link=False)
        return div, graph_title

    def plot_ah(self):
        try:
            is_a_h = tool.judgeAH(self.stock1_code)  # 1为A股，2为H股
            try:
                if self.a_h == "A/H":
                    self.stock2_code = tool.findHcode(self.stock1_code)
                else:
                    self.stock2_code = tool.findAcode(self.stock1_code)
            except Exception as e:
                return str(e),self.graph_title
            self.stock2 = pro.hk_daily(ts_code=self.stock2_code, start_date=self.start_date, end_date=self.end_date)
            # exchangeRate = tool.hdk2rmb()  # 汇率
        except Exception as e:
            return str(e),self.graph_title
