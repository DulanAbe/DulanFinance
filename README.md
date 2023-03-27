# DulanFinance


<img width="1512" alt="Screenshot 2023-03-07 at 00 36 14" src="https://user-images.githubusercontent.com/59977585/223288589-c6bfa8ef-93f4-4a3a-820d-cb570427deef.png">


## Summary
DulanFinance is a web app that allows logged-in users to "buy" and "sell" stocks (with virtual money) as well as look up real stock quotes fetched from IEX API. Users can also view their stock portfolio transaction history. This is based off PSET8 from Harvard's CS50 Course. 

## Technologies
* Python
* Flask 
* SQLite
* HTML
* Bootstrap


## How to Run
Please visit [this link](dulanabe.pythonanywhere.com). 
The website is hosted on pythonanywhere, so feel free to try out any of the features for yourself. 

## Views

### Register
Allow a new user to register for an account, rendering an apology view if the form data is incomplete or if the username already exists in the database.
Passwords are securely encrypted using hashing from werkzeug security module. 

<img width="1512" alt="Screenshot 2023-03-27 at 23 17 00" src="https://user-images.githubusercontent.com/59977585/228079315-a085373d-76fd-4c0f-a3c6-f8cb955a95f2.png">

### Login 
Allows a user to login with username and password. 

### Index
The homepage displays a table of the logged-in user's owned stocks, number of shares, current stock price, value of each holding. This view also shows the user's cash balance and the total of their cash plus stock value. (Shown in Screenshot at the top)

### Quote
Allows the user to submit a form to look up a stock's current price, retrieving real-time data from the IEX API. An error message is rendered if the stock symbol is invalid.

### Buy
Allows the user to "buy" stocks by submitting a form with the stock's symbol and number of shares. Checks to ensure the stock symbol is valid and the user can afford the purchase at the stock's current market price with their available balance, and stores the transaction history in the database.
<img width="1512" alt="Screenshot 2023-03-27 at 23 15 31" src="https://user-images.githubusercontent.com/59977585/228079392-979d6e48-cd27-449b-8cde-9c2793ab4ae7.png">


### Sell
Allows the user to "sell" shares of any stock currently owned in their portfolio. 

<img width="1512" alt="Screenshot 2023-03-27 at 23 15 39" src="https://user-images.githubusercontent.com/59977585/228079409-797b89f7-f0bc-4220-ac23-33614e4d866a.png">

### Leaderboard
Displays a table showing the total balance of all other users (calculated in real time), and their most invested in companies. 
<img width="1512" alt="Screenshot 2023-03-27 at 23 15 19" src="https://user-images.githubusercontent.com/59977585/228079193-e656cc69-aa8d-4305-ab29-931c44b04ffd.png">


### Delete Account
Enables the user to delete their accounts. Removes all records assosciated with the user from the SQLite databse

---

Please note that the **Login** and **Logout** functions and all functions in **helpers.py** came with the assignment starter code and are not my work. Starter code &copy;2020 David J. Malan/ Harvard
