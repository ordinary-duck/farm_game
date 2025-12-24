# -*- coding: utf-8 -*-
# """
# Database Connection and Operations Module
# """
import pymssql
from config import DB_CONFIG


class Database:
    """Database Connection Class"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.conn = pymssql.connect(
                server=DB_CONFIG['server'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG['charset']
            )
            self.cursor = self.conn.cursor(as_dict=True)
            print("Database connected successfully!")
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database disconnected")
    
    def execute_query(self, query, params=None):
        """Execute query statement"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """Execute update statement"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Update error: {e}")
            self.conn.rollback()
            return False
    
    # ==================== Player Related ====================
    
    def get_all_players(self):
        """Get all players"""
        query = """
        SELECT PlayerId, Name, Level, Exp, CurrencyGold, CurrencyGem, Status
        FROM game.Player
        WHERE Status = 'Active'
        ORDER BY PlayerId
        """
        return self.execute_query(query)
    
    def get_player_by_id(self, player_id):
        """Get player info by ID"""
        query = """
        SELECT PlayerId, Name, Level, Exp, CurrencyGold, CurrencyGem, Status
        FROM game.Player
        WHERE PlayerId = %s
        """
        result = self.execute_query(query, (player_id,))
        return result[0] if result else None
    
    # ==================== Farm Related ====================
    
    def get_player_farms(self, player_id):
        """Get all farms of a player"""
        query = """
        SELECT FarmId, PlayerId, Name, SoilQuality
        FROM game.Farm
        WHERE PlayerId = %s
        ORDER BY FarmId
        """
        return self.execute_query(query, (player_id,))
    
    def get_farm_by_id(self, farm_id):
        """Get farm info by ID"""
        query = """
        SELECT FarmId, PlayerId, Name, SoilQuality
        FROM game.Farm
        WHERE FarmId = %s
        """
        result = self.execute_query(query, (farm_id,))
        return result[0] if result else None
    
    # ==================== Plot Related ====================
    
    def get_farm_plots(self, farm_id):
        """Get all plots of a farm"""
        query = """
        SELECT p.PlotId, p.FarmId, p.X, p.Y, p.Status, 
               p.CropVarietyId, p.PlantedAt, p.WaterLevel, p.FertilizerLevel,
               cv.Name AS CropName, cv.GrowthHours
        FROM game.Plot p
        LEFT JOIN game.CropVariety cv ON cv.CropVarietyId = p.CropVarietyId
        WHERE p.FarmId = %s
        ORDER BY p.X, p.Y
        """
        return self.execute_query(query, (farm_id,))
    
    def update_plot_status(self, plot_id, status):
        """Update plot status"""
        query = """
        UPDATE game.Plot
        SET Status = %s
        WHERE PlotId = %s
        """
        return self.execute_update(query, (status, plot_id))
    
    def plant_crop(self, plot_id, crop_variety_id):
        """Plant crop"""
        query = """
        UPDATE game.Plot
        SET Status = 'Growing', CropVarietyId = %s, PlantedAt = SYSUTCDATETIME()
        WHERE PlotId = %s AND Status = 'Empty'
        """
        return self.execute_update(query, (crop_variety_id, plot_id))
    
    def harvest_plot(self, plot_id):
        """Harvest crop"""
        query = """
        UPDATE game.Plot
        SET Status = 'Empty', CropVarietyId = NULL, PlantedAt = NULL, 
            WaterLevel = 0, FertilizerLevel = 0
        WHERE PlotId = %s AND Status = 'Mature'
        """
        return self.execute_update(query, (plot_id,))

    def reset_plot(self, plot_id):
        """Force reset plot to empty state (used for clearing withered crops)."""
        query = """
        UPDATE game.Plot
        SET Status = 'Empty', CropVarietyId = NULL, PlantedAt = NULL,
            WaterLevel = 0, FertilizerLevel = 0
        WHERE PlotId = %s
        """
        return self.execute_update(query, (plot_id,))

    def set_plot_levels(self, plot_id, water_level=None, fertilizer_level=None):
        """Update soil moisture / fertilizer."""
        fields = []
        params = []
        if water_level is not None:
            fields.append("WaterLevel = %s")
            params.append(water_level)
        if fertilizer_level is not None:
            fields.append("FertilizerLevel = %s")
            params.append(fertilizer_level)
        if not fields:
            return False
        query = f"UPDATE game.Plot SET {', '.join(fields)} WHERE PlotId = %s"
        params.append(plot_id)
        return self.execute_update(query, tuple(params))
    
    # ==================== Inventory Related ====================
    
    def get_farm_inventory(self, farm_id):
        """Get farm inventory"""
        query = """
        SELECT i.InventoryId, i.FarmId, i.ItemId, i.Quantity,
               ic.Name, ic.ItemType, ic.BasePrice
        FROM game.Inventory i
        JOIN game.ItemCatalog ic ON ic.ItemId = i.ItemId
        WHERE i.FarmId = %s AND i.Quantity > 0
        ORDER BY ic.ItemType, ic.Name
        """
        return self.execute_query(query, (farm_id,))
    
    def update_inventory(self, farm_id, item_id, quantity_change):
        """Update inventory quantity"""
        query = """
        MERGE game.Inventory AS t
        USING (SELECT %s AS FarmId, %s AS ItemId) AS s
        ON (t.FarmId = s.FarmId AND t.ItemId = s.ItemId)
        WHEN MATCHED THEN 
            UPDATE SET Quantity = t.Quantity + %s
        WHEN NOT MATCHED THEN 
            INSERT (FarmId, ItemId, Quantity) 
            VALUES (s.FarmId, s.ItemId, %s);
        """
        return self.execute_update(query, (farm_id, item_id, quantity_change, quantity_change))
    
    # ==================== Crop Variety Related ====================
    
    def get_all_crop_varieties(self):
        """Get all crop varieties"""
        query = """
        SELECT CropVarietyId, Name, GrowthHours, BaseYield, SeedItemId, ProduceItemId
        FROM game.CropVariety
        ORDER BY CropVarietyId
        """
        return self.execute_query(query)
    
    # ==================== Item Related ====================
    
    def get_all_items(self):
        """Get all items"""
        query = """
        SELECT ItemId, Name, ItemType, StackLimit, BasePrice
        FROM game.ItemCatalog
        ORDER BY ItemType, Name
        """
        return self.execute_query(query)
    
    # ==================== Action Log ====================
    
    def log_action(self, player_id, farm_id, action, meta_json):
        """Log player action"""
        query = """
        INSERT INTO game.ActionLog(PlayerId, FarmId, Action, MetaJson)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_update(query, (player_id, farm_id, action, meta_json))


# Global database instance
db = Database()

