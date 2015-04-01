from flask import Flask, jsonify, request, send_from_directory, redirect, session, send_file
import flask_cors_util as cors
import var_calc, logging, random, time, math
from io import StringIO, BytesIO


app = Flask(__name__)

app.secret_key = 'F12!r47j\3yX R~X@H!jpxLwf/,?KT'
rates={}
hists={}
chg_files={}
pnl_files={}
fx_files={}

@app.route('/')
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def health_check():
    return 'Server is Running'
	
@app.route('/runVARModel', methods=['POST'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def runVarModel():
	try:
		req = request.get_json()
		ccys = req['ccy']
		start_date = req['start_date']
		end_date = req['end_date']
		horizon = int(req['time_horizon'])
		holding = int(req['holding_period'])
		ci = float(req['ci'])
		print('CI is: ' + str(ci))
		results = var_calc.getVaR(ccys, horizon, holding, ci, start_date=start_date, end_date=end_date)
		img1 = ''
		img2 = ''
		img1 = BytesIO()
		img2 = BytesIO()
		plt = results['plot']
		user_key = str(math.floor(random.random() * time.time() + time.time()))
		#rate_graph = user_key + '_rate_graph.png'
		#var_hist = user_key + '_var_hist.png'
		#plt.figure(1).savefig(rate_graph)
		#plt.figure(2).savefig(var_hist)
		plt.figure(1).savefig(img1)
		plt.figure(2).savefig(img2)
		img1.seek(0)
		img2.seek(0)
		rates[user_key] = img1
		hists[user_key] = img2
		var = results['var']
		resp_obj = {'var': str(var), 'fx_file': results['fx_file'], 'chg_file': results['chg_file'], 'pnl_file': results['pnl_file'], 'user_key':str(user_key), 'time_horizon':str(horizon), 'holding_period':str(holding), 'ci':str(ci), 'ccys':ccys, 'start_date':str(start_date), 'end_date':str(end_date)}
		fx_files[user_key] = results['fx_file']
		pnl_files[user_key] = results['pnl_file']
		chg_files[user_key] = results['chg_file']
		return jsonify(**resp_obj)
	except Exception as e:
		logging.exception('Error with Running Var Model')
		return None
		
@app.route('/getRateGraph/<user_key>', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getRateGraph(user_key):
	user_key = str(user_key)
	file = rates[user_key]
	del rates[user_key]
	#file = user_key + '_rate_graph.png'
	return send_file(file, mimetype='image/png')
	
@app.route('/getVarHist/<user_key>', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getVarHist(user_key):
	user_key = str(user_key)
	file = hists[user_key]
	del hists[user_key]
	#file = user_key + '_var_hist.png'
	return send_file(file, mimetype='image/png')
	
@app.route('/getChgFile/<user_key>', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getChgFile(user_key):
	user_key = str(user_key)
	file = chg_files[user_key]
	#file = user_key + '_var_hist.png'
	return send_file(file, mimetype='text/csv', as_attachment=True, attachment_filename='chg.csv')
	
@app.route('/getPnlFile/<user_key>', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getPnlFile(user_key):
	user_key = str(user_key)
	file = pnl_files[user_key]
	#file = user_key + '_var_hist.png'
	return send_file(file,mimetype='text/csv', as_attachment=True, attachment_filename='pnl.csv')
	
@app.route('/getFxFile/<user_key>', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getFxFile(user_key):
	user_key = str(user_key)
	file = fx_files[user_key]
	#file = user_key + '_var_hist.png'
	return send_file(file, mimetype='text/csv', as_attachment=True, attachment_filename='fx.csv')
	
@app.route('/Rates', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getRates():
	return str(rates.keys())
	
@app.route('/Hists', methods=['GET'])
@cors.cross_origin(headers=['Content-Type'], origins='*', send_wildcard=True)
def getHists():
	return str(hists.keys())
	
	
if __name__ == '__main__':
    app.run(debug=True)
