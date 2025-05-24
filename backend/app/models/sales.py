from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SaleData(BaseModel):
    """Model for individual sale data"""
    id: int = Field(description="Unique identifier for the sale")
    date: datetime = Field(description="Date and time of the sale")
    amount: float = Field(description="Total amount of the sale in MXN")
    category: str = Field(description="Product category")
    store: str = Field(description="Store name or identifier")


class CategorySales(BaseModel):
    """Model for category sales aggregation"""
    category: str = Field(description="Product category name")
    sales: float = Field(description="Total sales for the category in MXN")


class StoreMetrics(BaseModel):
    """Model for store performance metrics"""
    totalSales: float = Field(description="Total sales in MXN")
    averageTicket: float = Field(description="Average transaction value in MXN")
    topCategories: List[CategorySales] = Field(description="Top selling categories by sales amount")


class SalesResponse(BaseModel):
    """Response model for sales data endpoints"""
    sales: List[SaleData]


class MetricsResponse(BaseModel):
    """Response model for metrics endpoints"""
    metrics: StoreMetrics

