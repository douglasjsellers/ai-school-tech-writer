import os
import base64
import random
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage


def format_data_for_openai(diffs, readme_content, commit_messages):
    # Combine the changes into a string with clear delineation.
    changes = "\n".join(
        [f'File: {file["filename"]}\nDiff: \n{file["patch"]}\n' for file in diffs]
    )

    # Combine all commit messages
    commit_messages = "\n".join(commit_messages) + "\n\n"

    # Decode the README content
    readme_content = base64.b64decode(readme_content.content).decode("utf-8")

    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Please review the following code changes and commit messages from a GitHub pull request:\n"
        "Code changes from Pull Request:\n"
        f"{changes}\n"
        "Commit messages:\n"
        f"{commit_messages}"
        "Here is the current README file content:\n"
        f"{readme_content}\n"
        "Consider the code changes and commit messages, determine if the README needs to be updated. If so, edit the README, ensuring to maintain its existing style and clarity.\n"
        "Updated README:\n"
    )
    return prompt


def call_openai(prompt, context, type="pull requests"):
    client = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an AI trained to help with updating README files based on code changes."),
        HumanMessage(content=f"Here's the context of the {type}: {context}\n\n{prompt}")
    ])
    try:
        prompt = prompt_template.format_messages(context=context)
        # Make the API call to OpenAI chat interface
        response = client.invoke(input=prompt)
        parser = StrOutputParser()
        content = parser.invoke(input=response)

        return content
    except Exception as e:
        print(f"Error making OpenAI API call: {e}")


def update_readme_and_create_pr(repo, updated_readme, readme_sha):
    """
    Submit Updated README content as a PR in a new branch
    """

    commit_message = "Proposed README update based on recent code changes"
    main_branch = repo.get_branch("main")
    new_branch_name = f"update-readme-{readme_sha}-{random.randint(1, 1000)}"
    new_branch = repo.create_git_ref(
        ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha
    )

    # Update the README file
    repo.update_file(
        path="README.md",
        message=commit_message,
        content=updated_readme,
        sha=readme_sha,
        branch=new_branch_name,
    )

    # Create a PR for this document anad stuff
    pr_title = "Update README based on recent changes"
    br_body = "This PR proposes an update to the README based on recent code changes. Please review and merge if appropriate."
    pull_request = repo.create_pull(
        title=pr_title, body=br_body, head=new_branch_name, base="main"
    )

    return pull_request

def code_base_summary( vector_store ):
    pulling_prompt = f"Please summarize the entire code base as human readable text between five and ten sentences long."
    prompt = ( f"{pulling_prompt}  Don't describe the individual files but rather the system as a whole. "
               "Try to make it clear and concise and like it was written by a human rather than 'The code base contains...'."
               )
    context = vector_store.fetch_context(prompt)
    return call_openai(pulling_prompt, context, "code base")

def last_five_pr_summary( pull_request_number, vector_store ):
    pulling_prompt = f"Please summarize pull request {generate_pr_string( pull_request_number )} as human readable text of 3 sentences each."
    # Format data for OpenAI prompt
    prompt = ( f"{pulling_prompt}  Please return them as an ordered list. "
               "When formatted the output rather than saying something like 'Pull Request 10' say 'PR #10: '."
               )
    context = vector_store.fetch_context(pulling_prompt)
    return call_openai(prompt, context)

def generate_pr_string(current_pr_number, count=5):
    numbers = range(current_pr_number, current_pr_number - count, -1)
    number_strings = [str(num) for num in numbers]

    if len(number_strings) > 1:
        return ", ".join(number_strings[:-1]) + f", and {number_strings[-1]}"
    else:
        return number_strings[0]