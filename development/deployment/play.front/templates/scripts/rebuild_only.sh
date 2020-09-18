eval `ssh-agent -s` >/dev/null 2>/dev/null && ssh-add ~/github.ssh/github_do_rsa >/dev/null 2>/dev/null

echo
echo "****************************************"
date
echo "Rebuild only."
echo "****************************************"
echo

cd ~/DataOcean
sh clear_eslint_cache.sh
npm install
npm run build

echo
echo "---------------------"
echo "LANDING"
echo "---------------------"
echo

cd ~/DataOcean/landing
npm install
npm run build
