from typing import Tuple
from functools import reduce
import requests
from requests.auth import HTTPBasicAuth
import re

import streamlit as st
import pandas as pd

from ..types import Page


class Octosuite(Page):
    endpoint = "https://api.github.com"

    def write(self):
        st.title("Octosuite")
        st.write(
            "This is a dashboard implementation of the Octosuite CLI tool. It allows a user to use the GitHub API without having much technical knowledge. This is an MVP so is not really tested and definitely needs some refacoring!"
        )

        st.markdown("## Select User")
        username = st.text_input("Enter GitHub username")

        if username:
            st.markdown("### User Attributes")
            user_attrs = self.user_profile(username)
            st.write(user_attrs)

            st.markdown("## Select Repo")
            repos = self.get_repos_from_username(username)
            select_repo = st.selectbox("Select repo", repos)

            if select_repo:
                email = self.get_email_from_contributor(username, select_repo, username)
                st.markdown(f"User: {username}, Repo: `{select_repo}`, Email: {email}")

                st.markdown("### Repo Contributors")
                contributors = self.repo_contributors(username, select_repo)
                st.dataframe(contributors)

            st.markdown("## Select Gist")
            gists = self.user_gists(username)
            st.dataframe(gists)

    def get_repos_from_username(self, username: str):
        response = requests.get(
            f"{self.endpoint}/users/{username}/repos?per_page=100&sort=pushed",
            auth=HTTPBasicAuth(username, ""),
        ).text
        repositories = re.findall(
            rf'"full_name":"{username}/(.*?)",.*?"fork":(.*?),', response
        )
        unforked_repos = []
        for repository in repositories:
            if repository[1] == "false":
                unforked_repos.append(repository[0])
        return unforked_repos

    def user_gists(self, username, limit=100):
        response = requests.get(
            f"{self.endpoint}/users/{username}/gists?per_page={limit}"
        )
        return response.json()

    def user_profile(self, username: str):
        response = requests.get(f"{self.endpoint}/users/{username}")
        if response.status_code == 404:
            print(f"username {username} not found")

        return response.json()

    def repo_contributors(self, username: str, repo_name: str, limit: int = 100):
        response = requests.get(
            f"{self.endpoint}/repos/{username}/{repo_name}/contributors?per_page={limit}"
        )
        if response.status_code == 404:
            print(f"username {username} or repo {repo_name} not found")

        return response.json()

    def get_email_from_contributor(self, username, repo, contributor):
        response = requests.get(
            f"https://github.com/{username}/{repo}/commits?author={contributor}",
            auth=HTTPBasicAuth(username, ""),
        ).text
        latest_commit = re.search(rf'href="/{username}/{repo}/commit/(.*?)"', response)
        if latest_commit:
            latest_commit = latest_commit.group(1)
        else:
            latest_commit = "dummy"
        commit_details = requests.get(
            f"https://github.com/{username}/{repo}/commit/{latest_commit}.patch",
            auth=HTTPBasicAuth(username, ""),
        ).text
        email = re.search(r"<(.*)>", commit_details)
        if email:
            email = email.group(1)
        return email
