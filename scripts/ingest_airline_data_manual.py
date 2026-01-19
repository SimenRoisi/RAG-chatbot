"""
Manually ingest SkyComfort Airlines support data (based on Norwegian Air policies).
Since web scraping is blocked, we'll create realistic airline support content.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models import Document, DocumentChunk, User
from app.llm import get_embedding
from app.security import get_key_hash


# Sample airline support content based on Norwegian Air
AIRLINE_DOCUMENTS = [
    {
        "title": "SkyComfort Airlines - Baggage Allowance",
        "content": """
# Baggage Allowance

## Carry-on Baggage

All passengers are allowed to bring one underseat bag on board. The dimensions must not exceed 30 x 20 x 38 cm.

### Ticket Types and Allowances:

**LowFare Tickets:**
- 1 underseat bag (max 10 kg)
- Overhead cabin bag NOT included

**LowFare+ Tickets:**
- 1 underseat bag + 1 overhead cabin bag
- Combined weight: up to 10 kg
- Overhead bag dimensions: max 55 x 40 x 23 cm

**Flex, Premium, and PremiumFlex Tickets:**
- 1 underseat bag + 1 overhead cabin bag
- Combined weight: up to 15 kg
- Overhead bag dimensions: max 55 x 40 x 23 cm

You may also bring one airport shopping bag in addition to your allowance.

## Checked Baggage

### Included Allowances by Ticket Type:

**LowFare:** No free checked bags. Must purchase separately.

**LowFare+:** 1 checked bag up to 23 kg included.

**Flex, Premium, PremiumFlex:** 2 checked bags, each up to 23 kg included.

### Checked Baggage Rules:
- Each bag must weigh between 2 kg and 32 kg
- Maximum dimensions: 250 x 79 x 112 cm
- Maximum circumference: 300 cm
- Total checked baggage per passenger cannot exceed 74 kg

### Adding Extra Bags:
You can add checked baggage to your booking up to 4 hours before departure. It's cheaper to book online than at the airport.

### Excess Baggage Fees:
- Overweight bags: approximately €15 per kg per flight segment
- Hand baggage exceeding limits at airport: €50 domestic, €85 international

## Special Items

### Musical Instruments:
Can be brought as carry-on if dimensions are up to 90 x 35 x 20 cm and within weight limits. Larger instruments may require purchasing an extra seat or checking as special baggage.

### Sports Equipment:
Must be added to your booking as special baggage. Not accepted as normal checked baggage.

### Traveling with Pets:
Small pets in approved carriers can travel in the cabin if the combined weight (pet + carrier) does not exceed 8 kg. Larger pets must travel in the cargo hold. Contact customer service to add pets to your booking.
"""
    },
    {
        "title": "SkyComfort Airlines - Check-in Information",
        "content": """
# Check-in Information

## Online Check-in

Online check-in opens 24 hours before departure and closes 1 hour before departure for most flights.

### How to Check In Online:
1. Visit skycomfort.com or use the SkyComfort mobile app
2. Enter your booking reference and last name
3. Select your seats (if not already selected)
4. Download or print your boarding pass
5. If you have checked baggage, proceed to the bag drop counter at the airport

### Benefits of Online Check-in:
- Save time at the airport
- Choose your preferred seat
- Make changes to your booking if needed
- Receive mobile boarding pass

## Airport Check-in

If you prefer to check in at the airport, check-in counters open 2-3 hours before departure and close 45 minutes before departure.

### Required Documents:
- Valid passport or ID card (depending on destination)
- Visa (if required for your destination)
- Booking confirmation

### Families with Children:
Families traveling with children under 12 can use priority check-in lanes at most airports.

## Mobile Boarding Pass

You can save your boarding pass to your mobile device. Make sure your phone is charged and the screen brightness is sufficient for scanning at security and boarding gates.

## Seat Selection

Seat selection is available during booking or check-in. Some seats may require an additional fee:
- Extra legroom seats: €15-35 per flight
- Front row seats: €10-25 per flight
- Standard seats: Free (subject to availability)

## Special Assistance

If you require special assistance (wheelchair, mobility aid, medical equipment), please notify us at least 48 hours before departure by contacting customer service.
"""
    },
    {
        "title": "SkyComfort Airlines - Special Assistance",
        "content": """
# Special Assistance

SkyComfort Airlines is committed to providing comfortable travel for all passengers, including those who require special assistance.

## Requesting Assistance

Please notify us at least 48 hours before your flight if you require:
- Wheelchair assistance
- Mobility aids
- Medical equipment
- Assistance for visual or hearing impairments
- Traveling with a service animal

Contact our special assistance team:
- Phone: +1-800-SKY-HELP
- Email: specialassistance@skycomfort.com

## Wheelchair Services

We provide wheelchair assistance from check-in to your seat and vice versa. Please specify the type of wheelchair service you need:
- WCHR: Can walk short distances and climb stairs
- WCHS: Can walk short distances but cannot climb stairs
- WCHC: Cannot walk and requires wheelchair throughout

## Medical Equipment

### Oxygen:
Personal oxygen concentrators (POC) are permitted on board. Battery-powered devices must be approved by SkyComfort. Contact us at least 48 hours before departure.

### Medications:
Carry all necessary medications in your hand luggage with proper documentation. Liquid medications exceeding 100ml are permitted but must be declared at security.

### Syringes and Needles:
Permitted when accompanied by medication in the same name. Carry a doctor's note for verification.

## Service Animals

