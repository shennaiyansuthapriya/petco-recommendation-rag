"""
Seed 20 realistic pet products + 5 care guides for Petco RAG demo.
Run: python scripts/seed_sample_data.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models.product import LifeStage, PetCareGuide, PetProduct, PetType, ProductCategory

settings = get_settings()

SAMPLE_PRODUCTS = [
    {
        "sku": "RC-ADU-LB-15",
        "name": "Royal Canin Large Breed Adult Dry Dog Food",
        "brand": "Royal Canin",
        "pet_type": PetType.DOG,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.ADULT,
        "description": "Precisely formulated for large breeds over 55 lbs. Tailored fibre blend helps reduce stool odour and volume.",
        "health_benefits": "Joint support, digestive health, skin and coat care",
        "ingredients": "Chicken by-product meal, brown rice, oat groats, barley, soybean meal",
        "guaranteed_analysis": "Protein 25%, Fat 15%, Fiber 5%, Moisture 10%",
        "feeding_guidelines": "55-88 lbs: 3 to 3⅝ cups per day, divided into 2 meals",
        "protein_pct": 25.0,
        "fat_pct": 15.0,
        "fiber_pct": 5.0,
        "calories_per_cup": 364,
        "primary_protein": "chicken",
        "suitable_for_conditions": ["joint_support", "weight_management"],
        "vet_recommended": True,
        "price_usd": 79.99,
        "rating": 4.7,
        "review_count": 4321,
    },
    {
        "sku": "HC-ADU-WGF-12",
        "name": "Hill's Science Diet Adult Perfect Weight Dry Dog Food",
        "brand": "Hill's Science Diet",
        "pet_type": PetType.DOG,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.ADULT,
        "description": "Clinically proven weight management food helping 70% of dogs lose weight within 10 weeks.",
        "health_benefits": "Weight control, lean muscle maintenance",
        "ingredients": "Chicken, cracked pearled barley, peas, whole grain wheat, whole grain sorghum",
        "protein_pct": 30.0,
        "fat_pct": 10.0,
        "fiber_pct": 8.0,
        "calories_per_cup": 297,
        "primary_protein": "chicken",
        "grain_free": False,
        "suitable_for_conditions": ["obesity", "weight_management"],
        "vet_recommended": True,
        "price_usd": 69.99,
        "rating": 4.6,
        "review_count": 3456,
    },
    {
        "sku": "BN-SEN-GF-15",
        "name": "Purina Pro Plan Veterinary Diets NF Kidney Function Dog Food",
        "brand": "Purina Pro Plan",
        "pet_type": PetType.DOG,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.ADULT,
        "description": "Low phosphorus, restricted protein formula to support dogs with kidney disease.",
        "health_benefits": "Kidney function support, low phosphorus, controlled protein",
        "protein_pct": 14.0,
        "fat_pct": 18.0,
        "fiber_pct": 3.0,
        "calories_per_cup": 412,
        "primary_protein": "chicken",
        "suitable_for_conditions": ["kidney_disease", "chronic_renal_failure"],
        "vet_recommended": True,
        "prescription_required": True,
        "price_usd": 89.99,
        "rating": 4.8,
        "review_count": 1234,
    },
    {
        "sku": "WB-PUP-GF-5",
        "name": "Wellness CORE Grain-Free Puppy Formula",
        "brand": "Wellness",
        "pet_type": PetType.DOG,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.PUPPY_KITTEN,
        "description": "High-protein, grain-free puppy food with DHA for brain development.",
        "health_benefits": "Brain development, immune support, bone and joint health",
        "ingredients": "Deboned chicken, chicken meal, lentils, peas, tomato pomace",
        "protein_pct": 35.0,
        "fat_pct": 18.0,
        "fiber_pct": 4.0,
        "calories_per_cup": 421,
        "primary_protein": "chicken",
        "grain_free": True,
        "price_usd": 64.99,
        "rating": 4.7,
        "review_count": 2543,
    },
    {
        "sku": "RC-CAT-ADU-4",
        "name": "Royal Canin Feline Health Nutrition Indoor Adult Dry Cat Food",
        "brand": "Royal Canin",
        "pet_type": PetType.CAT,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.ADULT,
        "description": "Formulated for indoor cats to support healthy weight and reduce hairball formation.",
        "health_benefits": "Weight management, hairball control, urinary tract health",
        "protein_pct": 33.0,
        "fat_pct": 12.0,
        "fiber_pct": 7.5,
        "calories_per_cup": 343,
        "primary_protein": "chicken",
        "price_usd": 49.99,
        "rating": 4.6,
        "review_count": 3876,
    },
    {
        "sku": "HC-SEN-JNT-6",
        "name": "Hill's Science Diet Senior 7+ Healthy Mobility Cat Food",
        "brand": "Hill's Science Diet",
        "pet_type": PetType.CAT,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.SENIOR,
        "description": "Clinically proven to improve mobility in cats with joint issues. Natural fish oil for omega-3s.",
        "health_benefits": "Joint mobility, skin and coat, cognitive function",
        "protein_pct": 32.0,
        "fat_pct": 15.0,
        "calories_per_cup": 361,
        "primary_protein": "salmon",
        "suitable_for_conditions": ["joint_issues", "arthritis"],
        "vet_recommended": True,
        "price_usd": 44.99,
        "rating": 4.5,
        "review_count": 1876,
    },
    {
        "sku": "ZW-DOG-FLOSS",
        "name": "Zuke's Natural Mini Treats Dog Treats",
        "brand": "Zuke's",
        "pet_type": PetType.DOG,
        "category": ProductCategory.TREATS,
        "life_stage": LifeStage.ADULT,
        "description": "Soft, pea-sized training treats made with real chicken and healthy cherries. 3.5 calories each.",
        "health_benefits": "Low calorie training reward, wheat-free, no artificial flavors",
        "primary_protein": "chicken",
        "grain_free": True,
        "price_usd": 8.99,
        "rating": 4.8,
        "review_count": 12543,
    },
    {
        "sku": "VET-DOG-JNT",
        "name": "Nutramax Cosequin Maximum Strength Joint Health Supplement",
        "brand": "Nutramax",
        "pet_type": PetType.DOG,
        "category": ProductCategory.SUPPLEMENTS,
        "life_stage": LifeStage.ADULT,
        "description": "Veterinarian-recommended joint health supplement with glucosamine, chondroitin, and MSM.",
        "health_benefits": "Joint cartilage support, mobility improvement, #1 vet recommended joint supplement",
        "suitable_for_conditions": ["joint_issues", "arthritis", "hip_dysplasia"],
        "vet_recommended": True,
        "price_usd": 39.99,
        "rating": 4.7,
        "review_count": 8765,
    },
    {
        "sku": "KONG-CLASSIC-L",
        "name": "KONG Classic Dog Toy Large",
        "brand": "KONG",
        "pet_type": PetType.DOG,
        "category": ProductCategory.TOYS,
        "life_stage": LifeStage.ADULT,
        "description": "Durable natural rubber toy for stuffing with treats. Unpredictable bounce for extended play.",
        "health_benefits": "Mental stimulation, anxiety relief, dental health",
        "price_usd": 14.99,
        "rating": 4.9,
        "review_count": 45321,
    },
    {
        "sku": "FLR-CAT-SEN-WET",
        "name": "Fancy Feast Classic Senior Pate Wet Cat Food",
        "brand": "Fancy Feast",
        "pet_type": PetType.CAT,
        "category": ProductCategory.FOOD_WET,
        "life_stage": LifeStage.SENIOR,
        "description": "Tender pate with real salmon and shrimp, formulated with added vitamins for senior cats.",
        "health_benefits": "Urinary tract health, hydration, easy digestion for seniors",
        "primary_protein": "salmon",
        "protein_pct": 11.0,
        "fat_pct": 5.0,
        "price_usd": 1.29,
        "rating": 4.6,
        "review_count": 9876,
    },
    {
        "sku": "AQ-TETRA-TANK",
        "name": "Tetra 20 Gallon Complete Aquarium Kit",
        "brand": "Tetra",
        "pet_type": PetType.FISH,
        "category": ProductCategory.AQUATICS,
        "description": "Complete aquarium starter kit with LED lighting, Whisper filtration, and hinged hood.",
        "health_benefits": "Complete ecosystem for tropical fish health",
        "price_usd": 149.99,
        "rating": 4.4,
        "review_count": 2341,
    },
    {
        "sku": "FRISCO-BED-XL",
        "name": "Frisco Plush Orthopedic Dog Bed Extra Large",
        "brand": "Frisco",
        "pet_type": PetType.DOG,
        "category": ProductCategory.BEDS,
        "life_stage": LifeStage.SENIOR,
        "description": "Supportive memory foam orthopedic dog bed ideal for senior dogs with joint issues.",
        "health_benefits": "Joint pain relief, pressure point support, therapeutic memory foam",
        "suitable_for_conditions": ["joint_issues", "arthritis"],
        "price_usd": 89.99,
        "rating": 4.5,
        "review_count": 3456,
    },
    {
        "sku": "BW-CAT-SCRATCHER",
        "name": "Bergan Turbo Scratcher Cat Toy",
        "brand": "Bergan",
        "pet_type": PetType.CAT,
        "category": ProductCategory.TOYS,
        "life_stage": LifeStage.ALL_STAGES,
        "description": "Two-in-one scratcher and toy with a spinning ball track to satisfy hunting instincts.",
        "price_usd": 19.99,
        "rating": 4.6,
        "review_count": 7654,
    },
    {
        "sku": "FURMINATOR-DOG-L",
        "name": "FURminator deShedding Tool for Large Dogs — Long Hair",
        "brand": "FURminator",
        "pet_type": PetType.DOG,
        "category": ProductCategory.GROOMING,
        "life_stage": LifeStage.ALL_STAGES,
        "description": "Professional de-shedding tool that reduces shedding by up to 90% for long-haired large dogs.",
        "price_usd": 54.99,
        "rating": 4.8,
        "review_count": 23456,
    },
    {
        "sku": "PETSTAGES-PUPPY",
        "name": "Nylabone Puppy Starter Chew Toy Kit",
        "brand": "Nylabone",
        "pet_type": PetType.DOG,
        "category": ProductCategory.TOYS,
        "life_stage": LifeStage.PUPPY_KITTEN,
        "description": "Puppy teething kit with 3 nylon chews in different shapes and textures for teething relief.",
        "health_benefits": "Teething relief, dental health, safe for puppies under 25 lbs",
        "price_usd": 12.99,
        "rating": 4.5,
        "review_count": 4321,
    },
    {
        "sku": "PETMD-DIABETES",
        "name": "Purina Pro Plan Veterinary Diets DM Dietetic Management Cat Food",
        "brand": "Purina Pro Plan",
        "pet_type": PetType.CAT,
        "category": ProductCategory.FOOD_WET,
        "life_stage": LifeStage.ADULT,
        "description": "High protein, low carbohydrate wet food formulated to support blood glucose management in diabetic cats.",
        "health_benefits": "Blood glucose management, high protein for muscle maintenance",
        "protein_pct": 14.0,
        "fat_pct": 6.0,
        "primary_protein": "chicken",
        "suitable_for_conditions": ["diabetes", "weight_management"],
        "vet_recommended": True,
        "prescription_required": True,
        "price_usd": 3.49,
        "rating": 4.7,
        "review_count": 1234,
    },
    {
        "sku": "ZUPREEM-PARROT",
        "name": "ZuPreem Natural Large Parrot and Conure Pelleted Bird Food",
        "brand": "ZuPreem",
        "pet_type": PetType.BIRD,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.ALL_STAGES,
        "description": "Nutritionally complete pelleted diet for parrots with natural fruit flavors.",
        "health_benefits": "Complete nutrition, natural vitamin supplement, bright plumage support",
        "price_usd": 24.99,
        "rating": 4.6,
        "review_count": 876,
    },
    {
        "sku": "RC-HYPO-DOG",
        "name": "Royal Canin Hydrolyzed Protein Adult HP Dog Food",
        "brand": "Royal Canin",
        "pet_type": PetType.DOG,
        "category": ProductCategory.FOOD_DRY,
        "life_stage": LifeStage.ADULT,
        "description": "Hydrolyzed soy protein diet for dogs with severe food allergies and sensitivities.",
        "health_benefits": "Allergy management, skin health, digestive support",
        "protein_pct": 16.6,
        "fat_pct": 20.0,
        "fiber_pct": 3.4,
        "primary_protein": "hydrolyzed_soy",
        "suitable_for_conditions": ["food_allergies", "skin_conditions", "ibd"],
        "vet_recommended": True,
        "prescription_required": True,
        "price_usd": 99.99,
        "rating": 4.7,
        "review_count": 987,
    },
    {
        "sku": "ADAPTIL-COLLAR",
        "name": "Adaptil Calm Dog Collar",
        "brand": "Adaptil",
        "pet_type": PetType.DOG,
        "category": ProductCategory.HEALTH_WELLNESS,
        "life_stage": LifeStage.ADULT,
        "description": "Pheromone collar that releases calming signals to reduce anxiety in dogs during stressful situations.",
        "health_benefits": "Anxiety relief, stress reduction for travel, thunderstorms, separation",
        "suitable_for_conditions": ["anxiety", "separation_anxiety"],
        "vet_recommended": True,
        "price_usd": 27.99,
        "rating": 4.3,
        "review_count": 5432,
    },
    {
        "sku": "WHISKAS-CAT-WET",
        "name": "Blue Buffalo Tastefuls Natural Senior Wet Cat Food",
        "brand": "Blue Buffalo",
        "pet_type": PetType.CAT,
        "category": ProductCategory.FOOD_WET,
        "life_stage": LifeStage.SENIOR,
        "description": "Natural senior cat food with real chicken and LifeSource Bits for immune support.",
        "health_benefits": "Immune system support, kidney health, senior joint care",
        "protein_pct": 9.0,
        "fat_pct": 5.5,
        "primary_protein": "chicken",
        "price_usd": 2.19,
        "rating": 4.5,
        "review_count": 6789,
    },
]

SAMPLE_GUIDES = [
    {
        "title": "Nutrition Guide for Senior Dogs with Joint Issues",
        "pet_type": PetType.DOG,
        "topic": "nutrition",
        "content": """Senior dogs (7+ years) with joint issues have specific nutritional needs.
