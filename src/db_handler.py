from typing import Any
from pymongo import MongoClient
from datetime import datetime

class DBHandler:
    def __init__(self):
        self.client = MongoClient('mongodb://mongodb:27017/')
        self.db = self.client['fuelgraph']
        self.refills = self.db['refills']

    def add_refill(self, data: dict[str, Any]):
        """Add a new refill record to the database."""
        self.refills.insert_one(data)

    def get_refills(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
     ) -> list[Any]:
        """Get refill records for a specific user and date range."""
        query: dict[str, int | str | dict[str, datetime]] = {
            'user_id': user_id,
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date
            }
        }
        return list(self.refills.find(query).sort('timestamp', 1))

