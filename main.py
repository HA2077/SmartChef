from backend.user import load_users

def main():
    users = load_users("data/users.json")
    if not users:
        print("No users found. Please create users first.")
        return

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    loggedInUser = None
    for user in users:
        if user.login(username, password):
            loggedInUser = user
            break
            
    if loggedInUser:
        print(f"Login successful! Welcome, {loggedInUser.getusername()} ({loggedInUser.getrole()}).")
    else:
        print("Login failed. Invalid username or password.")

if __name__ == "__main__":
    main()