from app.ingestion import run_full_ingestion

if __name__ == "__main__":
    run_full_ingestion("data/raw_docs", namespace="sop")