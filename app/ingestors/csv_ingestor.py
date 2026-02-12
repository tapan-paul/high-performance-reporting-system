"""
CSV Ingestor Module
-------------------
This module defines the CSVIngestor class, which is responsible for ingesting data from CSV
files. It implements the BaseIngestor contract, providing an asynchronous streaming interface
that yields each row of the CSV file as a dictionary. This allows the Orchestrator to
process CSV data without needing to know the specifics of the file handling, ensuring modularity
and pluggability in the data ingestion process.
Usage:
    To use the CSVIngestor, create an instance and call the stream_data method with the path
    to the CSV file. The method will return an asynchronous generator that yields each row as a
    dictionary.
    Example:
    csv_ingestor = CSVIngestor()
    async for row in csv_ingestor.stream_data('path/to/file.csv'):
        print(row)
"""
import csv
import aiofiles
from .base_ingestor import BaseIngestor

class CSVIngestor(BaseIngestor):
    """
    Ingestor for CSV files. Implements the BaseIngestor contract.
    """
    async def stream_data(self, source: str):
        async with aiofiles.open(source, mode='r', encoding='utf-8') as f:
            header = await f.readline()
            fieldnames = [f.strip() for f in header.split(',')]
            
            async for line in f:
                values = line.strip().split(',')
                if len(values) == len(fieldnames):
                    yield dict(zip(fieldnames, values))