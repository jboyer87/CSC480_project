#!/usr/bin/env python

import os
import json

from flask import Flask, render_template, Response, redirect, url_for, request, session, flash

import db
import Chore
import Helpers
from Log import _log

app = Flask(__name__)

# set some globals
VERBOSITY = 1
DB_CONN = db.CONN


# The actual website endpoints

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')


@app.route('/chores', methods=['GET', 'POST'])
def chores():
    chores_dict = {'Take out trash': 1,  # build a fake chore dict
                   'Take out recycling': 1, 
                   'Clean kitty litter': 2, 
                   'Clean chicken coop': 3, 
                   'Clean playroom': 1, 
                   'Wash dishes': 2, 
                   'Clean your room': 1, 
                   'Clean bathroom': 3, 
                   'Vacuum': 1}
    return render_template('chores.html', data=chores_dict)


@app.route('/new_chore', methods=['GET'])
def new_chore():
    return render_template('new_chore.html')


@app.route('/new_chore_results', methods=['GET', 'POST'])
def new_chore_results():
    # general processing of the form we've received
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    _log(1, VERBOSITY, res)
    processed_res, missing = Helpers._process_chore_form(res)  # process the form results and validate
    _log(6, VERBOSITY, missing)
    if len(missing) > 0:
        return render_template('error.html', data=missing)

    # build a chore object, populate it, and stick it in the db
    this_chore = Chore.Chore(processed_res)
    db.write_chore_to_storage(DB_CONN, this_chore)

    # proceed to the results page
    order_list = ['name', 'desc', 'assigned_to', 'points', 'due']
    return render_template('new_chore_results.html', order=order_list, data=res)


@app.route('/available', methods=['GET'])
def available():
    chores_list = db.get_available_chores(DB_CONN)  # get chores from db (currently a list of json files)
    chores_dict = {}
    for chore in chores_list:  # build a large dict with all of the info in it
        status, this_chore = db._read_from_storage(DB_CONN, chore)
        chores_dict[chore] = this_chore
    order_list = [k for k in chores_dict]  # get keys(chore names)
    order_list.sort()  # sort the name list, can change sort type
    return render_template('available.html', order=order_list, data=chores_dict)


@app.route('/my_account', methods=['GET'])
def my_account():
    return render_template('my_account.html')


@app.route('/new_account', methods=['GET'])
def new_account():
    return render_template('new_account.html')


@app.route('/new_account_results', methods=['GET', 'POST'])
def new_account_results():
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    return render_template('new_account_results.html')


@app.route('/new_reward', methods=['GET'])
def new_reward():
    return render_template('new_reward.html')


@app.route('/new_reward_results', methods=['GET', 'POST'])
def new_reward_results():
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    return render_template('new_reward_results.html')


@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


