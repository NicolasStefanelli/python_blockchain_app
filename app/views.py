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
                           title='FruitNet: Decentralized '
                                 'fruit trading',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit():
    amount = request.form["amount"]
    sell_fruit = request.form["sell_fruit"]
    author = request.form["author"]
    desired_fruit = request.form["desired_fruit"]

    funds_avaliable = check_for_funds(sell_fruit,amount,author)
    
    if(funds_avaliable == True):
        submit_textarea(sell_fruit,amount,author,desired_fruit)
        
        #user sell_fruit goes to bank
        edit_database(sell_fruit,amount,author,"SOLD")
        edit_database(sell_fruit,amount,"bank","BOUGHT")

        #bank desired_fruit goes to user
        edit_database(desired_fruit,amount,author,"BOUGHT")
        edit_database(desired_fruit,amount,"bank","SOLD")
        
        print(DATABASE)

    else:

        print("Transaction Cancelled. Not Enough Funds")
        results = "This transaction was not successful. Please try again."


    return redirect('/')


def edit_database(sell_fruit,amount,author,transaction):
    DATABASE.edit_wallet(sell_fruit,int(amount),author,transaction)
    return 0

def check_for_funds(sell_fruit,amount,author):
    
    if(DATABASE.get_fund(author,sell_fruit) >= int(amount)):
        print("Successful Check")
        return True
    else:
        print("Not Enough Funds")
        return False

def submit_textarea(sell_fruit,amount,author,desired_fruit):
    """
    Endpoint to create a new transaction via our application.
    """

    post_object = {
        
        'sell_fruit' : sell_fruit,
        'amount': amount,
        'author': author,
        'desired_fruit': desired_fruit,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-sell_fruit': 'application/json'})

    print("new transaction created")
    return 0


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
