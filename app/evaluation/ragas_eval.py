"""
RAGAS evaluation for Petco pet product recommendation RAG pipeline.
Measures: faithfulness, answer_relevancy, context_precision, context_recall.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from app.config import get_settings
from app.rag.chain import PetcoRAGChain

settings = get_settings()

EVAL_DATASET = [
    {
        "question": "What is the best dry food for a large breed adult dog?",
        "ground_truth": "Royal Canin Large Breed Adult Dry Dog Food is specifically formulated for large breeds over 55 lbs with joint support, tailored fibre blend, and 25% protein. Hill's Science Diet is also recommended.",
    },
    {
        "question": "My senior cat has kidney disease. What food should I feed her?",
        "ground_truth": "For cats with chronic kidney disease (CKD), use prescription diets with reduced phosphorus and restricted protein such as Royal Canin Renal Support or Hill's Prescription Diet k/d. Always consult your veterinarian.",
    },
    {
        "question": "What food helps with weight management for dogs?",
        "ground_truth": "Hill's Science Diet Adult Perfect Weight has been clinically proven to help 70% of dogs lose weight within 10 weeks. It has 30% protein, 10% fat, and 297 calories per cup.",
    },
    {
        "question": "My dog has food allergies. What should I feed him?",
        "ground_truth": "For dogs with food allergies, Royal Canin Hydrolyzed Protein HP or Hill's Prescription Diet z/d are recommended. These require an 8-12 week elimination trial. Both require veterinary guidance.",
    },
    {
        "question": "Best grain-free food for puppies?",
        "ground_truth": "Wellness CORE Grain-Free Puppy Formula provides 35% protein with DHA for brain development. It is AAFCO-approved for growth and uses deboned chicken as the primary protein.",
    },
    {
        "question": "What supplements help with dog joint problems?",
        "ground_truth": "Nutramax Cosequin Maximum Strength is the #1 vet-recommended joint supplement with glucosamine, chondroitin sulfate, and MSM. It is especially suitable for dogs with arthritis and hip dysplasia.",
    },
    {
        "question": "What toys are good for dog mental stimulation?",
        "ground_truth": "The KONG Classic Dog Toy is rated 4.9 stars with 45,000+ reviews. It can be stuffed with treats for mental stimulation and helps with anxiety relief and dental health.",
    },
    {
        "question": "What wet food should I give my senior cat?",
        "ground_truth": "Blue Buffalo Tastefuls Natural Senior Wet Cat Food with chicken provides immune support and kidney health. Fancy Feast Classic Senior Pate with salmon is another option at 1.29 per can.",
    },
    {
        "question": "My dog has separation anxiety. What products help?",
        "ground_truth": "Adaptil Calm Dog Collar releases pheromone signals that reduce anxiety caused by separation, thunderstorms, or travel. It is vet-recommended and suitable for adult dogs.",
    },
    {
        "question": "What food is good for diabetic cats?",
        "ground_truth": "Purina Pro Plan Veterinary Diets DM Dietetic Management wet food is formulated for blood glucose management in diabetic cats with high protein and low carbohydrates. It requires a veterinary prescription.",
    },
]


@dataclass
class RAGASReport:
    run_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0
    num_questions: int = 0
    per_question: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_at": self.run_at,
            "metrics": {
                "faithfulness": round(self.faithfulness, 4),
                "answer_relevancy": round(self.answer_relevancy, 4),
                "context_precision": round(self.context_precision, 4),
                "context_recall": round(self.context_recall, 4),
            },
            "num_questions": self.num_questions,
            "per_question": self.per_question,
        }


async def run_ragas_evaluation(
    questions: list[dict] | None = None,
    top_k: int = 5,
    pet_type: str | None = None,
) -> RAGASReport:
    eval_set = questions or EVAL_DATASET
    chain = PetcoRAGChain()

    queries, answers, contexts_list, ground_truths = [], [], [], []

    for item in eval_set:
        result = await chain.recommend(query=item["question"], top_k=top_k)
        queries.append(item["question"])
        answers.append(result.answer)
        contexts_list.append([s.get("name", "") + " " + s.get("brand", "") for s in result.sources])
        ground_truths.append(item["ground_truth"])

    dataset = Dataset.from_dict(
        {
            "question": queries,
            "answer": answers,
            "contexts": contexts_list,
            "ground_truth": ground_truths,
        }
    )

    result = evaluate(
        dataset,
        metrics=[answer_faithfulness, answer_relevancy, context_precision, context_recall],
    )

    report = RAGASReport(
        faithfulness=float(result["faithfulness"]),
        answer_relevancy=float(result["answer_relevancy"]),
        context_precision=float(result["context_precision"]),
        context_recall=float(result["context_recall"]),
        num_questions=len(eval_set),
    )

    for i, q in enumerate(queries):
        report.per_question.append(
            {
                "question": q,
                "answer_preview": answers[i][:200],
                "sources_count": len(contexts_list[i]),
            }
        )

    return report
