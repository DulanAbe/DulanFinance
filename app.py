import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from operator import itemgetter

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get the users username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']

    # Get the relevant information from display table
    output = db.execute("SELECT symbol, amount FROM display WHERE user_id = ? ORDER BY shares_value DESC", session["user_id"])

    # Create an empty list of dictionaries
    data = []
    shares_value = 0
    # Collect the data from the SQLite output
    for dict_item in output:
        symbol = dict_item['symbol']
        amount = dict_item['amount']


        # Get the relevant information about the company from lookup
        company = lookup(symbol)
        # Create a new dict_item to pass into index
        item = {}
        item['symbol'] = symbol
        item['name'] = company['name']
        item['amount'] = amount
        item['price'] = usd(company['price'])
        item['total'] = usd(company['price'] * amount)
        shares_value = shares_value + company['price'] * amount
        data.append(item)

    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    cash_display = usd(cash)
    net_worth = usd(cash + shares_value)


    return render_template("index.html", username = username, data = data, cash = cash_display, net_worth = net_worth)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
        if not lookup(request.form.get("symbol")):
            return apology("Company Not Found")
        else:
            # buy the stock for the user
            company = lookup(request.form.get("symbol"))
            # fill up the purchases table
            user_id = session["user_id"]
            symbol = company["symbol"]
            amount = int(request.form.get("number"))
            price = company["price"]
            # calculate the value of the transaction
            shares_value = price * amount
            # need to calculate balance
            # find the initial amount of money
            current_balance = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
            cost = float(amount) * price
            new_balance = current_balance - cost
            if new_balance < 0:
                return apology("You cannot afford this transaction")
            # update the database
            # insert into the purchases table
            db.execute("INSERT INTO purchases (users_id, symbol, amount, timestamp, price, balance, type) VALUES (?, ?, ?, datetime('now'), ?, ?, ?)", user_id, symbol, amount, price, new_balance, "buy")
            # update users table
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)
            # update index table
            # if the user already owns share of this stock
            owns_stock = db.execute("SELECT * FROM display WHERE user_id = ? and symbol = ?", user_id, symbol)
            if not owns_stock:
                # make a new entry in the table;
                db.execute("INSERT INTO display (user_id, symbol, amount, shares_value) VALUES (?, ?, ?, ?)", user_id, symbol, amount, shares_value)
            else:
                # otherwise modify the existing entry
                # find initial amount
                initial_amount = db.execute("SELECT amount FROM display WHERE user_id = ? and symbol = ?", user_id, symbol)[0]['amount']
                # calculate new amount
                new_amount = initial_amount + amount
                # calculate new value
                # find initial value
                initial_value = db.execute("SELECT shares_value FROM display WHERE user_id = ? and symbol = ?", user_id, symbol)[0]['shares_value']
                new_value = initial_value + value
                db.execute("UPDATE display SET amount = ?, shares_value = ? WHERE user_id = ? and symbol = ?", new_amount, shares_value, user_id, symbol)
            # Caclulate value
            return render_template("bought.html", symbol = symbol, amount = amount, price = usd(price), cost = usd(cost), balance = usd(new_balance))






