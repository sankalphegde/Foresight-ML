from dotenv import load_dotenv
load_dotenv()

from src.data.pipeline.core import (
    fetch_sec_data,
    fetch_fred_data,
    merge_data,
)

def main():
    sec = fetch_sec_data()
    fred = fetch_fred_data()
    merged = merge_data(sec, fred, output_dir="data/output")
    print("Pipeline completed:", merged)

if __name__ == "__main__":
    main()
