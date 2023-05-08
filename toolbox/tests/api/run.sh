sudo docker compose -f ../../../docker-compose.test.yaml up --build -d
python _test_API_ImageStorage.py
python -m unittest discover -s . -v
docker compose -f ../../../docker-compose.test.yaml down --volumes