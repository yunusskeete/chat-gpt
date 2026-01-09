"""Initialize database with tables and sample PT preferences"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, SessionLocal
from app.models import PTPreferences
from app.config import get_settings


def seed_pt_preferences():
    """Seed database with sample PT preferences from environment"""
    settings = get_settings()
    db = SessionLocal()

    try:
        # Check if PT already exists
        existing_pt = db.query(PTPreferences).filter_by(id=1).first()
        if existing_pt:
            print(f"PT preferences already exist for: {existing_pt.name}")
            return

        # Create PT from settings (which reads from env vars or pt_defaults.py)
        pt = PTPreferences(
            id=1,
            name=settings.pt_name,
            target_goals=settings.pt_target_goals,
            age_range=settings.pt_age_range,
            preferred_location=settings.pt_location,
            min_budget=settings.pt_min_budget,
            required_commitment=settings.pt_required_commitment,
            specialty=settings.pt_specialty,
            # Extended fields (will populate from pt_defaults.py by default)
            bio=settings.pt_bio,
            years_experience=settings.pt_years_experience,
            certifications=settings.pt_certifications,
            additional_info=settings.pt_additional_info,
        )

        db.add(pt)
        db.commit()
        print(f"Created PT preferences for: {pt.name}")
        print(f"  Specialty: {pt.specialty}")
        print(f"  Target goals: {pt.target_goals}")
        print(f"  Age range: {pt.age_range}")
        print(f"  Location: {pt.preferred_location}")
        print(f"  Min budget: £{pt.min_budget}/month")
        print(f"  Required commitment: {pt.required_commitment}x/week")

    except Exception as e:
        print(f"Error seeding PT preferences: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database tables created successfully!")

    print("\nSeeding PT preferences...")
    seed_pt_preferences()
    print("\nDatabase initialization complete!")
