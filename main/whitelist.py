import json
import os
import subprocess
from datetime import datetime

class WhitelistManager:
    def __init__(self, whitelist_file="whitelist_users.json", output_file="whitelist.json"):
        self.whitelist_file = whitelist_file
        self.output_file = output_file
        self.whitelist = self.load_whitelist()

    def load_whitelist(self):
        if os.path.exists(self.whitelist_file):
            with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_whitelist(self):
        with open(self.whitelist_file, 'w', encoding='utf-8') as f:
            json.dump(self.whitelist, f, indent=2, ensure_ascii=False)
        self.save_public_whitelist()

    def save_public_whitelist(self):
        usernames = [data["username"] for data in self.whitelist.values()]
        public_data = {
            "users": usernames,
            "last_updated": datetime.now().isoformat(),
            "count": len(usernames)
        }
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(public_data, f, indent=2)

    def push_to_github(self, message):
        try:
            subprocess.run(["git", "add", self.output_file], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
            result = subprocess.run(["git", "push"], check=True, capture_output=True, text=True)
            print("Pushed to GitHub successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print("Git push failed: " + e.stderr.strip() if e.stderr else "Git push failed.")
            return False

    def add_user(self, username):
        username_lower = username.lower()

        if username_lower in self.whitelist:
            print(f"{username} is already in the whitelist.")
            return False

        self.whitelist[username_lower] = {
            "username": username,
            "added_at": datetime.now().isoformat()
        }
        self.save_whitelist()
        print(f"{username} added.")
        self.push_to_github(f"Add {username} to whitelist")
        return True

    def remove_user(self, username):
        username_lower = username.lower()

        if username_lower not in self.whitelist:
            print(f"{username} is not in the whitelist.")
            return False

        removed = self.whitelist[username_lower]["username"]
        del self.whitelist[username_lower]
        self.save_whitelist()
        print(f"{removed} removed.")
        self.push_to_github(f"Remove {removed} from whitelist")
        return True

    def list_users(self):
        if not self.whitelist:
            print("Whitelist is empty.")
            return []

        users = sorted(self.whitelist.values(), key=lambda x: x["added_at"], reverse=True)
        print(f"\n{len(users)} user(s):\n")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user['username']}  ({user['added_at']})")
        print()
        return users

def main():
    manager = WhitelistManager()

    print("=" * 50)
    print("  ROBLOX WHITELIST MANAGER")
    print("=" * 50)

    while True:
        print("\n1. Add user")
        print("2. Remove user")
        print("3. View whitelist")
        print("4. Quit")

        choice = input("\n> ").strip()

        if choice == "1":
            username = input("Roblox username: ").strip()
            if username:
                manager.add_user(username)

        elif choice == "2":
            username = input("Username to remove: ").strip()
            if username:
                manager.remove_user(username)

        elif choice == "3":
            manager.list_users()

        elif choice == "4":
            break

if __name__ == "__main__":
    main()
