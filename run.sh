#!/bin/bash
set -e

if [ ! -d "db-postgre-sql" ]; then
  git clone https://github.com/SecurityChecker/db-postgre-sql.git
fi

cd db-postgre-sql
docker-compose up -d --build

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python3 ./main.py
cd ..

pip install -r requirements.txt

python3 ./main.py
