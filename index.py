from flask import Flask, request
from scraper import * # Web Scraping utility functions for Online Clubs with Penn.
app = Flask(__name__)

@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return "Welcome to the Penn Club Review API!."

if __name__ == '__main__':
    app.run()
