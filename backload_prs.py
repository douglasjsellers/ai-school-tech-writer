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
    for pull_request_number in range(1, 10):

        # Get the repo object
        repo = g.get_repo(repo_path)

        # print(readme_content)
        # Fetch pull request by number
        pull_request = repo.get_pull(pull_request_number)

        vector = PullRequestVector(pull_request, pull_request_number)
        vector_store = VectorStore( os.getenv( 'PINECONE_INDEX_CHANGES'))
        vector_store.add_vector(vector.vectorize())



if __name__ == '__main__':
    main()
