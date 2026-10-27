#!/bin/sh
# Fetches the last year of contributions for a user into data/github.json
USER_LOGIN="${1:-erkankolakan}"
gh api graphql -f login="$USER_LOGIN" -f query='
query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
  totalContributions weeks{ contributionDays{ date contributionCount contributionLevel } } } } } }' \
| python3 -I -c '
import json,sys
cal=json.load(sys.stdin)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
days=[d for w in cal["weeks"] for d in w["contributionDays"]]
lv={"NONE":0,"FIRST_QUARTILE":1,"SECOND_QUARTILE":2,"THIRD_QUARTILE":3,"FOURTH_QUARTILE":4}
out={"user":sys.argv[1],"total":cal["totalContributions"],"start":days[0]["date"],
 "counts":[d["contributionCount"] for d in days],"levels":"".join(str(lv[d["contributionLevel"]]) for d in days)}
print(json.dumps(out,separators=(",",":")))' "$USER_LOGIN" > data/github.json
