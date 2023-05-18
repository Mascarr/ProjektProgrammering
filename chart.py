# https://www.youtube.com/watch?v=KdoGekqz2hg, Hjälpte mig enormt 
import matplotlib.pyplot as plt
from binance.client import Client
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import threading 

api_key = ''
api_secret = ''


plt.style.use('bmh') 

client = Client(api_key, api_secret)


asset = "BTCUSDT"
asset_options = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT", "XRPUSDT"]    
trading_fee = 0.0001  # 0.01% trading fee



def getminutedata(symbol, interval, lookback): 
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume'] 
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


df = getminutedata(asset, '1m', '120m')


portfolio = {
        'cash': 1000.0,  # USD
        'asset': 0.0,  # BTC
        'initial_deposit': 1000.0,  # Initial deposit (USD)
        'total_investment': 1000.0,  # Totala Investering (USD)
    }

# Eric, Leo Hjälpte mig
def buy(symbol, quantity, price):
    cost = quantity * price
    fee = cost * trading_fee
    actual_cost = cost + fee
    actual_quantity = cost / price  # Updaterar antalet baserad på den riktiga kostnaden
    if portfolio['cash'] >= actual_cost: 
        portfolio['cash'] -= actual_cost
        portfolio['asset'] += actual_quantity
        portfolio['total_investment'] += cost
        messagebox.showinfo("Buy", f"Successfully bought {actual_quantity:.8f} {symbol}")
    else:   
        messagebox.showerror("Error", "Insufficient balance.")
 


def sell(symbol, quantity, price):
    proceeds = quantity * price
    tolerance = 1e-8

    if portfolio['asset'] - quantity >= -tolerance:
        portfolio['cash'] += proceeds
        portfolio['asset'] -= quantity
        messagebox.showinfo("Sell", f"Successfully sold {quantity:.8f} {symbol}")
    else:
        messagebox.showerror("Error", "Insufficient balance.")
   
        
def deposit(amount):
    portfolio['cash'] += amount
    portfolio['initial_deposit'] += amount
    
def get_profit_loss():
    # Få in senaste Data IRL
    latest_data = getminutedata(asset, '1m', '1m')
    last_price = latest_data['Close'].iloc[-1]
    return (portfolio['cash'] + portfolio['asset'] * last_price) - portfolio['initial_deposit'] # Hjälp av Leo

def create_gui():
    def update_labels(): 
        cash_balance_label.config(text=f"Cash Balance: {portfolio['cash']:.2f} USD")
        asset_balance_label.config(text=f"Asset Balance: {portfolio['asset']:.8f} BTC")
        profit_loss = get_profit_loss()
        profit_loss_label.config(text=f"Profit/Loss: {profit_loss:.2f} USD")
        last_price = df['Close'].iloc[-1]
        current_price_label.config(text=f"Current Price: {last_price:.2f} USD")
        root.after(1000, update_labels)


    def deposit_money():
        try:
            amount = float(deposit_entry.get()) 
            if amount > 0:
                deposit(amount)
                messagebox.showinfo("Deposit", f"Successfully deposited {amount:.2f} USD")
                deposit_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Invalid input.Please enter a positive number.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid number.")

    def on_click(action): 
        try:
            quantity =float(asset_entry.get())
            if quantity > 0:
                last_price = df['Close'].iloc[-1]

                if action == "buy":
                    buy(asset, quantity, last_price)
                elif action == "sell":
                    sell(asset, quantity, last_price)
            else:
                messagebox.showerror("Error", "Invalid input. Please enter a positive number.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
    

    root = tk.Tk()
    root.title("Tradelize Order")

    #ChatGPT Hjälpte, gör sidan responsiv, (anpasar sig efter storlek)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(column=0, row=0, sticky=(tk.W,   tk.E, tk.N, tk.S))

    for i in range(3):
        main_frame.columnconfigure(i, weight=1)

    for i in range(10):
        main_frame.rowconfigure(i, weight=1)
    #-------

    total_balance_label = tk.Label(main_frame, text="", font=("TkDefaultFont", 10, "bold"))
    total_balance_label.grid(column=0, row=4, columnspan=3, sticky=(tk.W, tk.E))

    cash_balance_label = tk.Label(main_frame, text="")
    cash_balance_label.grid(column=0, row=0, columnspan=3, sticky=(tk.W, tk.E))

   
    profit_loss_label = tk.Label(main_frame, text="", font=("TkDefaultFont", 10, "bold"))
    profit_loss_label.grid(column=0, row=2, columnspan=3, sticky=(tk.W, tk.E))

    current_price_label = tk.Label(main_frame, text="", font=("TkDefaultFont", 10, "bold"))
    current_price_label.grid(column=0, row=3, columnspan=3, sticky=(tk.W, tk.E))

    deposit_label = ttk.Label(main_frame, text="Deposit:")
    deposit_label.grid(column=0, row=4, sticky=(tk.W, tk.E))

    deposit_entry = ttk.Entry(main_frame)
    deposit_entry.grid(column=1, row=4, sticky=(tk.W, tk.E))

    asset_balance_label = tk.Label(main_frame, text="")
    asset_balance_label.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E))


    deposit_button = ttk.Button(main_frame, text="Deposit", command=deposit_money)
    deposit_button.grid(column=2, row=4, sticky=(tk.W, tk.E))

    asset_label = ttk.Label(main_frame, text="Enter amount of asset:")
    asset_label.grid(column=0, row=5, sticky=(tk.W, tk.E))

    asset_entry = ttk.Entry(main_frame)
    asset_entry.grid(column=1, row=5, sticky=(tk.W, tk.E))
    
    asset_var = tk.StringVar()
    asset_var.set(asset)

    asset_combobox = ttk.Combobox(main_frame, textvariable=asset_var, values=asset_options)
    asset_combobox.grid(column=1, row=7, sticky=(tk.W, tk.E))

    buy_button = ttk.Button(main_frame, text="Buy", command=lambda: on_click("buy"))
    buy_button.grid(column=2, row=5, sticky=(tk.W, tk.E))

    sell_button = ttk.Button(main_frame, text="Sell", command=lambda: on_click("sell"))
    sell_button.grid(column=2, row=6, sticky=(tk.W, tk.E))


    #ChatGPT
    def on_asset_selected(event):
        global asset, df
        asset = asset_var.get()
        df = getminutedata(asset, '1m', '120m')
        update_labels()

    asset_combobox.bind("<<ComboboxSelected>>", on_asset_selected)
    

    update_labels()
    root.mainloop()

def run_plot():
    plt.ion()
    while True:
        update_plot()
        plt.pause(10) 

def update_plot(): 
    data = getminutedata(asset, '1m', '120m')
    plt.cla()
    plt.plot(data.index, data['Close'])
    plt.xlabel('time')
    plt.ylabel('price')
    plt.title(asset)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.draw()


def main(): 
    gui_thread = threading.Thread(target=create_gui)
    plot_thread = threading.Thread(target=run_plot)

    gui_thread.start()
    plot_thread.start()

    gui_thread.join()
    plot_thread.join()

if __name__ == "__main__":
    main()

