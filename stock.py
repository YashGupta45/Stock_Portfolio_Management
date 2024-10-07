import mysql.connector
import yfinance as yf
from datetime import datetime
from decimal import Decimal

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="********",
    database="stock_portfolio"
)

cursor = db_connection.cursor()

#Fetch the current stock price
def fetch_stock_price(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    stock_info = stock.history(period='1d')
    if not stock_info.empty:
        current_price = stock_info['Close'].iloc[0]
        return float(current_price)
    else:
        return None
    
    
#Calculate the profit or loss
def calculate_profit_loss(purchase_price, current_price, quantity):
    # Convert purchase_price and current_price to Decimal for precision
    purchase_price = Decimal(purchase_price)
    current_price = Decimal(current_price)
    return (current_price - purchase_price) * quantity


#Update the porfolio with current stock prices and get the details
def update_portfolio():
    cursor.execute("SELECT id, stock_symbol, purchase_price, quantity FROM Portfolio")
    portfolio = cursor.fetchall()

    for stock in portfolio:
        stock_id, stock_symbol, purchase_price, quantity = stock
        current_price = fetch_stock_price(stock_symbol) 

        if current_price is not None:
            profit_loss = calculate_profit_loss(purchase_price, current_price, quantity)

            # Calculate total invested and current value
            total_invested = Decimal(purchase_price) * Decimal(quantity)
            total_current_value = Decimal(current_price) * Decimal(quantity)

            cursor.execute(
                "UPDATE Portfolio SET current_price = %s, profit_loss = %s, total_invested = %s, total_current_value = %s WHERE id = %s",
                (current_price, profit_loss, total_invested, total_current_value, stock_id)
            )
            db_connection.commit()
            print(f"Updated {stock_symbol}: Current Price = {current_price}, Profit/Loss = {profit_loss}")


#Updating the details of the stocks sold
def sell_stock(stock_symbol):
    cursor.execute("SELECT id, purchase_price, quantity FROM Portfolio WHERE stock_symbol = %s", (stock_symbol,))
    stock = cursor.fetchone()

    if stock:
        stock_id, purchase_price, existing_quantity = stock

        sell_price = float(input(f"Enter the sell price for {stock_symbol}: "))
        quantity = int(input(f"Enter the quantity of {stock_symbol} to sell: "))

        if quantity <= existing_quantity:
            profit_loss = calculate_profit_loss(purchase_price, sell_price, quantity)
            sell_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                "INSERT INTO SoldStocks (stock_symbol, purchase_price, sell_price, quantity, profit_loss, sell_date) VALUES (%s, %s, %s, %s, %s, %s)",
                (stock_symbol, purchase_price, sell_price, quantity, profit_loss, sell_date)
            )
            db_connection.commit()

            new_quantity = existing_quantity - quantity
            if new_quantity > 0:
                cursor.execute(
                    "UPDATE Portfolio SET quantity = %s WHERE id = %s", (new_quantity, stock_id)
                )
            else:
                cursor.execute("DELETE FROM Portfolio WHERE id = %s", (stock_id,))
            db_connection.commit()

            print(f"Sold {quantity} of {stock_symbol} at {sell_price}. Profit/Loss: {profit_loss}")

        else:
            print("You don't have enough quantity to sell.")
    else:
        print(f"{stock_symbol} is not in the portfolio.")


#Add a new stock to portfolio
def add_stock_to_portfolio(stock_symbol, quantity, purchase_price):
    cursor.execute(
        "SELECT id, quantity, purchase_price FROM Portfolio WHERE stock_symbol = %s", (stock_symbol,)
    )
    existing_stock = cursor.fetchone()

    if existing_stock:
        stock_id, existing_quantity, old_purchase_price = existing_stock
        new_quantity = existing_quantity + quantity
        old_purchase_price = Decimal(old_purchase_price)
        purchase_price = Decimal(purchase_price)

        average_purchase_price = (old_purchase_price * existing_quantity + purchase_price * quantity) / new_quantity

        cursor.execute(
            "UPDATE Portfolio SET quantity = %s, purchase_price = %s WHERE id = %s",
            (new_quantity, average_purchase_price, stock_id)
        )
    else:
        cursor.execute(
            "INSERT INTO Portfolio (stock_symbol, quantity, purchase_price) VALUES (%s, %s, %s)",
            (stock_symbol, quantity, purchase_price)
        )
    db_connection.commit()
    print(f"Added {quantity} of {stock_symbol} at {purchase_price} to the portfolio.")


#Delete an existing stock which is wrongly entered
def delete_stock_from_portfolio(stock_symbol):
    cursor.execute("DELETE FROM Portfolio WHERE stock_symbol = %s", (stock_symbol,))
    db_connection.commit()
    print(f"Deleted {stock_symbol} from the portfolio.")


#Update the portfolio summary details
def update_portfolio_summary():
    cursor.execute("DELETE FROM PortfolioSummary")  # Clear existing values
    cursor.execute(
        "INSERT INTO PortfolioSummary (sold_p_l, total_invested, total_current_value, current_p_l)"
        "SELECT SUM(profit_loss),"
        "(SELECT SUM(total_invested) FROM Portfolio),"  
        "(SELECT SUM(total_current_value) FROM Portfolio),"
        "(SELECT SUM(total_current_value) - SUM(total_invested) from Portfolio)" 
        "FROM SoldStocks"
    )
    db_connection.commit()


def menu():
    while True:
        print("\nStock Portfolio Management")
        print("1. Add Stock")
        print("2. Sell Stock")
        print("3. Update Portfolio")
        print("4. Delete Stock")
        print("5. Update Portfolio Summary")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            stock_symbol = input("Enter stock symbol: ")
            quantity = int(input("Enter quantity: "))
            purchase_price = float(input("Enter purchase price: "))
            add_stock_to_portfolio(stock_symbol, quantity, purchase_price)

        elif choice == '2':
            stock_symbol = input("Enter stock symbol to sell: ")
            sell_stock(stock_symbol)

        elif choice == '3':
            update_portfolio()
            print("Portfolio Updated.")

        elif choice == '4':
            stock_symbol = input("Enter stock symbol to delete: ")
            delete_stock_from_portfolio(stock_symbol)

        elif choice == '5':
            update_portfolio_summary()
            print("Portfolio summary updated.")

        elif choice == '6':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please select again.")

def main():
    menu()

if __name__ == "__main__":
    main()

cursor.close()
db_connection.close()