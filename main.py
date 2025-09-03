#!/usr/bin/env python3
"""
Main entry point for India Airspace Management System - Enhanced with Fleet Configuration
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import IndiaAirspaceMap
from ui.dialog import DepotSelectionWindow
from PyQt5.QtWidgets import QMessageBox

def main():
    """Main application entry point with depot, customer, and fleet selection"""
    app = QApplication(sys.argv)
    app.setApplicationName("India Airspace Management - Custom Depot & Fleet Configuration")
    app.setStyle('Fusion')
    
    # Step 1: Show depot and fleet selection window
    print("Starting Depot & Fleet Configuration Selection...")
    depot_dialog = DepotSelectionWindow()
    
    selected_depot = None
    selected_customer_count = None
    selected_electric_trucks = None
    selected_fuel_trucks = None
    selected_drones = None
    main_window = None
    
    def on_depot_selected(lat, lng, customer_count, electric_trucks, fuel_trucks, drones):
        nonlocal selected_depot, selected_customer_count, selected_electric_trucks, selected_fuel_trucks, selected_drones, main_window
        selected_depot = [lat, lng]
        selected_customer_count = customer_count
        selected_electric_trucks = electric_trucks
        selected_fuel_trucks = fuel_trucks
        selected_drones = drones
        
        total_vehicles = electric_trucks + fuel_trucks + drones
        
        print(f"Configuration selected:")
        print(f"  Depot: {lat:.6f}, {lng:.6f}")
        print(f"  Customers: {customer_count}")
        print(f"  Fleet: {electric_trucks} electric trucks, {fuel_trucks} fuel trucks, {drones} drones")
        print(f"  Total vehicles: {total_vehicles}")
        
        # Close the depot dialog
        depot_dialog.close()
        
        # Step 2: Launch main application with selected configuration
        print(f"\nLaunching main application with full configuration...")
        
        # Create main window with all selected parameters
        main_window = IndiaAirspaceMap(
            depot_coords=selected_depot, 
            customer_count=selected_customer_count,
            electric_trucks=selected_electric_trucks,
            fuel_trucks=selected_fuel_trucks,
            drones=selected_drones
        )
        main_window.show()
        
        print("\n" + "="*70)
        print("INDIA AIRSPACE MANAGEMENT SYSTEM LAUNCHED!")
        print("="*70)
        print("Configuration Applied:")
        print(f"📍 Depot Location: {selected_depot[0]:.6f}, {selected_depot[1]:.6f}")
        print(f"👥 Customers: {selected_customer_count}")
        print(f"🚚 Fleet Configuration:")
        print(f"   • Electric Trucks: {selected_electric_trucks}")
        print(f"   • Fuel Trucks: {selected_fuel_trucks}")
        print(f"   • Drones: {selected_drones}")
        print(f"   • Total Vehicles: {total_vehicles}")
        print(f"📦 Delivery Points: {selected_customer_count} points generated around depot")
        print("\nFeatures:")
        print("✅ Custom Fleet Configuration Applied")
        print("✅ Comprehensive No-Fly Zones across India")
        print("✅ Real-time Vehicle Movement (NO map reloading)")
        print("✅ Left Sidebar: Vehicle Controls & Delivery Info")
        print("✅ Right Sidebar: Drone Sound Monitoring & Statistics")
        print("✅ Interactive Controls:")
        print("   • Change Depot Location & Fleet Configuration (anytime)")
        print("   • Toggle No-Fly Zones")
        print("   • Toggle Vehicles") 
        print("   • Start/Stop Vehicle Movement")
        print(f"\n🚀 Your Fleet ({total_vehicles} vehicles):")
        print(f"• Drones: {selected_drones} units - Blue icons with dotted routes (60 km/h)")
        print(f"• Electric Trucks: {selected_electric_trucks} units - Green icons (40 km/h)")  
        print(f"• Fuel Trucks: {selected_fuel_trucks} units - Orange icons (35 km/h)")
        print(f"\n📦 Delivery System:")
        print("• All vehicles start from YOUR selected depot")
        print(f"• {selected_customer_count} delivery points generated around depot")
        print("• Real-time vehicle trails and status monitoring")
        print("• Each vehicle gets assigned a delivery route")
        print("\n🎯 Advanced Features:")
        print("• Full depot & fleet reconfiguration without restarting")
        print("• Automatic delivery point regeneration")
        print("• Real-time sound monitoring simulation")
        print("• Comprehensive vehicle status tracking")
        print("• Scalable fleet management (up to 200 vehicles total)")
        print("="*70)
    
    def on_dialog_closed():
        """Handle when depot dialog is closed without selection"""
        if not selected_depot:
            print("No configuration selected. Exiting application.")
            app.quit()
    
    # Connect signals - now expects 6 parameters instead of 3
    depot_dialog.depot_selected.connect(on_depot_selected)
    
    # Show the depot selection window
    depot_dialog.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()