Key nutrients include:
- Omega-3 fatty acids (EPA and DHA) from fish oil to reduce joint inflammation
- Glucosamine and chondroitin sulfate to support cartilage health
- Controlled calorie intake to maintain healthy weight (extra weight stresses joints)
- High-quality, easily digestible protein (25-30%) to maintain muscle mass
- Antioxidants (vitamins C and E) to reduce oxidative stress

Recommended brands: Hill's Science Diet Healthy Mobility, Royal Canin Joint Care,
Purina Pro Plan Bright Mind. Always consult a veterinarian before changing senior diet.

Signs your dog may need a joint-supportive diet:
- Difficulty rising after rest
- Reluctance to climb stairs
- Decreased activity level
- Limping or favouring one leg
""",
    },
    {
        "title": "Managing Kidney Disease in Cats — Diet and Care",
        "pet_type": PetType.CAT,
        "topic": "health",
        "content": """Chronic kidney disease (CKD) is common in cats, especially those over 7 years old.
Diet is the cornerstone of management.

Dietary priorities for cats with kidney disease:
- REDUCED PHOSPHORUS: Phosphorus is the most critical factor — lower is better
- RESTRICTED PROTEIN: But not too low — protein quality matters more than quantity
- INCREASED MOISTURE: Wet food or water fountains to support kidney filtration
- OMEGA-3 FATTY ACIDS: Help slow progression of kidney disease

