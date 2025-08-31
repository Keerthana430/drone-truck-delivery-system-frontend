#!/usr/bin/env python3
"""
Main entry point for India Airspace Management System
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import IndiaAirspaceMap
from ui.dialog import DepotSelectionWindow
from PyQt5.QtWidgets import QMessageBox

def main():
    """Main application entry point with depot and customer selection"""
    app = QApplication(sys.argv)
    app.setApplicationName("India Airspace Management - Custom Depot & Customer Selection")
    app.setStyle('Fusion')
    
    # Step 1: Show depot selection window
    print("Starting Depot & Customer Selection...")
    depot_dialog = DepotSelectionWindow()
    
    selected_depot = None
    selected_customer_count = None
    main_window = None
    
    def on_depot_selected(lat, lng, customer_count):
        nonlocal selected_depot, selected_customer_count, main_window
        selected_depot = [lat, lng]
        selected_customer_count = customer_count
        print(f"Depot selected: {lat:.6f}, {lng:.6f} with {customer_count} customers")
        
        # Close the depot dialog
        depot_dialog.close()
        
        # Step 2: Launch main application with selected depot and customer count
        print(f"\nLaunching main application with:")
        print(f"  Depot: {selected_depot[0]:.6f}, {selected_depot[1]:.6f}")
        print(f"  Customers: {selected_customer_count}")
        
        # Create main window with selected depot and customer count
        main_window = IndiaAirspaceMap(depot_coords=selected_depot, customer_count=selected_customer_count)
        main_window.show()
        
        print("\n" + "="*70)
        print("INDIA AIRSPACE MANAGEMENT SYSTEM LAUNCHED!")
        print("="*70)
        print("Features:")
        print("✅ Custom Depot Location & Customer Count Selected")
        print(f"   📍 Depot: {selected_depot[0]:.6f}, {selected_depot[1]:.6f}")
        print(f"   👥 Customers: {selected_customer_count}")
        print(f"   📦 Delivery Points: {selected_customer_count} points generated")
        print("✅ Comprehensive No-Fly Zones across India")
        print("✅ Real-time Vehicle Movement (NO map reloading)")
        print("✅ Left Sidebar: Vehicle Controls & Delivery Info")
        print("✅ Right Sidebar: Drone Sound Monitoring & Statistics")
        print("✅ Interactive Controls:")
        print("   • Change Depot Location & Customer Count (anytime)")
        print("   • Toggle No-Fly Zones")
        print("   • Toggle Vehicles") 
        print("   • Start/Stop Vehicle Movement")
        print("\n🚀 Moving Vehicles:")
        print("• Drones: Blue icons with dotted routes (60 km/h)")
        print("• Electric Trucks: Green icons (40 km/h)")  
        print("• Fuel Trucks: Red icons (35 km/h)")
        print(f"\n📦 Delivery System ({selected_customer_count} customers):")
        print("• Vehicles move from YOUR selected depot")
        print(f"• {selected_customer_count} delivery points generated around your depot")
        print("• Real-time vehicle trails and status monitoring")
        print("• Dynamic delivery point generation based on customer count")
        print("\n🎯 Advanced Features:")
        print("• Depot & customer count reconfiguration without restarting app")
        print("• Automatic delivery point regeneration")
        print("• Real-time sound monitoring simulation")
        print("• Comprehensive vehicle status tracking")
        print("• Scalable customer-based delivery system (1-20 customers)")
        print("="*70)
    
    def on_dialog_closed():
        """Handle when depot dialog is closed without selection"""
        if not selected_depot:
            print("No depot selected. Exiting application.")
            app.quit()
    
    # Connect signals
    depot_dialog.depot_selected.connect(on_depot_selected)
    
    # Show the depot selection window
    depot_dialog.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()