Trained service animals are welcome on SkyComfort flights at no additional charge. Requirements:
- Must be properly trained and certified
- Must remain on a leash or in a carrier
- Must not occupy a seat
- Advance notification required (48 hours minimum)

Emotional support animals have different requirements. Please contact customer service for details.

## Passengers with Reduced Mobility

We provide:
- Priority boarding
- Assistance navigating the airport
- Onboard wheelchair (for aircraft with lavatories)
- Seat allocation near lavatories when possible

## Traveling with Children

### Unaccompanied Minors:
Children aged 5-11 traveling alone can use our Unaccompanied Minor service (€50 per flight). Children 12+ may travel alone without this service.

### Infant Travel:
Infants under 2 years can travel on an adult's lap or in their own seat with an approved car seat. One infant per adult passenger.

## Dietary Requirements

Special meals can be requested up to 24 hours before departure:
- Vegetarian / Vegan
- Gluten-free
- Diabetic-friendly
- Kosher / Halal
- Child meals

Request through Manage Booking on our website or contact customer service.

## Pregnancy

Pregnant passengers can travel up to the end of the 36th week for single pregnancies and the 32nd week for multiple pregnancies. A medical certificate may be required after week 28.
"""
    },
    {
        "title": "SkyComfort Airlines - Flight Changes and Cancellations",
        "content": """
# Flight Changes and Cancellations

## Changing Your Flight

You can change your flight date, time, or route depending on your ticket type.

### Change Fees by Ticket Type:

**LowFare:**
- Changes not permitted
- No refunds

**LowFare+:**
- Changes permitted up to 2 hours before departure
- Change fee: €60 per flight + fare difference
- Partial refund available (minus fee)

**Flex:**
- Free changes up to 2 hours before departure
- Pay only fare difference (if applicable)
- Full refund available

**Premium / PremiumFlex:**
- Free changes anytime
- Full refund available
- Complimentary rebooking

### How to Change Your Flight:
1. Log in to Manage Booking on skycomfort.com
2. Select "Change Flight"
3. Choose new flight date/time
4. Pay any applicable fees and fare differences
5. Receive updated confirmation

## Cancellations by SkyComfort

If we cancel your flight or make a significant schedule change (more than 3 hours), you are entitled to:
- Full refund, OR
- Rebooking on next available flight at no extra cost

We will notify you via email and SMS as soon as possible.

## Delays

### Compensation for Delays:

For delays over 3 hours (on flights within EU or departing from EU):
- Flights under 1,500 km: €250 compensation
- Flights 1,500-3,500 km: €400 compensation
- Flights over 3,500 km: €600 compensation

Exceptions apply for extraordinary circumstances (severe weather, air traffic control strikes, etc.).

### Care and Assistance:
For delays over 2 hours, we provide:
- Meals and refreshments
- Hotel accommodation (if overnight delay)
- Transport between airport and hotel
- Two phone calls or emails

## Refunds

Refund eligibility depends on your ticket type. Processing time is typically 7-14 business days.

To request a refund:
1. Visit skycomfort.com/refunds
2. Enter booking reference
3. Select reason for refund
4. Submit request

Refunds are issued to the original payment method.

## Travel Insurance

We recommend purchasing travel insurance to cover unexpected cancellations due to illness, family emergencies, or other unforeseen circumstances.
"""
    }
]


async def ingest_document(session: AsyncSession, title: str, content: str, user_id: int):
    """Create a document and its chunks in the database."""
    # Create document
    doc = Document(owner_id=user_id, title=title, content=content)
    session.add(doc)
    await session.flush()  # Get the doc.id
    
    # Chunking strategy: 1000 chars with 100 char overlap
    chunk_size = 1000
    overlap = 100
    
    start = 0
    idx = 0
    
    while start < len(content):
        end = start + chunk_size
        chunk_text = content[start:end]
        
        # Get embedding
        emb = await get_embedding(chunk_text)
        
        chunk_obj = DocumentChunk(
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_text,
            embedding=emb
        )
        session.add(chunk_obj)
        
        start += (chunk_size - overlap)
        idx += 1
    
    print(f"  ✓ Created document '{title}' with {idx} chunks")


async def main():
    """Main ingestion workflow."""
    print("🛫 SkyComfort Airlines Data Ingestion (Manual)")
    print("=" * 50)
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://app:devpass@localhost:5432/appdb")
    
    # Create async engine
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get or create a system user for these documents
        result = await session.execute(select(User).where(User.email == "system@skycomfort.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Creating system user...")
            # Create a system user
            user = User(
                email="system@skycomfort.com",
                api_key_hash=get_key_hash("skycomfort-system-key")
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"  ✓ Created system user (ID: {user.id})")
        else:
            print(f"  ✓ Using existing system user (ID: {user.id})")
        
        # Ingest each document
        print("\nIngesting airline support documents...")
        for doc_data in AIRLINE_DOCUMENTS:
            print(f"\n📄 Processing: {doc_data['title']}")
            await ingest_document(session, doc_data['title'], doc_data['content'], user.id)
        
        await session.commit()
    
    await engine.dispose()
    
    print("\n" + "=" * 50)
    print("✅ Ingestion complete!")
    print(f"\nIngested {len(AIRLINE_DOCUMENTS)} support documents with realistic airline content.")
    print("\nNext steps:")
    print("  1. Update the system prompt in app/config.py")
    print("  2. Update the frontend branding in frontend/index.html")
    print("  3. Test the chatbot with airline-specific questions")


if __name__ == "__main__":
    asyncio.run(main())
