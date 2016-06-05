import operate_sql

# グラフ化に必要なものの準備
import matplotlib
# matplotlib.rc({'backend': 'TkAgg'})
import matplotlib.pyplot as plt
import _
from _ import p, d, MyObject, MyException
# データの扱いに必要なライブラリ
import pandas as pd
import numpy as np
import datetime as dt
# import seaborn as sns
# sns.set_style("darkgrid")
# plt.style.use('ggplot') 
# font = {'family' : 'Times New Roman'}
# matplotlib.rc('font', **font)
if __name__ == '__main__':
	# operate_sql.save_stats(stats_dict = {'whose': 'sys', 'status': '', 'number': 114513})
	datas = operate_sql.get_stats(whose = 'LiveAI_Umi', status = 'time_line_cnt')
	df = pd.DataFrame({
		'value' : [data[0] for data in datas],
		'time' : [data[1] for data in datas]
		})
	print(df)
	# # print(df.dtypes)
	# # df.plot(y=['value', 'time'], figsize=(16,4), alpha=0.5)
	# # plt.savefig('hoge.png')
	# x = np.random.normal(size=100)
	# # titanic = sns.load_dataset("titanic") ##kaggleで有名な、タイタニック号の生死者データ
	# # tips = sns.load_dataset("tips")  ## お店の食事時間と会計総額とチップの関係のデータ
	# iris = sns.load_dataset("iris")  ## Rでお馴染みのアヤメの統計データ
	# # sns.jointplot(x='time', y='value', data=df)
	# sns.pairplot(iris, hue="species")
	# plt.savefig('hoge.png')


