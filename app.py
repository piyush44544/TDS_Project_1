import requests
import csv
import time

# API settings
BASE_URL = "https://api.github.com"
TOKEN = "your_personal_access_token"  # Replace with your GitHub token
HEADERS = {"Authorization": f"token {TOKEN}"}

# Function to get users in Berlin with more than 200 followers
def get_users_in_berlin(min_followers=200, location="Berlin"):
    users = []
    page = 1

    while True:
        query = f"location:{location} followers:>{min_followers}"
        url = f"{BASE_URL}/search/users?q={query}&per_page=30&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching users: {response.status_code}")
            break

        data = response.json()
        users.extend(data.get("items", []))
        
        if len(data["items"]) < 30:
            break

        page += 1
        time.sleep(1)  # Avoid rate limiting

    return users

# Function to get repositories for each user
def get_user_repos(username):
    url = f"{BASE_URL}/users/{username}/repos?sort=pushed&per_page=500"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

# Function to clean company names
def clean_company_name(company):
    if not company:
        return ""
    company = company.strip()
    if company.startswith("@"):
        company = company[1:]
    return company.upper()

# Write users and repositories to CSV
def save_to_csv(users_data, repos_data):
    # Save users.csv
    with open("users.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])
        for user in users_data:
            writer.writerow([
                user.get("login", ""),
                user.get("name", ""),
                clean_company_name(user.get("company", "")),
                user.get("location", ""),
                user.get("email", ""),
                str(user.get("hireable", "")).lower(),
                user.get("bio", ""),
                user.get("public_repos", ""),
                user.get("followers", ""),
                user.get("following", ""),
                user.get("created_at", "")
            ])

    # Save repositories.csv
    with open("repositories.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "full_name", "created_at", "stargazers_count", "watchers_count", "language", "has_projects", "has_wiki", "license_name"])
        for repo in repos_data:
            writer.writerow([
                repo.get("owner", {}).get("login", ""),
                repo.get("full_name", ""),
                repo.get("created_at", ""),
                repo.get("stargazers_count", ""),
                repo.get("watchers_count", ""),
                repo.get("language", ""),
                str(repo.get("has_projects", "")).lower(),
                str(repo.get("has_wiki", "")).lower(),
                repo.get("license", {}).get("key", "")
            ])

# Main script
users = get_users_in_berlin()
users_data = []
repos_data = []

for user in users:
    username = user["login"]
    user_details = requests.get(f"{BASE_URL}/users/{username}", headers=HEADERS).json()
    users_data.append(user_details)

    print(f"Fetching repos for {username}...")
    repos = get_user_repos(username)
    for repo in repos:
        repo["owner"] = {"login": username}  # Add owner login for reference
        repos_data.append(repo)
    time.sleep(1)

save_to_csv(users_data, repos_data)
print("Data saved to users.csv and repositories.csv")
