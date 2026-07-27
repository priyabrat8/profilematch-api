import psycopg2
from psycopg2.extras import execute_values
from app.config import DB_CONFIG 

def get_connection():
	return psycopg2.connect(**DB_CONFIG)

def insert_candidate(profile: dict, embedding : list[float]):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("""
		INSERT INTO candidates 
		(name, email, phone, summary, embedding) 
		VALUES (%s,%s,%s,%s,%s)
		RETURNING id;
		""", (
			profile["name"],
			profile["email"],
			profile["phone"],
			profile["summary"],
			embedding
			))
	
	candidate_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()
	return candidate_id