PROJECT="wellness-cron"

deploy:
	[ -f "secrets.py" ] || ( echo "Please create a secrets.py file with\n\tslack_alertlib_webhook_url = 'foo...'\nin it." ; exit 1 )
	gcloud preview app deploy app.yaml cron.yaml --promote --stop-previous-version --project $(PROJECT)

.PHONY: deploy
