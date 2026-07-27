import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

llm = ChatOpenAI(
	model="gpt-5-mini",
	temperature=0,
	api_key=os.getenv("OPENAI_API_KEY")
	)

embeddings = OpenAIEmbeddings(
	model="text-embedding-3-small",
	api_key=os.getenv("OPENAI_API_KEY")
	)

DB_CONFIG = {
	"dbname": os.getenv("DB_NAME"),
	"user": os.getenv("DB_USER"),
	"password": os.getenv("DB_PASSWORD"),
	"host": os.getenv("DB_HOST"),
	"port": os.getenv("DB_PORT"),
}