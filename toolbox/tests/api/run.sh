sudo docker compose -f ../../../docker-compose.yaml up --build -d
python _test_API_ImageStorage.py
python -m unittest discover -s . -v
docker compose -f ../../../docker-compose.yaml down --volumes