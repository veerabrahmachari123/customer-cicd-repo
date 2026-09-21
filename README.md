# Customer CI/CD - Multi-Environment Docker/Jenkins

## Environment mapping

| Environment | Branch | App | DB | Network | Host port |
|---|---|---|---|---|---:|
| DEV | develop | customer-app-dev | customer-db-dev | customer-dev-net | 8081 |
| UAT | release | customer-app-uat | customer-db-uat | customer-uat-net | 8082 |
| PROD | main | customer-app-prod | customer-db-prod | customer-prod-net | 8083 |

The application listens on container port 8080.

## Git workflow

```bash
git branch develop
git branch release
git checkout -b feature/customer-search

git add app/app.py
git commit -m "Add customer search endpoint"

git add app/test_app.py
git commit -m "Add customer search validation tests"

git add README.md
git commit -m "Document customer search deployment"

git checkout develop
git merge --no-ff feature/customer-search -m "Merge customer-search feature"

git checkout release
git merge --no-ff develop -m "Promote develop to UAT"

# After UAT validation:
git checkout main
git merge --no-ff release -m "Promote release to production"
git tag -a v5.0 -m "Production release 5.0"
```

## Local DEV deployment

```bash
docker network create customer-dev-net
docker volume create customer-db-dev-data

docker build --build-arg VERSION=5.0 -t customer-app:5.0 .

docker run -d --name customer-db-dev   --network customer-dev-net   -e POSTGRES_DB=customer_dev   -e POSTGRES_USER=customer_dev   -e POSTGRES_PASSWORD=devpassword   -v customer-db-dev-data:/var/lib/postgresql/data   -v "$PWD/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro"   postgres:16

docker run -d --name customer-app-dev   --network customer-dev-net   -p 8081:8080   -e ENVIRONMENT=DEV   -e APP_VERSION=5.0   -e DB_HOST=customer-db-dev   -e DB_PORT=5432   -e DB_NAME=customer_dev   -e DB_USER=customer_dev   -e DB_PASSWORD=devpassword   customer-app:5.0
```

Test:

```bash
curl http://localhost:8081/health
curl http://localhost:8081/environment
curl http://localhost:8081/version
curl "http://localhost:8081/customers/search?name=John"
```

Prove DB connectivity from inside the app container:

```bash
docker exec customer-app-dev python -c "import socket; socket.create_connection(('customer-db-dev',5432),5); print('DATABASE CONNECTIVITY SUCCESS')"
```

## Persistence test

Insert a record, remove only the DB container, recreate it with the same named volume, and verify the record remains.

```bash
docker exec customer-db-dev psql -U customer_dev -d customer_dev   -c "INSERT INTO customers(name,email) VALUES ('Persistence Test','persist@example.com');"

docker rm -f customer-db-dev
docker volume inspect customer-db-dev-data
```

Then recreate the DB using `customer-db-dev-data`.

## Jenkins

Create credentials:

- `git-credentials`
- `db-dev`
- `db-uat`
- `db-production`

Replace `YOUR_GIT_URL` in Jenkinsfile.

Parameters:

- ENVIRONMENT = DEV | UAT | PRODUCTION
- ACTION = DEPLOY | ROLLBACK
- VERSION = e.g. 5.0
- RUN_TESTS = YES | NO
- PRODUCTION_CONFIRMATION = YES | NO

The branch is derived from ENVIRONMENT; users cannot independently select a branch.

Production requires explicit confirmation.

## Evidence

```bash
git log --graph --oneline --decorate --all
git tag
docker images
docker ps
docker network inspect customer-prod-net
docker volume inspect customer-db-prod-data
```
