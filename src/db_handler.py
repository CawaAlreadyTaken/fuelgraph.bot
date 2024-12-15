from pymongo import MongoClient
from datetime import datetime

class DBHandler:
    def __init__(self):
        self.client = MongoClient('mongodb://mongodb:27017/')
        self.db = self.client['fuelgraph']
        self.refills = self.db['refills']

    def add_refill(self, data):
        """Add a new refill record to the database."""
        self.refills.insert_one(data)

    def get_refills(self, user_id, start_date, end_date):
        """Get refill records for a specific user and date range."""
        query = {
            'user_id': user_id,
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date
            }
        }
        return list(self.refills.find(query).sort('timestamp', 1))

