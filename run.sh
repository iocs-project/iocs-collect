#!/bin/bash
set -e

# 1. Klonuj závislý projekt, pokud ještě není
if [ ! -d "db-postgre-sql" ]; then
  git clone https://github.com/SecurityChecker/db-postgre-sql.git
fi

# 2. Spusť docker compose z něj
cd db-postgre-sql
docker-compose up -d --build
python3 ./main.py
cd ..

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# 2. Aktivuj venv
source venv/bin/activate

# 3. Nainstaluj dependencies
pip install --upgrade pip
pip install -r requirements.txt

python3 ./main.py