Prescription diets to discuss with your vet:
- Royal Canin Renal Support
- Hill's Prescription Diet k/d
- Purina Pro Plan Veterinary Diets NF

Regular monitoring: Bloodwork every 3-6 months to check creatinine, BUN, and phosphorus levels.
IMPORTANT: Never switch to a kidney diet without veterinary guidance.
""",
    },
    {
        "title": "Puppy Nutrition: First Year Feeding Guide",
        "pet_type": PetType.DOG,
        "topic": "nutrition",
        "content": """The first year of a puppy's life is critical for establishing healthy dietary patterns.

Feeding schedule by age:
- 8-12 weeks: 4 meals per day
- 3-6 months: 3 meals per day
- 6-12 months: 2 meals per day (large breeds: continue 3 meals until 12-18 months)

What to look for in puppy food:
- AAFCO statement: "complete and nutritional for growth"
- DHA for brain and eye development
- Calcium-to-phosphorus ratio of 1.2:1
- At least 22% protein, 8% fat
- Large breed puppies need lower calcium density to prevent skeletal issues

Red flags in puppy food:
- Corn, soy, or wheat as primary ingredients
- Artificial colors and flavors
- No specific meat source listed (just "meat")

Recommended: Look for breed-size-specific formulas for large or small breeds.
""",
    },
    {
        "title": "Food Allergies in Dogs — Identification and Management",
        "pet_type": PetType.DOG,
        "topic": "health",
        "content": """Food allergies affect approximately 10% of all dog allergies.
