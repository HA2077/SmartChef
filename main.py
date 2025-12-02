from backend.user import load_users

def main():
    users = load_users("data/users.json")
    if not users:
        print("No users found. Please create users first.")
        return

    # Attempt to log in as the admin user
    username = "admin"
    password = "1234"

    loggedInUser = None
    for user in users:
        if user.login(username, password):
            loggedInUser = user
            break
            
    if loggedInUser:
        print(f"Login successful! Welcome, {loggedInUser.username} ({loggedInUser.role}).")
    else:
        print("Login failed. Invalid username or password.")

if __name__ == "__main__":
    main()
