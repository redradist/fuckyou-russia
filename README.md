## Anti-war tool, that helps to prevent spreading of misinformation from russian's telegram channels
1. Go to https://core.telegram.org/api/obtaining_api_id
2. Click to 'API development tools'
3. Login into Telegram
4. Name your application
5. Create local .env file and copy there `apiId` and `apiHash`:
```env
API_ID=4215242
API_HASH='a7896f9ays90yh98as9h9hasf'
```
6. Install pip dependencies `python3 -m pip install -r ./requirements.txt`
7. Run `python3 ./telegram_reporter.py`
