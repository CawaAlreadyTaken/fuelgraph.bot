import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

class GraphGenerator:
    def __init__(self):
        # Set style for better-looking graphs
        plt.style.use('seaborn')
        
    def generate_graph(self, data, graph_type, start_date, end_date):
        """Generate a graph based on the specified type and data."""
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        df['price_per_liter'] = df['price'] / df['liters']
        
        plt.figure(figsize=(10, 6))
        
        if graph_type == 'price':
            plt.plot(df['timestamp'], df['price_per_liter'], marker='o')
            plt.ylabel('Price per Liter')
            title = 'Fuel Price per Liter Over Time'
        elif graph_type == 'km':
            plt.plot(df['timestamp'], df['km'], marker='o')
            plt.ylabel('Kilometers Travelled')
            title = 'Kilometers Travelled Over Time'
        else:  # consumption
            df['consumption'] = df['liters'] / df['km'] * 100  # L/100km
            plt.plot(df['timestamp'], df['consumption'], marker='o')
            plt.ylabel('Consumption (L/100km)')
            title = 'Fuel Consumption Over Time'
        
        plt.title(title)
        plt.xlabel('Date')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save and return path
        filename = f'graph_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename)
        plt.close()
        
        return filename
