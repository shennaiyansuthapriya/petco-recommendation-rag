"""
System and user prompt templates for Petco pet product recommendation RAG.
"""

SYSTEM_PROMPT = """You are a knowledgeable and caring pet health advisor for Petco, with expertise in \
pet nutrition, health, and care across dogs, cats, fish, birds, reptiles, and small animals.

Your role is to provide personalised product recommendations that prioritise the pet's health and well-being, \
considering their species, age, health conditions, and dietary needs.

Guidelines:
- Always cite product name, brand, key nutritional specs (protein %, fat %, calories), and price
- For health-sensitive queries (allergies, kidney disease, joint issues), recommend vet-approved products first
- Distinguish between life stages: puppy/kitten, adult, senior
- Include feeding guidelines where relevant
- Warn when a query involves a health condition that warrants veterinary consultation
- Format product citations as [Product Name — Brand] with key specs
- Reference care guide content when it adds important context
- Never diagnose medical conditions — recommend vet visits when appropriate
"""

USER_PROMPT_TEMPLATE = """Based on the following product and care guide information, provide personalised \
pet product recommendations.

PRODUCT & CARE GUIDE CONTEXT:
{context}

CUSTOMER QUESTION:
{query}

{filter_context}

Provide specific product recommendations with nutritional details and health reasoning. \
Flag any products that are vet-recommended or require a prescription."""


def build_context(results: list[dict]) -> str:
    lines: list[str] = []
    for i, r in enumerate(results, 1):
        payload = r.get("metadata", {})
        text = r.get("text", "")
        source = r.get("source", "product")
        name = payload.get("name", "Unknown")
        brand = payload.get("brand", "")
        category = payload.get("category", "")
        pet_type = payload.get("pet_type", "")
        life_stage = payload.get("life_stage", "")
        protein = payload.get("protein_pct")
        fat = payload.get("fat_pct")
        calories = payload.get("calories_per_cup")
        price = payload.get("price_usd")
        vet_rec = payload.get("vet_recommended", False)
        grain_free = payload.get("grain_free", False)
        cohere_score = r.get("cohere_relevance_score", r.get("score", 0))

        if source == "product":
            spec_parts = []
            if protein:
                spec_parts.append(f"Protein: {protein}%")
            if fat:
                spec_parts.append(f"Fat: {fat}%")
            if calories:
                spec_parts.append(f"{calories} kcal/cup")
            if price:
                spec_parts.append(f"${price:.2f}")
            if vet_rec:
                spec_parts.append("Vet Recommended")
            if grain_free:
                spec_parts.append("Grain-Free")

            spec_str = " | ".join(spec_parts)
            lines.append(
                f"[{i}] {name} — {brand}\n"
                f"    Type: {pet_type} | {category} | {life_stage}\n"
                f"    Specs: {spec_str}\n"
                f"    {text}"
            )
        else:
            topic = payload.get("topic", "care")
            lines.append(f"[{i}] CARE GUIDE ({pet_type} — {topic})\n    {text}")

    return "\n\n".join(lines)


def build_filter_context(pet_type: str | None, health_condition: str | None) -> str:
    parts = []
    if pet_type:
        parts.append(f"Pet type: {pet_type}")
    if health_condition:
        parts.append(f"Health condition: {health_condition}")
    return ("Active filters: " + ", ".join(parts)) if parts else ""
