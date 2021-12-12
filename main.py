#%%
import requests
import dateutil.parser as parser
import datetime
import sys
import os

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
#%%
output = f"Last commit: {commit_dates_parsed[0]} Last sync: {last_modified_parsed - datetime.timedelta(hours=1)}"
print(output)

result = 0
if list(filter(lambda x: x > last_modified_parsed, commit_dates_parsed)) != []:
    result = 1
    print("Sync is at least 1 hour behind")

#%%
GITHUB_ENV = os.environ["GITHUB_ENV"]

#%%
with open(GITHUB_ENV, "a") as f:
    f.write(f"output={output}\n")
    f.write(f"result={result}\n")
