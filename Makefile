run:
	cd back/ && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload --env-file ../.env && cd ..

main:
	cd app/ && uv python main.py
clean:
	docker compose down -v
	sudo rm -rf db/data/

app:
	docker compose up app
#
#build:
#	docker compose build
#
#up:
#	docker compose up
#
#flake:
#	flake8 rag_app | grep -v 'E501' && cd ..
#
#tests:
#	docker compose exec app bash app/scripts/tests.sh
#
#
#	sudo rm -rf app/logs/

