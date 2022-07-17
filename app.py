from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import plotly.express as px
import pandas as PD
import yfinance

#configure Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///model.db'
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    price_data = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<Ticker %r>' % self.id


#index
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        ticker_content = request.form['content']
        info_dictionary = yfinance.Ticker(ticker_content).info
        price_content = info_dictionary["regularMarketPrice"]
        new_ticker = Stock(content=ticker_content, price_data=price_content)

        try:
            db.session.add(new_ticker)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your ticker'

    else:
        tickers = Stock.query.order_by(Stock.date_created).all()
        return render_template('index.html', tickers=tickers)

#delete
@app.route('/delete/<int:id>')
def delete(id):
    ticker_to_delete = Stock.query.get_or_404(id)

    try:
        db.session.delete(ticker_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

#update
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    ticker = Stock.query.get_or_404(id)

    if request.method == 'POST':
        ticker.content = request.form['content']
        info_dictionary = yfinance.Ticker(ticker.content).info
        ticker.price_data = info_dictionary["regularMarketPrice"]

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    
    else:
        return render_template('update.html', ticker=ticker)

#charting using Plotly
@app.route('/chart/<int:id>', methods=['GET','POST'])
def chart(id):
    ticker = Stock.query.get_or_404(id)
    data = yfinance.download(tickers=ticker.content,period='max')
    data.to_csv(f"{ticker}.csv")
    reader = PD.read_csv(f"{ticker}.csv")

    fig = px.line(reader, x = 'Date', y = 'Close', title=f'{ticker.content} Share Prices')
    fig.show()
    return redirect('/')

#debugger mode
if __name__ == "__main__":
    app.run(debug=True)
