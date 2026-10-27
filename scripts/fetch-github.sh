#!/bin/sh
# Fetches the last year of contributions and public repo languages for a user into data/github.json
USER_LOGIN="${1:-erkankolakan}"
gh api graphql -f login="$USER_LOGIN" -f query='
query($login:String!){ user(login:$login){
  contributionsCollection{ contributionCalendar{
    totalContributions weeks{ contributionDays{ date contributionCount contributionLevel } } } }
  repositories(first:100, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC){ nodes{
    languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } } } } }' \
| python3 -I -c '
import json,sys
user=json.load(sys.stdin)["data"]["user"]
cal=user["contributionsCollection"]["contributionCalendar"]
days=[d for w in cal["weeks"] for d in w["contributionDays"]]
lv={"NONE":0,"FIRST_QUARTILE":1,"SECOND_QUARTILE":2,"THIRD_QUARTILE":3,"FOURTH_QUARTILE":4}
langs={}
for repo in user["repositories"]["nodes"]:
  for e in repo["languages"]["edges"]:
    l=langs.setdefault(e["node"]["name"],{"name":e["node"]["name"],"color":e["node"]["color"] or "#8b949e","size":0})
    l["size"]+=e["size"]
out={"user":sys.argv[1],"total":cal["totalContributions"],"start":days[0]["date"],
 "counts":[d["contributionCount"] for d in days],"levels":"".join(str(lv[d["contributionLevel"]]) for d in days),
 "langs":sorted(langs.values(),key=lambda l:-l["size"])[:8]}
print(json.dumps(out,separators=(",",":")))' "$USER_LOGIN" > data/github.json
