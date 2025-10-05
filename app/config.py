import os
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN=os.getenv('TELEGRAM_TOKEN')
MODEL_MODE=os.getenv('MODEL_MODE','templated')
RAG_TOPK=int(os.getenv('RAG_TOPK','3'))
DATA_CSV='app/data/space_weather.csv'
INDEX_DIR='app/rag/index'
STORY_YAML='app/story/story.yaml'
TEMPLATE_TURN='app/story/templates/turn.jinja'
SYSTEM_PROMPT='app/nlp/prompts/system_prompt.txt'