The most common allergens are: beef, dairy, wheat, egg, chicken, lamb, soy, pork.

Signs of food allergy:
- Itchy skin (especially ears, paws, belly, groin)
- Recurring ear infections
- Gastrointestinal issues (vomiting, diarrhea, excessive gas)
- Skin rashes or hives

Diagnosis via elimination diet:
1. Feed a novel protein or hydrolyzed protein diet exclusively for 8-12 weeks
2. No treats, flavored medications, or table scraps during trial
3. If symptoms resolve, gradually reintroduce original diet components to identify trigger

Recommended prescription diets for elimination trial:
- Royal Canin Hydrolyzed Protein HP
- Hill's Prescription Diet z/d
- Purina Pro Plan Veterinary Diets HA Hydrolyzed

Always work with your veterinarian for proper allergy diagnosis.
""",
    },
    {
        "title": "Indoor Cat Health: Weight Management and Enrichment",
        "pet_type": PetType.CAT,
        "topic": "health",
        "content": """Over 60% of indoor cats are overweight or obese. Excess weight leads to diabetes,
joint disease, and shortened lifespan.

Weight management strategies:
- Measure food precisely — most cats need only 1/4 to 1/3 cup of dry food per day
- Use puzzle feeders to slow eating and increase mental stimulation
- Choose lower-calorie indoor formulas (300-350 kcal/cup rather than 400+)
- Consider wet food — higher moisture, lower calorie density
- Interactive play: 2x 10-minute sessions daily with wand toys

