from backend.user import load_users

users = load_users("data/users.json")
if not users:
    print("No users found. Please create users first.")
    exit()

username = input("Enter your username: ")
password = input("Enter your password: ")

loggedInUser = None
for user in users:
    if user.login(username, password):
        loggedInUser = user
        break
            
if loggedInUser:
    print(f"Login successful! Welcome, {loggedInUser.get_username()} ({loggedInUser.get_role()}).")
else:
    print("Login failed. Invalid username or password.")