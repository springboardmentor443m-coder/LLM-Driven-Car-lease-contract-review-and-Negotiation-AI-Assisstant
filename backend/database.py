import pandas as pd
import json
import os

class CarDatabase:
    def __init__(self):
        self.cars = self.load_cars()
        self.contracts = self.load_contracts()
        self.customers = pd.DataFrame()
    
    def load_cars(self):
        # Sample car data
        data = [
            {"id": 1, "brand": "Toyota", "model": "Camry", "year": 2024, 
             "price": 28000, "monthly": 450, "type": "Sedan", "fuel": "Hybrid",
             "image": "https://cdn.pixabay.com/photo/2019/07/25/18/58/toyota-4362817_1280.jpg"},
            {"id": 2, "brand": "Honda", "model": "Accord", "year": 2024,
             "price": 29000, "monthly": 470, "type": "Sedan", "fuel": "Petrol",
             "image": "https://cdn.pixabay.com/photo/2016/11/23/17/24/automobile-1853936_1280.jpg"},
            {"id": 3, "brand": "BMW", "model": "3 Series", "year": 2024,
             "price": 45000, "monthly": 750, "type": "Luxury", "fuel": "Petrol",
             "image": "https://cdn.pixabay.com/photo/2015/09/02/12/25/bmw-918408_1280.jpg"},
            {"id": 4, "brand": "Tesla", "model": "Model 3", "year": 2024,
             "price": 42000, "monthly": 700, "type": "Electric", "fuel": "Electric",
             "image": "https://cdn.pixabay.com/photo/2021/01/15/16/49/tesla-5919764_1280.jpg"},
            {"id": 5, "brand": "Ford", "model": "Mustang", "year": 2024,
             "price": 38000, "monthly": 620, "type": "Sports", "fuel": "Petrol",
             "image": "https://cdn.pixabay.com/photo/2012/04/13/20/37/car-33556_1280.png"},
            {"id": 6, "brand": "Mercedes", "model": "C-Class", "year": 2024,
             "price": 48000, "monthly": 800, "type": "Luxury", "fuel": "Petrol",
             "image": "https://cdn.pixabay.com/photo/2017/03/26/19/57/mercedes-benz-2176955_1280.jpg"},
        ]
        return pd.DataFrame(data)
    
    def load_contracts(self):
        return pd.DataFrame(columns=[
            'id', 'customer_name', 'car_id', 'start_date', 'end_date',
            'monthly_payment', 'status', 'created_at'
        ])
    
    def get_car_by_id(self, car_id):
        car = self.cars[self.cars['id'] == car_id]
        return car.iloc[0] if not car.empty else None
    
    def add_contract(self, contract_data):
        new_id = len(self.contracts) + 1
        contract_data['id'] = new_id
        contract_data['created_at'] = pd.Timestamp.now()
        self.contracts = pd.concat([self.contracts, pd.DataFrame([contract_data])], ignore_index=True)
        return new_id
    
    def filter_cars(self, brand=None, car_type=None, max_price=None):
        filtered = self.cars.copy()
        if brand:
            filtered = filtered[filtered['brand'] == brand]
        if car_type:
            filtered = filtered[filtered['type'] == car_type]
        if max_price:
            filtered = filtered[filtered['price'] <= max_price]
        return filtered