Ideal body condition score (BCS): 4-5 on a 9-point scale
- You should feel ribs easily but not see them
- A slight waist visible from above

Safe weight loss rate: 0.5-2% of body weight per week (faster loss risks hepatic lipidosis).

Enrichment ideas for indoor cats:
- Window perches with bird feeders outside
- Cat trees and vertical space
- Puzzle toys with kibble
- Rotating toy selection to maintain novelty
""",
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        for data in SAMPLE_PRODUCTS:
            result = await session.execute(select(PetProduct).where(PetProduct.sku == data["sku"]))
            if result.scalar_one_or_none():
                print(f"  Exists: {data['name']}")
                continue
            product = PetProduct(**data)
            session.add(product)
            print(f"  Added product: {data['name']} [{data['sku']}]")

        for data in SAMPLE_GUIDES:
            result = await session.execute(
                select(PetCareGuide).where(PetCareGuide.title == data["title"])
            )
            if result.scalar_one_or_none():
                print(f"  Exists guide: {data['title']}")
                continue
            guide = PetCareGuide(**data)
            session.add(guide)
            print(f"  Added guide: {data['title']}")

        await session.commit()

    print(f"\nSeeded {len(SAMPLE_PRODUCTS)} products and {len(SAMPLE_GUIDES)} care guides.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
