import os
import platform
import subprocess
import sys
import time
from github import Github
import select
import json
from pathlib import Path

base_folder = Path(__file__).parent.resolve()

if os.path.exists(os.getcwd() + "/sync_config.json"):
    with open("./sync_config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {
    "github_email": "",
    "github_username": "",
    "github_token": "",
    "repo_name": "",
    "run_cmd": ""
    }
    with open(os.getcwd() + "/sync_config.json", "w+") as f:
        json.dump(configTemplate, f, indent=4)
    print("First time setup. Please take a look at sync_config.json")
    exit()

# Replace with your Github username and Github token
EMAIL = configData["github_email"]
USERNAME = configData["github_username"]
TOKEN = configData["github_token"]
# Replace with the name of the repo you want to sync
REPO_NAME = configData["repo_name"]

#command to run after the sync is complete
run_cmd = configData["run_cmd"]

pipinstall = configData["install_pip_req"]

# Check if Git is installed, install it if not
if platform.system() == "Linux":
    result = subprocess.run(['dpkg', '-s', 'git'], capture_output=True)
    if result.returncode != 0:
        print("Git is not installed. Installing...")
        os.system('apt-get update')
        os.system('apt-get install -y git')

# Authenticate with the Github API using the token
g = Github(TOKEN)

# Get the authenticated user
user = g.get_user()

# Make sure config email and user are inside ""
config_email = f"\"{EMAIL}\""
config_username = f"\"{USERNAME}\""

# Check if the repository exists locally
if not os.path.exists(REPO_NAME):
    # Create a local repository with the specified name
    os.mkdir(REPO_NAME)
    os.chdir(REPO_NAME)

    # If the repository doesn't exist locally, clone it from Github
    repo = user.get_repo(REPO_NAME)
    clone_url = repo.clone_url.replace("https://", f"https://{USERNAME}:{TOKEN}@")
    os.system(f"git clone {clone_url} .")
    if pipinstall == "True":
        print("First time setup: installing pip requirementx")
        os.system(f"python3 -m pip install -r {base_folder}/{REPO_NAME}/requirements.txt")
else:
    # If the repository already exists, change to its directory
    os.chdir(REPO_NAME)
    
    # Check if Git user configuration exists, set it if it doesn't exist
    result = subprocess.run(['git', 'config', '--get', 'user.email'], capture_output=True)
    if result.returncode != 0:
        print("Git user email not set. Setting default Git user configuration...")
        subprocess.run(['git', 'config', '--global', 'user.email', config_email])
        subprocess.run(['git', 'config', '--global', 'user.name', config_username])

    # If the repository exists locally, pull changes from Github
    os.system("git fetch")
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True)
    if result.stdout:
        # If there are uncommitted changes, ask the user if they want to push changes or override with remote changes
        print("Local changes detected.")
        print("You have 10 seconds to decide if you want to push changes to Github.")
        print("Press [y] to push changes, [n] to discard changes and re-pull or wait to skip any action.")
        i, o, e = select.select([sys.stdin], [], [], 10)
        if i:
            push_changes = input("Do you want to push changes to Github? (y/n): ")
            if push_changes.lower() == "y":
                # If the user wants to push changes, commit and push the changes to Github
                commit_message = input("Enter commit message: (push from git-sync)")
                if commit_message=="":
                    commit_message="push from git-sync"
                os.system("git add .")
                os.system(f'git commit -m "{commit_message}"')
                os.system("git push")
            elif push_changes.lower() == "n":
                # If the user wants to override local changes with remote changes, discard local changes and pull from Github
                os.system("git reset --hard")
                os.system("git pull")
        else:
            print("Skipping github sync")
    else:
        # If there are no uncommitted changes, simply pull from Github
        os.system("git pull")
    
# go to repo dir
repo_dir = f"{base_folder}/{REPO_NAME}"
os.chdir(repo_dir)
# Start the main.py file
os.system(run_cmd)
