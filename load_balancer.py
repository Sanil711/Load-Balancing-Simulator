from flask import Flask, render_template_string, redirect, url_for
import requests
import random

app = Flask(__name__)

# Load balancer state
workers = ['http://127.0.0.1:5001', 'http://127.0.0.1:5002', 'http://127.0.0.1:5003']
current_worker = 0
request_count = 0
history = []  # To store last few requests
load_balancing_mode = 'round_robin'  # or 'random'

@app.route('/')
def home():
    return redirect(url_for('handle_request'))

@app.route('/toggle')
def toggle_mode():
    global load_balancing_mode
    load_balancing_mode = 'random' if load_balancing_mode == 'round_robin' else 'round_robin'
    return redirect(url_for('handle_request'))

@app.route('/request')
def handle_request():
    global current_worker, request_count, history, load_balancing_mode

    # Choose worker based on mode
    if load_balancing_mode == 'round_robin':
        worker_url = workers[current_worker]
        current_worker = (current_worker + 1) % len(workers)
    else:
        worker_url = random.choice(workers)

    request_count += 1

    try:
        response = requests.get(f"{worker_url}/process")
        message = response.json()['message']
    except Exception as e:
        message = f"Worker not available: {e}"

    full_message = f"Request {request_count}: {message} ({load_balancing_mode.replace('_', ' ').title()})"

    # Save to history (keep only last 10 entries)
    history.insert(0, full_message)
    if len(history) > 10:
        history.pop()

    history_html = "<br>".join(history)

    html = f"""
    <html>
        <head>
            <title>Load Balancer</title>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    background-color: #121212;
                    color: #eeeeee;
                    text-align: center;
                    padding-top: 50px;
                }}
                .box {{
                    background-color: #1e1e1e;
                    display: inline-block;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.4);
                    width: 550px;
                }}
                .message {{
                    font-size: 24px;
                    color: #fff;
                    margin-bottom: 20px;
                }}
                .history {{
                    margin-top: 30px;
                    text-align: left;
                    font-size: 16px;
                    color: #aaaaaa;
                    max-height: 300px;
                    overflow-y: auto;
                }}
                .button {{
                    background-color: #4CAF50;
                    color: black;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    margin: 5px;
                }}
                .button:hover {{
                    background-color: #45a049;
                }}
                .mode {{
                    margin-bottom: 15px;
                    font-size: 18px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="box">
                <div class="mode">Mode: <strong>{load_balancing_mode.replace('_', ' ').title()}</strong></div>
                <div class="message">{full_message}</div>
                <form method="get" action="/request">
                    <button class="button" type="submit">Send Next Request</button>
                </form>
                <form method="get" action="/toggle">
                    <button class="button" type="submit">Switch Mode</button>
                </form>
                <div class="history">
                    <strong>Recent History:</strong><br>
                    {history_html}
                </div>
            </div>
        </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(port=5000)
