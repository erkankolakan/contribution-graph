#!/bin/sh
# Refreshes data/github.json and inlines it into index.html
cd "$(dirname "$0")"
./scripts/fetch-github.sh "${1:-erkankolakan}"
python3 -I -c 'import sys;t=open(sys.argv[1]).read();d=open(sys.argv[2]).read().strip();open(sys.argv[3],"w").write(t.replace("__DATA__",d))' template.html data/github.json index.html
echo "index.html built"
