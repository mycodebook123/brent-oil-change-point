from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

def load_prices():
    df = pd.read_csv(os.path.join(DATA_DIR, 'processed_brent_prices.csv'))
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def load_events():
    df = pd.read_csv(os.path.join(DATA_DIR, 'events.csv'))
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def load_change_point():
    with open(os.path.join(DATA_DIR, 'change_point_results.json')) as f:
        return json.load(f)


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/prices')
def prices():
    df = load_prices()

    start = request.args.get('start')
    end = request.args.get('end')
    granularity = request.args.get('granularity', 'monthly')

    if start:
        df = df[df['Date'] >= pd.to_datetime(start)]
    if end:
        df = df[df['Date'] <= pd.to_datetime(end)]

    if granularity == 'daily':
        out = df[['Date', 'Price']].copy()
    else:
        df = df.set_index('Date')
        out = df['Price'].resample('ME').mean().reset_index()

    out['Date'] = out['Date'].dt.strftime('%Y-%m-%d')
    return jsonify(out.to_dict(orient='records'))


@app.route('/api/events')
def events():
    df = load_events()
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return jsonify(df.to_dict(orient='records'))


@app.route('/api/change-points')
def change_points():
    result = load_change_point()
    return jsonify(result)


@app.route('/api/summary')
def summary():
    df = load_prices()
    return jsonify({
        'start_date': df['Date'].min().strftime('%Y-%m-%d'),
        'end_date': df['Date'].max().strftime('%Y-%m-%d'),
        'min_price': float(df['Price'].min()),
        'max_price': float(df['Price'].max()),
        'avg_price': float(df['Price'].mean()),
        'total_observations': len(df),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
