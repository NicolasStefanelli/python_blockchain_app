import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app
from database import *

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
DATABASE = Database()

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit():
    amount = request.form["amount"]
    type = request.form["type"]
    author = request.form["author"]
    transaction = request.form["transaction"]

    funds_avaliable = True
    if(request.form["transaction"] == "SOLD"):
        funds_avaliable = check_for_funds(type,amount,author)
    
    if(funds_avaliable == True):
        submit_textarea(type,amount,author,transaction)
        edit_database(type,amount,author,transaction)
        edit_database(type,amount,"bank",opposite_transaction(transaction))
        # print(DATABASE)
    else:
        print("Transaction Cancelled. Not Enough Funds")


    return redirect('/')

def opposite_transaction(transaction):
    if(transaction == "SOLD"):
        return "BOUGHT"
    else:
        return "SOLD"

def edit_database(type,amount,author,transaction):
    DATABASE.edit_wallet(type,int(amount),author,transaction)
    return 0

def check_for_funds(type,amount,author):

    """
    post_object = {
        
        'type' : type,
        'amount': amount,
        'author': author,
    }
    new_tx_address = "{}/fund_check".format(DATABASE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    """
    
    if(DATABASE.get_fund(author,type) >= int(amount)):
        print("Successful Check")
        return True
    else:
        print("Not Enough Funds")
        return False

def submit_textarea(type,amount,author,transaction):
    """
    Endpoint to create a new transaction via our application.
    """

    post_object = {
        
        'type' : type,
        'amount': amount,
        'author': author,
        'transaction': transaction,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    print("new transaction created")
    return 0


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
