"""
views.py

"""

import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app
from app.database import *

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
DATABASE = Database() # define a database to hold transactions

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
    """
    Driver function for submit method. Handles the transaction and then posts it to the blockchain.
    
    """
    # Get info from html form
    amount = request.form["amount"]
    sell_fruit = request.form["sell_fruit"]
    author = request.form["author"]
    desired_fruit = request.form["desired_fruit"]

    # error checking
    vars_list = [amount,sell_fruit,author,desired_fruit]
    results = error_check(vars_list)
    print("Line 70: " + results)
    # check that there are enough funds to complete the transaction
    
    
    # if there are enough funds, complete the transaction and post it to the blockchain.
    if(results == "NO ERRORS"):
        results = "The transaction was successful."
        submit_textarea(sell_fruit,amount,author, desired_fruit, results)
        
        #user sell_fruit goes to bank
        edit_database(sell_fruit,amount,author,"SOLD")
        edit_database(sell_fruit,amount,"bank","BOUGHT")

        #bank desired_fruit goes to user
        edit_database(desired_fruit,amount,author,"BOUGHT")
        edit_database(desired_fruit,amount,"bank","SOLD")
        
        print(DATABASE)
    
    # if there aren't enough funds, post the transaction, but do not move fruits.
    elif(results == "Transaction Cancelled. All fields must be filled in."):
        submit_textarea("NaN","NaN","NaN","NaN",results)
    else:
        submit_textarea(sell_fruit, amount, author, desired_fruit, results)

    return redirect('/')

def error_check(vars_list):
    
    fruit_list = DATABASE.get_all_companies()
    # check that all boxes have value
    for var in vars_list:
        if var == "":
            return "Transaction Cancelled. All fields must be filled in."
    # check that author is a valid author
    if(vars_list[2] not in DATABASE.get_users()):
        return "Transaction Cancelled. Invalid Author."
    #check that fruits are valid fruits
    elif(vars_list[1] not in fruit_list or vars_list[3] not in fruit_list):
        return "Transaction Cancelled. Valid fruits are 'apples', 'bananas', or 'oranges'."
    #check that amount is a number
    elif(type(vars_list[0] != int)):
        return "Transaction Cancelled. Please enter a valid integer amount."
    
    # check for valid funds
    funds_avaliable = check_for_funds(vars_list[1],vars_list[0],vars_list[2])
    if(funds_avaliable == False):
        return "Transaction Cancelled. Not enough funds."
    return "NO ERRORS"

def edit_database(sell_fruit,amount,author,transaction):
    """Edit the database, either adding or removing fruit from the specified "author" """
    DATABASE.edit_wallet(sell_fruit,int(amount),author,transaction)
    return 0

def check_for_funds(sell_fruit,amount,author):
    """checks to ensure user has enough fruit for transaction to take place"""
    
    if(DATABASE.get_fund(author,sell_fruit) >= int(amount)):
        return True
    else:
        return False

def submit_textarea(sell_fruit,amount,author,desired_fruit,msg):
    """
    Endpoint to create a new transaction via our application.
    """

    # create json object
    post_object = {
        
        'sell_fruit' : sell_fruit,
        'amount': amount,
        'author': author,
        'desired_fruit': desired_fruit,
        'results': msg,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-sell_fruit': 'application/json'})

    return 0


def timestamp_to_string(epoch_time):
    """Convert timestamp to a string"""
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
