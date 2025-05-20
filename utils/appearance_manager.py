import customtkinter as ctk

class AppearanceManager:
    """Centralized manager for appearance mode changes"""
    
    _instance = None
    _listeners = []
    _current_mode = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = AppearanceManager()
            cls._current_mode = ctk.get_appearance_mode()
        return cls._instance
    
    @classmethod
    def register(cls, component):
        """Register a component to receive appearance updates"""
        manager = cls.get_instance()
        if component not in manager._listeners:
            manager._listeners.append(component)
    
    @classmethod
    def unregister(cls, component):
        """Unregister a component"""
        manager = cls.get_instance()
        if component in manager._listeners:
            manager._listeners.remove(component)
    
    @classmethod
    def set_appearance_mode(cls, mode):
        """Set appearance mode and notify all listeners"""
        manager = cls.get_instance()
        
        # Set appearance mode
        ctk.set_appearance_mode(mode)
        manager._current_mode = mode
        
        # Notify all listeners
        for component in manager._listeners[:]:  # Use a copy of the list
            try:
                if hasattr(component, 'update_appearance'):
                    component.update_appearance(mode)
            except Exception as e:
                print(f"Error updating component: {e}")
                # Remove invalid components
                if component in manager._listeners:
                    manager._listeners.remove(component)