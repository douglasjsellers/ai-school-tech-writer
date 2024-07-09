import os
from github import Github
from utility import *
from dotenv import load_dotenv
from lib.pull_request_vector import PullRequestVector
from lib.vector_store import VectorStore

if os.getenv('LOAD_ENV') is not None:
    load_dotenv()
def main():
    # Initialize GitHub API with token
    g = Github(os.getenv('GITHUB_TOKEN'))

    # Get the repo path and PR number from the environment variables
    repo_path = os.getenv('REPO_PATH')
    print( os.getenv( 'PINECONE_INDEX_CHANGES'))
    pull_request_number = int(os.getenv('PR_NUMBER'))

    # Get the repo object
    repo = g.get_repo(repo_path)

    # Fetch README content (assuming README.md)
    readme_content = repo.get_contents("README.md")
    
    # print(readme_content)
    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

    vector = PullRequestVector(pull_request, pull_request_number)
    vector_store = VectorStore( os.getenv( 'PINECONE_INDEX_CHANGES'))
#    vector_store.add_vector(vector.vectorize())


    # Format data for OpenAI prompt
    prompt = "Please review the following pull requests and summarize each of the pull requests in no more than 3 sentences.  Then return a list of all of the summarized pull requests in descending order with the newest change first.  Please be sure to summarize every pull request."
    context = vector_store.fetch_context(prompt)

    # Call OpenAI to generate the updated README content
    updated_readme = call_openai(prompt, context)

    print(updated_readme)
    # Create PR for Updated PR
    #update_readme_and_create_pr(repo, updated_readme, readme_content.sha)

if __name__ == '__main__':
    main()
