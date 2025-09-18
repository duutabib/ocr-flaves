from typing import Dict, Any, List, Optional
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class ModelScore:
    """Represents a model's score for a given document."""
    model_name: str
    score: float
    confidence: float
    response: Dict[str, Any]
    timestamp: str
    metrics: Dict[str, float]  # Individual scoring metrics

class ModelScorer:
    """Scores model responses based on various metrics."""
    
    @staticmethod
    def calculate_completeness(response: Dict[str, Any]) -> float:
        """Calculate how complete the response is (0-1)."""
        if not response:
            return 0.0
            
        # Count non-empty fields
        total_fields = len(response)
        if total_fields == 0:
            return 0.0
            
        non_empty_fields = sum(1 for v in response.values() if v)
        return non_empty_fields / total_fields
    
    @staticmethod
    def calculate_confidence(response: Dict[str, Any]) -> float:
        """Calculate confidence score based on response structure (0-1)."""
        if not response:
            return 0.0
            
        # Simple implementation - can be enhanced with more sophisticated logic
        confidence = 0.5  # Base confidence
        
        # Check for common indicators of uncertainty
        text = json.dumps(response).lower()
        uncertainty_indicators = [
            'unknown', 'n/a', 'not found', 'not specified',
            'not available', 'missing', 'not detected'
        ]
        
        for indicator in uncertainty_indicators:
            if indicator in text:
                confidence -= 0.1  # Penalize for uncertainty indicators
                
        return max(0.0, min(1.0, confidence))  # Ensure score is between 0 and 1
    
    @classmethod
    def score_response(
        cls,
        model_name: str,
        response: Dict[str, Any],
        document_type: Optional[str] = None
    ) -> ModelScore:
        """Score a model's response."""
        if not response:
            return ModelScore(
                model_name=model_name,
                score=0.0,
                confidence=0.0,
                response=response,
                timestamp=datetime.utcnow().isoformat(),
                metrics={"completeness": 0.0, "confidence": 0.0}
            )
        
        completeness = cls.calculate_completeness(response)
        confidence = cls.calculate_confidence(response)
        
        # Combine scores (can be adjusted with weights)
        score = (completeness * 0.6) + (confidence * 0.4)
        
        return ModelScore(
            model_name=model_name,
            score=score,
            confidence=confidence,
            response=response,
            timestamp=datetime.utcnow().isoformat(),
            metrics={
                "completeness": completeness,
                "confidence": confidence
            }
        )
    
    @classmethod
    def select_best_model(
        cls,
        model_scores: List[ModelScore],
        min_confidence: float = 0.5
    ) -> Optional[ModelScore]:
        """Select the best model based on scores and minimum confidence."""
        if not model_scores:
            return None
            
        # Filter out low-confidence results
        valid_scores = [s for s in model_scores if s.confidence >= min_confidence]
        
        if not valid_scores:
            return max(model_scores, key=lambda x: x.score)  # Return best of the bad
            
        return max(valid_scores, key=lambda x: x.score)