@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username or password. Usernames are also case sensitive", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        stock = request.form.get("stock")
        company = lookup(stock)
        if not company:
            return apology("Stock not Found")
        name = company["name"]
        symbol = company["symbol"]
        price = company["price"]
        return render_template("quoted.html", name = company["name"], symbol = company["symbol"], price = company["price"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        if not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        # Ensure username not already in use
        # Do a SQL query to look for the username:
        username_exists = db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))
        # If the username is already there return an error
        if username_exists:
            return apology("username already in use")

        # Register the user
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password)
        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        """Sell shares of stock"""
        # Get all of the shares the user owns to fill up the sell table
        output = db.execute("SELECT symbol FROM display WHERE user_id = ?", session['user_id'])
        symbols = []
        for dict_item in output:
            symbols.append(dict_item['symbol'])
        return render_template("sell.html", symbols = symbols)
    else:
        # Access the information
        symbol = request.form.get("company")
        amount = request.form.get("amount")
        # Error Check
        # Check the amount is a number:
        if not amount.isdigit():
            return apology("Please enter a number as digits")
        # Convert amount into an integer
        amount = int(amount)
        # Get amount owned
        amount_owned = db.execute("SELECT amount FROM display WHERE user_id = ? AND symbol = ?", session['user_id'], symbol)[0]['amount']



        if amount > amount_owned:
            return apology("You are attempting to sell more shares than you own")
        
        # get share value
        price = lookup(symbol)['price']

        # get transaction value
        transaction_value = price * amount

        # get current balance
        current_balance = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])[0]['cash']
        new_balance = current_balance + transaction_value
        
        if amount == amount_owned:
            # Delete the records from the tables
            db.execute("DELETE FROM display WHERE user_id = ? AND symbol = ?", session['user_id'], symbol)
            # Do the rest of the steps

            # enter all the values into the purchases table
            db.execute("INSERT INTO purchases (users_id, symbol, amount, timestamp, price, balance, type) VALUES (?, ?, ?, datetime('now'), ?, ?, ?)", session['user_id'], symbol, amount, price, new_balance, "sell")
            # Update users
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, session['user_id'])

        else: 
            # enter all the values into the purchases table
            db.execute("INSERT INTO purchases (users_id, symbol, amount, timestamp, price, balance, type) VALUES (?, ?, ?, datetime('now'), ?, ?, ?)", session['user_id'], symbol, amount, price, new_balance, "sell")

            # Update users
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, session['user_id'])

            # Update display
            # Calculate the new amount
            # Get the current amount
            current_amount = db.execute("SELECT amount FROM display WHERE user_id = ? AND symbol = ?", session['user_id'], symbol)[0]['amount']
            new_amount = current_amount - amount

            # Calculate the new shares_value
            # Get the old shares value
            current_shares_value = db.execute("SELECT shares_value FROM display WHERE user_id = ? AND symbol = ?", session['user_id'], symbol)[0]['shares_value']
            new_shares_value = current_shares_value - transaction_value
            db.execute("UPDATE display SET amount = ?, shares_value = ? WHERE user_id = ? AND symbol = ?", new_amount, new_shares_value, session['user_id'], symbol)
        return redirect("/")

@app.route("/leaderboard")
@login_required
def leaderboard():
    # Fill up the leaderboard table
    # Get the username, shares_value from display, and order it right now. 
    output = db.execute("SELECT id FROM users")
    # For every id, run the display query; 
    ids = []
    leaderboard = []
    for dict_item in output:
        ids.append(dict_item['id'])
    for id in ids:
        # Get their display table 
        display_table = db.execute("SELECT * FROM display WHERE user_id = ? ORDER BY shares_value DESC", id)
        net_worth = 0
        most_used_shares = []
        for i in range(len(display_table)):
            net_worth += display_table[i]['shares_value']
            if i < 3:
                most_used_shares.append(display_table[i]['symbol'])
            # Calculate their net worth and get their most used shares
        # Also get username from here
        users_output = db.execute("SELECT cash, username FROM users WHERE id = ?", id)
        net_worth += users_output[0]['cash']
        username = users_output[0]['username']
        # Convert the list of most used shares into a string
        string = ", ".join(most_used_shares)
        # Now just add all of the information into the dictionary
        display_dict_item = {}
        display_dict_item['username'] = username
        display_dict_item['net_worth'] = net_worth
        display_dict_item['most_used_shares'] = string 
        leaderboard.append(display_dict_item)

    # Sort the dictionary, then pass it into leaderboard
    sorted_leaderboard = sorted(leaderboard, key=itemgetter('net_worth'), reverse=True)
    # add variable to represent position
    for i in range(len(sorted_leaderboard)):
        sorted_leaderboard[i]["position"] = i+1
        sorted_leaderboard[i]['net_worth'] = usd(sorted_leaderboard[i]['net_worth'])
    print(sorted_leaderboard)

    return render_template("leaderboard.html", leaderboard = sorted_leaderboard)




