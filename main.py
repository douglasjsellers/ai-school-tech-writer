import os
from github import Github
from utility import *
from dotenv import load_dotenv
from lib.pull_request_vector import PullRequestVector
from lib.vector_store import VectorStore
from lib.code_base_vector import CodeBaseVector
import time

if os.getenv('LOAD_ENV') is not None:
    load_dotenv()
def main():
    code_vector_store = VectorStore( 'ai-school-tech-writer-code')
    code_vector_store.add_vector( CodeBaseVector('.').vectorize() )
    time.sleep(5)
    project_summary =  code_base_summary( code_vector_store )
    code_vector_store.clear_index()

    g = Github(os.getenv('GITHUB_TOKEN'))
    repo_path = os.getenv('REPO_PATH')
    pull_request_number = int(os.getenv('PR_NUMBER'))
    repo = g.get_repo(repo_path)
    pull_request = repo.get_pull(pull_request_number)
    vector = PullRequestVector(pull_request, pull_request_number)
    changes_vector_store = VectorStore( 'ai-school-tech-writer-changes' )

    changes_vector_store.add_vector(vector.vectorize())

    pr_summary = last_five_pr_summary( pull_request_number, changes_vector_store )
    readme_content = repo.get_contents("README.md")

    updated_readme = f"# AI for Developer Productivity: Technical Writer Agent\n##Project Summary\n{project_summary}\n\n##Recent Changes\n{pr_summary}"
    print( updated_readme )
    update_readme_and_create_pr(repo, updated_readme, readme_content.sha)

if __name__ == '__main__':
    main()
