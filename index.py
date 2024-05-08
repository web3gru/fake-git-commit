import subprocess
import os
from dotenv import load_dotenv

# Main function
def run_command(command):
    """
    Execute a given shell command using subprocess and handle output.
    
    Parameters:
        command (str): The command line string to be executed by the shell.

    Outputs execution stdout and stderr to console.
    """
    result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        print(result.stdout.decode().strip())
    if result.stderr:
        print("Error:", result.stderr.decode().strip())

def fake_repository(url, username):
    """
    Clone the repository from GitHub, switch to main branch, and overwrite author/committer info.

    Parameters:
        url (str): The repository name.
        username (str): The GitHub username where the repository is hosted.

    Changes are saved into the local clone and ready to be pushed back.
    """
    print(f"Faking repository: {url}")
    # Construct the complete Git repo URL with authentication token
    git_url = f'https://{os.getenv("GITHUB_TOKEN")}@github.com/{username}/{url}.git'
    
    # Clone the GitHub repository
    run_command(f'git clone {git_url}')
    
    # Change directory into the cloned repository
    os.chdir(url)
    
    # Rename the default branch to 'main'
    run_command('git branch -M main')
    
    # Apply changes to the Git history to modify author and committer details
    run_command("""
        git filter-branch -f --env-filter '
            GIT_AUTHOR_NAME="{0}";
            GIT_AUTHOR_EMAIL="{1}";
            GIT_COMMITTER_NAME="{0}";
            GIT_COMMITTER_EMAIL="{1}";
        ' HEAD
    """.format(os.getenv("G_NAME"), os.getenv("G_EMAIL")))
    
    # Change directory back to the original directory
    os.chdir('..')
    
    print(f"Successfully faked repository: {url}")

def push_repository(url):
    """
    Push local changes of the repository back to GitHub.

    Parameters:
        url (str): The repository name.
    """
    print(f"Pushing repository: {url}")
    
    # Navigate into the repository's directory
    os.chdir(url)
    
    # Push changes back to GitHub using the authentication token
    run_command(f'git push https://github.com/{os.getenv("G_NAME")}/{url}')
    
    # Navigate back to the original directory
    os.chdir('..')
    
    print(f"Successfully pushed repository: {url}")

if __name__ == '__main__':
    # Load environment variables from the .env file
    load_dotenv()

    # Open the file containing GitHub repo URLs
    with open("fork_url.txt", "r", encoding='utf8') as f:
        repositories = f.readlines()

    # Process each repository URL from the file
    for repo in repositories:
        repo = repo.strip()
        if repo:
            url_list = repo.split("/")
            url = url_list[4]
            username = url_list[3]
            print(f"Processing repository: {url}")
            fake_repository(url, username)
            push_repository(url)
