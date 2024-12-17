from typing import Any
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class GraphGenerator:
    def __init__(self):
        # Set style for better-looking graphs
        print(plt.style.available)
        plt.style.use('seaborn-v0_8-dark')
        
    def generate_graph(
        self,
        user_id: int,
        data: list[Any],
        graph_type: str,
        start_date: datetime,
        end_date: datetime
    ):
        """Generate a graph based on the specified type and data."""
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        df['price_per_liter'] = df['price'] / df['liters']
        
        plt.figure(figsize=(10, 6))
        
        if graph_type == 'price':
            total_cost = df['price'].sum()
            plt.plot(df['timestamp'], df['price_per_liter'], marker='o')
            plt.ylabel('Price per Liter')
            title = f"Fuel Price per Liter Over Time. Total Cost: {total_cost:.2f}€"
        elif graph_type == 'km':
            total_km = df['km'].sum()
            plt.plot(df['timestamp'], df['km'], marker='o')
            plt.ylabel('Kilometers Travelled')
            title = f"Kilometers Travelled Over Time. Total KM: {total_km:.2f}km"
        else:  # consumption
            df['consumption'] = df['liters'] / df['km'] * 100  # L/100km
            total_liters = df['liters'].sum()
            plt.plot(df['timestamp'], df['consumption'], marker='o')
            plt.ylabel('Consumption (L/100km)')
            title = f"Fuel Consumption Over Time. Total Liters: {total_liters:.2f}L"
        
        plt.title(title)
        plt.xlabel('Date')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save and return path
        filename = f'graph_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename)
        plt.close()
        
        return filename
