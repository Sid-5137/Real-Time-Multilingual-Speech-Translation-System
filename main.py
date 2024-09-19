"""
Main script to start the real-time multilingual speech translation system.
"""
from real_time_processing.pipeline import RealTimePipeline

def main():
    pipeline = RealTimePipeline()
    pipeline.run()

if __name__ == "__main__":
    main()
