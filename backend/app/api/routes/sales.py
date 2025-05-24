from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
import random

from app.models.sales import SaleData, StoreMetrics, CategorySales

router = APIRouter()

# In a real application, this data would come from a database
# For demo purposes, we'll generate mock data

# Sample store names
STORES = ["Oxxo Centro", "Oxxo Norte", "Oxxo Sur", "Oxxo Este", "Oxxo Oeste"]

# Sample product categories
CATEGORIES = ["Bebidas", "Snacks", "Alimentos", "Servicios", "Tabaco", "Electrónicos", "Otros"]

# Generate random sales data
def generate_mock_sales(days: int = 30) -> List[SaleData]:
    sales = []
    now = datetime.now()
    
    for i in range(1, 200):  # Generate 200 sales records
        # Random date within the specified period
        random_days = random.randint(0, days)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        sale_date = now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        # Random amount between 20 and 500 pesos
        amount = round(random.uniform(20, 500), 2)
        
        # Random category and store
        category = random.choice(CATEGORIES)
        store = random.choice(STORES)
        
        sales.append(SaleData(
            id=i,
            date=sale_date,
            amount=amount,
            category=category,
            store=store
        ))
    
    # Sort by date (newest first)
    sales.sort(key=lambda x: x.date, reverse=True)
    return sales

# Filter sales by period
def filter_sales_by_period(sales: List[SaleData], period: str) -> List[SaleData]:
    now = datetime.now()
    
    if period == "daily":
        # Today's sales
        return [sale for sale in sales if (now - sale.date).days < 1]
    elif period == "weekly":
        # This week's sales
        return [sale for sale in sales if (now - sale.date).days < 7]
    elif period == "monthly":
        # This month's sales
        return [sale for sale in sales if (now - sale.date).days < 30]
    else:
        # Default to all sales
        return sales

# Calculate metrics from sales data
def calculate_metrics(sales: List[SaleData]) -> StoreMetrics:
    if not sales:
        return StoreMetrics(
            totalSales=0,
            averageTicket=0,
            topCategories=[]
        )
    
    # Calculate total sales
    total_sales = sum(sale.amount for sale in sales)
    
    # Calculate average ticket
    average_ticket = total_sales / len(sales)
    
    # Calculate sales by category
    category_sales = {}
    for sale in sales:
        if sale.category in category_sales:
            category_sales[sale.category] += sale.amount
        else:
            category_sales[sale.category] = sale.amount
    
    # Convert to list of CategorySales objects and sort by sales (descending)
    top_categories = [
        CategorySales(category=category, sales=amount)
        for category, amount in category_sales.items()
    ]
    top_categories.sort(key=lambda x: x.sales, reverse=True)
    
    return StoreMetrics(
        totalSales=total_sales,
        averageTicket=average_ticket,
        topCategories=top_categories
    )

# API Endpoints

@router.get("/sales", response_model=List[SaleData])
async def get_sales(period: Optional[str] = Query("monthly", description="Time period: daily, weekly, or monthly")):
    """
    Get sales data for the specified time period.
    """
    if period not in ["daily", "weekly", "monthly", "all"]:
        raise HTTPException(status_code=400, detail="Invalid period. Must be one of: daily, weekly, monthly, all")
    
    all_sales = generate_mock_sales()
    filtered_sales = filter_sales_by_period(all_sales, period)
    
    return filtered_sales

@router.get("/sales/by-period", response_model=List[SaleData])
async def get_sales_by_period(period: Optional[str] = Query("monthly", description="Time period: daily, weekly, or monthly")):
    """
    Get sales data grouped by the specified time period.
    """
    if period not in ["daily", "weekly", "monthly", "all"]:
        raise HTTPException(status_code=400, detail="Invalid period. Must be one of: daily, weekly, monthly, all")
    
    all_sales = generate_mock_sales()
    filtered_sales = filter_sales_by_period(all_sales, period)
    
    return filtered_sales

@router.get("/metrics", response_model=StoreMetrics)
async def get_metrics(period: Optional[str] = Query("monthly", description="Time period: daily, weekly, or monthly")):
    """
    Get store performance metrics for the specified time period.
    """
    if period not in ["daily", "weekly", "monthly", "all"]:
        raise HTTPException(status_code=400, detail="Invalid period. Must be one of: daily, weekly, monthly, all")
    
    all_sales = generate_mock_sales()
    filtered_sales = filter_sales_by_period(all_sales, period)
    metrics = calculate_metrics(filtered_sales)
    
    return metrics

@router.get("/dashboard/stats", response_model=StoreMetrics)
async def get_dashboard_stats():
    """
    Get summary statistics for the dashboard.
    """
    all_sales = generate_mock_sales()
    metrics = calculate_metrics(all_sales)
    
    return metrics

