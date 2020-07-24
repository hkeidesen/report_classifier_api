# docker run --name classified-reports-db -p 4000:4000 -e POSTGRES_DB=classified-reports -e POSTGRES_PASSWORD=K19h5Br4 -d postgres
import os


user = os.environ['POSTGRES_USER'] # postgres
password = os.environ['POSTGRES_PASSWORD'] # K19h5Br4
host = os.environ['POSTGRES_HOST'] # localhost
database = os.environ['POSTGRES_DB'] # classified-reports
port = os.environ['POSTGRES_PORT'] # 4000:4000


DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

