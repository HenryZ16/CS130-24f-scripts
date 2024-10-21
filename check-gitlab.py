import requests
import yaml
import os
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup


class GitlabAdmin:
    def __init__(self):
        # read password from "check-gitlab.yaml"
        # then login
        with open('check-gitlab.yaml', 'r') as file:
            data = yaml.safe_load(file)

        # perform login
        self.session = requests.Session()
        login_url = "http://10.15.29.208/users/sign_in"

        ## get the authenticity token
        login_page = self.session.get(login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})['content']

        ## login
        login_data = {
            'user[login]': 'root',
            'user[password]': data['password'],
            'authenticity_token': csrf_token,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        }
        response = self.session.post(login_url, data=login_data, headers=headers)

        # check response
        if response.status_code == 200:
            print("[GitlabAdmin::init] Login successful")
            self.logged_in = True
        else:
            print(
                "[GitlabAdmin::init] Login failed, status code: ", response.status_code
            )
            self.logged_in = False
            return

    def __del__(self):
        self.session.close()
        print("[GitlabAdmin::del] Session closed")

    def get_commit_info(self, groupId, commitCnt=-1):
        if self.logged_in == False:
            print("[GitlabAdmin::get_commit_info] Not logged in")
            return
        if groupId.isdigit() == False:
            print("[GitlabAdmin::get_commit_info] Invalid group id")
            return

        s_groupId = groupId if (int(groupId) >= 10) else ("0" + groupId)
        if s_groupId == "26":
            s_groupId = "-26"
        url = f"http://10.15.29.208/pintos/group{s_groupId}/-/commits/main"
        response = self.session.get(url)

        if response.status_code == 200:
            print("[GitlabAdmin::get_commit_info] Request successful")
            print("[GitlabAdmin::get_commit_info] Commit info:")
            soup = BeautifulSoup(response.text, 'html.parser')
            commits = soup.find_all('li', class_='commit flex-row js-toggle-container')

            prev_commit_time = None
            last_commit_time = None
            print(
                "[GitlabAdmin::get_commit_info] ----------------------------------------"
            )
            for commit in commits:
                if commitCnt == 0:
                    break
                commit_id = commit['id']
                commit_time = datetime.datetime.fromisoformat(
                    commit.find('time')['datetime'].replace('Z', '+00:00')
                )

                if prev_commit_time:
                    time_diff = prev_commit_time - commit_time
                    if time_diff > timedelta(days=7):
                        print(
                            f"\033[91m[GitlabAdmin::get_commit_info] Time since previous commit: {time_diff}\033[0m"
                        )
                    else:
                        print(
                            f"[GitlabAdmin::get_commit_info] Time since previous commit: {time_diff}"
                        )
                    print(
                        "[GitlabAdmin::get_commit_info] ----------------------------------------"
                    )

                print(f"[GitlabAdmin::get_commit_info]     Commit ID:   {commit_id}")
                print(f"[GitlabAdmin::get_commit_info]     Commit Time: {commit_time}")

                prev_commit_time = commit_time
                if last_commit_time == None:
                    last_commit_time = commit_time

                if commitCnt > 0:
                    commitCnt -= 1

            if last_commit_time:
                time_since_last_commit = (
                    datetime.datetime.now(datetime.timezone.utc) - last_commit_time
                )
                print(
                    "[GitlabAdmin::get_commit_info] ----------------------------------------"
                )
                if time_since_last_commit > timedelta(days=7):
                    print(
                        f"\033[91m[GitlabAdmin::get_commit_info] Time since previous commit: {time_since_last_commit}\033[0m"
                    )
                else:
                    print(
                        f"[GitlabAdmin::get_commit_info] Time since last commit: {time_since_last_commit}"
                    )

        else:
            print(
                "[GitlabAdmin::get_commit_info] Request failed, status code: ",
                response.status_code,
            )
            return


class consoleArg:
    def __init__(self):
        self.groupId = None
        self.commitCnt = -1

        self.parse_args()

    def parse_args(self):
        import argparse

        parser = argparse.ArgumentParser(description="Check gitlab commits")
        parser.add_argument("group", type=str, help="Group ID. Acceptable: numbers")
        parser.add_argument(
            "commit",
            type=str,
            help="Number of commits to show. Acceptable: numbers or 'inf'",
        )

        args = parser.parse_args()
        self.groupId = args.group
        self.commitCnt = args.commit

        print("[consoleArg::parse_args] Group ID: ", self.groupId)
        print("[consoleArg::parse_args] Commit count: ", self.commitCnt)

        if self.groupId.isdigit() == False:
            print("[consoleArg::parse_args] Invalid group id")
            os._exit(1)

        if self.commitCnt.isdigit() == False and self.commitCnt.strip() != "inf":
            print("[consoleArg::parse_args] Invalid commit count")
            os._exit(1)

    def get_groupId(self):
        return self.groupId

    def get_commitCnt(self):
        if self.commitCnt.strip() == "inf":
            return -1
        else:
            return int(self.commitCnt)


if __name__ == '__main__':
    args = consoleArg()
    groupId = args.get_groupId()
    commitCnt = args.get_commitCnt()

    rootUser = GitlabAdmin()
    rootUser.get_commit_info(groupId, commitCnt)
