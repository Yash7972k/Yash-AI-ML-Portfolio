"""
Database initialization script - creates demo data
Run this after database setup to populate demo data
"""
from utils.database import SessionLocal, User, CollectionPoint, EWasteSubmission, init_db
from utils.auth import hash_pwd
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create demo users, collection points, and submissions"""
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    
    try:
        # ==================== CREATE DEMO USERS ====================
        
        demo_users = [
            {
                "email": "demo@ewaste.com",
                "phone": "+91-9876543210",
                "name": "Demo User",
                "address": "123, MG Road, Pune",
                "password": "demo123",
                "is_admin": False
            },
            {
                "email": "admin@ewaste.com",
                "phone": "+91-9876543211",
                "name": "Admin User",
                "address": "456, FC Road, Pune",
                "password": "admin123",
                "is_admin": True
            }
        ]
        
        for user_data in demo_users:
            # Check if user already exists
            existing = db.query(User).filter_by(email=user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    phone=user_data["phone"],
                    name=user_data["name"],
                    address=user_data["address"],
                    password_hash=hash_pwd(user_data["password"]),
                    is_admin=user_data["is_admin"],
                    is_active=True
                )
                db.add(user)
                print(f"✅ Created user: {user_data['email']}")
            else:
                print(f"⏭️ User already exists: {user_data['email']}")
        
        db.commit()
        
        # ==================== CREATE COLLECTION POINTS ====================
        
        collection_points = [
            {
                "name": "Green Recycle Hub",
                "address": "12 MG Road, Pune",
                "city": "Pune",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "capacity": 500,
                "phone": "+91-9876543210",
                "status": "Active"
            },
            {
                "name": "EcoWaste Center",
                "address": "45 FC Road, Pune",
                "city": "Pune",
                "latitude": 18.5314,
                "longitude": 73.8446,
                "capacity": 300,
                "phone": "+91-9876543211",
                "status": "Active"
            },
            {
                "name": "TechRecycle Point",
                "address": "78 Baner Road, Pune",
                "city": "Pune",
                "latitude": 18.5590,
                "longitude": 73.7868,
                "capacity": 400,
                "phone": "+91-9876543212",
                "status": "Active"
            },
            {
                "name": "CleanEarth Depot",
                "address": "23 Kothrud, Pune",
                "city": "Pune",
                "latitude": 18.5074,
                "longitude": 73.8077,
                "capacity": 200,
                "phone": "+91-9876543213",
                "status": "Full"
            },
            {
                "name": "RecyclePro Center",
                "address": "56 Hadapsar, Pune",
                "city": "Pune",
                "latitude": 18.5018,
                "longitude": 73.9260,
                "capacity": 600,
                "phone": "+91-9876543214",
                "status": "Active"
            }
        ]
        
        for point_data in collection_points:
            existing = db.query(CollectionPoint).filter_by(name=point_data["name"]).first()
            if not existing:
                point = CollectionPoint(**point_data)
                db.add(point)
                print(f"✅ Created collection point: {point_data['name']}")
            else:
                print(f"⏭️ Collection point already exists: {point_data['name']}")
        
        db.commit()
        
        # ==================== CREATE DEMO SUBMISSIONS ====================
        
        item_types = ["Mobile Phone", "Laptop", "Desktop Computer", "Television", 
                     "Refrigerator", "Washing Machine", "Air Conditioner", "Battery"]
        
        demo_submissions = [
            {
                "name": "Rajesh Kumar",
                "phone": "+91-9123456789",
                "email": "rajesh@example.com",
                "address": "123 Street, Pune",
                "item_type": "Laptop",
                "quantity": 1,
                "condition": "Broken/Non-functional",
                "status": "Pending",
                "priority": "High",
                "hazard_level": "High",
                "co2_saved": 75.5,
                "weight_kg": 2.5,
                "recycle_value": 45.0,
                "collection_point": "Green Recycle Hub",
                "date": datetime.utcnow() - timedelta(days=5)
            },
            {
                "name": "Priya Singh",
                "phone": "+91-8987654321",
                "email": "priya@example.com",
                "address": "456 Avenue, Pune",
                "item_type": "Mobile Phone",
                "quantity": 3,
                "condition": "Working",
                "status": "Collected",
                "priority": "High",
                "hazard_level": "High",
                "co2_saved": 210.0,
                "weight_kg": 0.6,
                "recycle_value": 45.0,
                "collection_point": "EcoWaste Center",
                "date": datetime.utcnow() - timedelta(days=3)
            },
            {
                "name": "Amit Patel",
                "phone": "+91-7654321098",
                "email": "amit@example.com",
                "address": "789 Road, Pune",
                "item_type": "Printer",
                "quantity": 1,
                "condition": "Partially Working",
                "status": "Recycled",
                "priority": "Medium",
                "hazard_level": "Medium",
                "co2_saved": 45.0,
                "weight_kg": 5.0,
                "recycle_value": 10.0,
                "collection_point": "TechRecycle Point",
                "date": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        for sub_data in demo_submissions:
            existing = db.query(EWasteSubmission).filter_by(
                phone=sub_data["phone"],
                item_type=sub_data["item_type"]
            ).first()
            if not existing:
                submission = EWasteSubmission(**sub_data)
                db.add(submission)
                print(f"✅ Created submission: {submission.id}")
            else:
                print(f"⏭️ Submission already exists for {sub_data['phone']}")
        
        db.commit()
        
        print("\n" + "="*50)
        print("✅ Demo data created successfully!")
        print("="*50)
        print("\n🔐 Demo Credentials:")
        print("  Regular User:")
        print("    Email: demo@ewaste.com")
        print("    Password: demo123")
        print("\n  Admin User:")
        print("    Email: admin@ewaste.com")
        print("    Password: admin123")
        print("\n🚀 Run: streamlit run app_improved.py")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
