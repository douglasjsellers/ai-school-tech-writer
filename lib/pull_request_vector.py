import json
from datetime import datetime, timezone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

class PullRequestVector:
    def __init__(self, pull_request, pull_request_number ):
        self._pull_request = pull_request
        self._pull_request_number = pull_request_number
        self._json = self.build_json()

    @property
    def json(self):
        return self._json

    def vectorize(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents([Document(page_content=self.json)])
        return documents
        

    def build_json(self):
        pr_json = {
            "pull_request_number": self._pull_request_number,
            "title": self._pull_request.title,
            "created_at": self._pull_request.created_at.replace(tzinfo=timezone.utc).isoformat(),
            "commits": []
        }

        for commit in self._pull_request.get_commits():
            commit_date = commit.commit.author.date.replace(tzinfo=timezone.utc).isoformat()
            commit_data = {
                "sha": commit.sha,
                "message": commit.commit.message,
                "date": commit_date,
                "author": {
                    "name": commit.commit.author.name,
                    "email": commit.commit.author.email
                },
                "files": []
            }

            # Get the files changed in this commit
            for file in commit.files:
                file_data = {
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch  # This is the diff
                }
                commit_data["files"].append(file_data)
            pr_json["commits"].append(commit_data)

            return json.dumps(pr_json, indent=4)