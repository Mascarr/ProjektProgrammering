import PySimpleGUI as sg
import re
import json
import string 
import time
import random
import subprocess 
import sys 




def generate_temp_password(): 
    length=4
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choice(characters) for _ in range(length)) 


def load_users(filename, email=None): #Hjälp via Discord 
    try:
        with open(filename, "r") as f: 
            users = json.load(f) 
            if email is not None:  
                return users.get(email, {})
            return users    
    except FileNotFoundError:
        return {}


def save_users(users, filename):    
    with open(filename, "w") as f:
        json.dump(users, f, indent=4) # Hjälp via Discord


def is_already_in_use(users, email, username): 
    for user_info in users.values():
        if user_info["email"] == email:
            return "Email"
        if user_info["username"] == username:
            return "Username"
    return False

# Fake Stimulation
def is_valid_email(email):
    if len(email) > 5:
        if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) != None: # ChatGPT 
            return True
    return False

# Fake Stimulation
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True

# Hjälp Via discord
def verify_user(users, email, password):    
    for user_info in users.values():
        if user_info["email"] == email: 
            if user_info["password"] == password:
                 return email #process_login
            elif "temp_password" in user_info and user_info["temp_password"] == password and time.time() < user_info["temp_password_expiration"]: # ChatGPT
                return email
            else:
                return "Incorrect password"
    return "Invalid email and password"

# Hjälp via discord
def process_login(values):  
    email = values["email"]
    password = values["password"]

    users = load_users("users.json")  # Load.users funktion
    result = verify_user(users, email, password) #verify_user funktion
    
    
    if isinstance(result, str) and "Invalid" not in result and "Incorrect" not in result: #
        sg.popup("Login successful!")
        # Close the login window and open the chart.py script
        window.close()
        subprocess.Popen([sys.executable, "chart.py"])  # ChatGPT 
    else:
        sg.popup(result)


# Register layout
def get_register_layout():
    register_layout = [
        [sg.Text("Email")],
        [sg.Input(key="email")],
        [sg.Text("Username")],
        [sg.Input(key="new_username")],
        [sg.Text("Password")],
        [sg.Input(key="new_password", password_char="*", enable_events=True)], 
        [sg.Text("Confirm password")],
        [sg.Input(key="confirm_password", password_char="*")],
        [sg.Checkbox("Show Password", key="show_password", enable_events=True)], 
        [sg.Button("Register"), sg.Button("Back")]
    ]
    return register_layout

# Login layout
login_layout = [
    [sg.Text("Email")],
    [sg.Input(key="email")],    
    [sg.Text("Password")],
    [sg.Input(key="password", password_char="*")],
    [sg.Checkbox("Show Password", key="show_password", enable_events=True)],
    [sg.Button("Log in"), sg.Button("Register account"), sg.Text("Forgot Password?", key="forgot_password", enable_events=True, text_color="blue", font=("Helvetica", 9, "underline"))]
]   


# Main window
window = sg.Window("Login", login_layout)
main_window_open = True 
while True:
    event, values = window.read() 
    if event == sg.WIN_CLOSED:
        main_window_open = False  
        break
    
    # Om Använder klickar "Log in"
    if event == "Log in":
        process_login(values) 

    # Om Använder klickar Register account"
    elif event == "Register account":
        window.hide()

        # Create a new register layout inside the loop
        register_window = sg.Window("Register account", get_register_layout())

        while True:
            register_event, register_values = register_window.read(timeout=100) 

            if register_event == sg.WIN_CLOSED or register_event == "Back":
                register_window.close()
                break

            # If the user clicks "Register"
            elif register_event == "Register":
                email = register_values["email"]
                new_username = register_values["new_username"]
                new_password = register_values["new_password"]
                confirm_password = register_values["confirm_password"]

                users = load_users("users.json")  # Laddar existerande användare

                
                in_use = is_already_in_use(users, email, new_username)  # kollar om email eller username amvänds redan
                if in_use:
                    sg.popup(f"{in_use} is already in use.")
                elif not is_valid_email(email):
                    sg.popup("Invalid email address")
                elif not is_valid_password(new_password):
                    sg.popup("The password must be at least 8 characters long and contain both letters and numbers.")
                elif new_password != confirm_password:
                    sg.popup("Passwords do not match")
                else:
                    # Save the new user
                    users[email] = {"email": email, "username": new_username, "password": new_password}
                    save_users(users, "users.json")
                    sg.popup("Registration successful!")

            # Show/Hide password toggle
            elif register_event == "show_password":
                register_window["confirm_password"].update(password_char="" if register_values["show_password"] else "*")
                register_window["new_password"].update(password_char="" if register_values["show_password"] else "*")

                    
        # Gå tillbaka till login window efter ha stängt register window
        if main_window_open:  # kollar om  main window är fortfarande öpen innan den "un-hidinar" den
            window.un_hide()

    # Visa/Göm lösenord toggle
    if event == "show_password":
        window["password"].update(password_char="" if values["show_password"] else "*") 

    # Glömt lösenord  funktionalitet
    elif event == "forgot_password":
        email = sg.popup_get_text("Enter your email address:")
        if email is not None:
            users = load_users("users.json")
            found_email = False
            for user_info in users.values():
                if user_info["email"] == email:
                    found_email = True
                    # Skapar en random temporär lösenord och expiration time (5 minutes)
                    temp_password = generate_temp_password()
                    expiration_time = time.time() + 5 * 60   # Minuter
                    user_info["temp_password"] = temp_password
                    user_info["temp_password_expiration"] = expiration_time
                    save_users(users, "users.json")
                    # Show the temporary passwordin a popup
                    sg.popup(f"Temporary password: {temp_password}\nThis password will be valid for 5 minutes.")
                    break
            if not found_email:
                sg.popup("Email address not found.")

window.close()