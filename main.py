#%%
import requests
import dateutil.parser as parser
import datetime
import sys
import os
import pytz

#%%
r = requests.get('https://api.github.com/repos/bioconda/bioconda-recipes/commits')
# %%
commit_dates = []
for commit in r.json()[:]:
    c = commit["commit"]
    commit_dates.append(c["committer"]["date"])
commit_dates_parsed = list(map(parser.parse,commit_dates))

#%%
repodata = {
    # "sync": "https://conda.anaconda.org/bioconda/rss.xml",
    "noarch": "https://conda.anaconda.org/bioconda/noarch/repodata.json.bz2",
    "linux": "https://conda.anaconda.org/bioconda/linux-64/repodata.json.bz2",
    "osx": "https://conda.anaconda.org/bioconda/osx-64/repodata.json.bz2",
}
# %%
last_modified = {}
for name,url in repodata.items():
    r = requests.head(url)
    last_modified[name] = r.headers["Last-Modified"]
last_modified_parsed = max(map(parser.parse, last_modified.values())) + datetime.timedelta(hours=1)
last_sync = max(map(parser.parse, last_modified.values()))
#%%
# 1. Were there any commits since last sync?
# 2. Was any of these commits longer than 1 hour ago
commits_since_last_sync = list(filter(lambda x: x > last_sync, commit_dates_parsed))
try:
    earliest_commit_since_last_sync = min(commits_since_last_sync)
except ValueError:
    earliest_commit_since_last_sync = None
#%%
output = f"Earliest commit since sync: {earliest_commit_since_last_sync} Last sync: {last_sync}"
print(output)

result = 0
if earliest_commit_since_last_sync:
    if earliest_commit_since_last_sync < datetime.datetime.now(pytz.utc) - datetime.timedelta(hours=1):
        result = 1
        print("Sync out of date")
    else:
        print("No hour passed since earliest commit after sync")
else:
    print("No commits since last sync")

#%%
GITHUB_ENV = os.environ["GITHUB_ENV"]

#%%
with open(GITHUB_ENV, "a") as f:
    f.write(f"output={output}\n")
    f.write(f"result={result}\n")
