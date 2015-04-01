import pandas as pd
import matplotlib.pyplot as plt
import math

ccys = ['CAD', 'PHP', 'INR']
holding_period = 5
conf = .95
horizon = 260
remove_zeros = True
scale_time = True

ci = (1-conf)



def getFXData(ccys, start_date='', end_date=''):
	curves = {'CAD': 'DataFiles/CAD_03132015_10yr.csv', 'PHP':'DataFiles/PHP_03132015_10yr.csv', 'INR':'DataFiles/INR_03132015_10yr.csv'}
	fx_data = ''
	for curve in ccys:
		print('Curve is: ' + str(curve))
		curve_data = pd.DataFrame.from_csv(curves[curve], infer_datetime_format=True)
		ccy_curve = pd.DataFrame()
		ccy_curve['Date'] = curve_data['Date']
		ccy_curve[curve] = curve_data['Spot Rate']
		if len(fx_data)==0:
			fx_data = ccy_curve
		else:
			fx_data = fx_data.merge(ccy_curve, on='Date')
	fx_data['Date'] = pd.to_datetime(fx_data['Date'])
	if start_date!='' and end_date!='':
		df = pd.DataFrame()
		df['Date'] = pd.date_range(start=start_date, end=end_date)
		fx_data = df.merge(fx_data, on='Date')
	return fx_data

def getExposureData():
	balance_data = pd.DataFrame.from_csv('DataFiles/balances.csv', index_col=False)
	return balance_data

def getPnL(fx_data, balance_data, horizon, holding_period, chg_file='chg.csv'):
	pnl_df = pd.DataFrame()
	chg_df = pd.DataFrame()
	chg_df['Date'] = fx_data['Date']
	pnl_df['Date'] = fx_data['Date']
	for column in fx_data.columns:
		print('Column is: ' + str(column))
		if column == 'Date':
			print('Skipping Date Column')
			continue
		else:
			chg_df[column] = fx_data[column].pct_change(holding_period)
		chg_df = chg_df.dropna()
	for column in fx_data.columns:
		if column == 'Date':
			print('Skipping Date Column')
			continue
		else:
			exp = balance_data[column][0]
			print('Balance is: ' + str(exp))
			pnl_df[column]=chg_df[column] * exp
	pnl_df = pnl_df.dropna()
	pnl_df.set_index(pnl_df['Date'])
	pnl_df['PnL'] = pnl_df.ix[:,1:].sum(axis=1)
	if scale_time:
		scale_factor = math.sqrt(horizon/holding_period)
		pnl_df['PnL'] = pnl_df['PnL']*scale_factor
	pnl_df['Date'] = pd.to_datetime(pnl_df['Date'])
	if remove_zeros:
		pnl_df = pnl_df.loc[(pnl_df.ix[:,1:]!=0).all(axis=1)]
	chg_df.to_csv(chg_file, index_col=False)
	print('Pnl DF is: ' + str(pnl_df.head()))
	return pnl_df
	

def getVaR(ccys, horizon, holding_period, ci, start_date='', end_date='', fx_file='fx.csv', chg_file = 'chg.csv', pnl_file='pnl.csv' ):
	fx = getFXData(ccys, start_date, end_date)
	fx.to_csv(fx_file, index_col=False)
	exp = getExposureData()
	pnl = getPnL(fx, exp, horizon, holding_period, chg_file=chg_file)
	f=plt.figure(1)
	f.clf()
	f.canvas.set_window_title('FX Rates')
	f=f.add_subplot(len(fx.columns)-1,1,1)
	fx['Date'] = pd.to_datetime(fx['Date'])
	fx.plot(ax=f, x=fx['Date'], subplots=True)
	g= plt.figure(2)
	g.clf()
	g.canvas.set_window_title('PnL Distribution')
	pnl['PnL'].hist(bins=100)
	t = len(pnl['PnL'])
	h = holding_period
	n = t-h+1
	m=1/(1-(h/n)+((h^2-1)/(3*n^2)))
	var = pnl['PnL'].quantile(ci)
	#var = pnl['PnL'].quantile((ci/h))
	var = math.sqrt(m)*var
	pnl.to_csv(pnl_file, index_col=False)
	print('Limit is: ' + str(var))
	#plt.show()
	return {'fx_file': fx_file, 'pnl_file': pnl_file, 'chg_file': chg_file, 'var':var, 'plot':plt}

if __name__ == "__main__":
	getVaR(ccys, horizon, holding_period, ci, start_date='', end_date='')
