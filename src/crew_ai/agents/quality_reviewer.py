"""
Quality Reviewer Agent for Study Assistant CrewAI integration.
Specializes in reviewing and improving generated study materials.
"""

import logging
from typing import Dict, Any, Optional, List
from crewai import Agent

from .research_agent import CustomLlamaLLM
from ...generation.llm_client import LLMClient
from ...config import get_config

logger = logging.getLogger(__name__)


class QualityReviewerAgent:
    """
    Quality Reviewer Agent for evaluating and improving study materials.
    
    This agent specializes in:
    - Content accuracy verification
    - Educational effectiveness assessment
    - Clarity and coherence improvement suggestions
    - Difficulty level validation
    - Learning objective alignment
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the Quality Reviewer Agent.
        
        Args:
            llm_client: Optional LLMClient instance. If None, creates a new one.
        """
        self.config = get_config()
        self.llm_client = llm_client or LLMClient()
        self.custom_llm = CustomLlamaLLM(self.llm_client)
        
        # Create the CrewAI agent
        self.agent = Agent(
            role='Educational Quality Reviewer',
            goal='Review and improve the quality, accuracy, and educational effectiveness of generated study materials',
            backstory="""You are an experienced educational quality assurance expert with a keen eye for detail
            and deep understanding of pedagogical best practices. You have years of experience reviewing educational
            content and ensuring it meets the highest standards for student learning. Your expertise includes
            content accuracy verification, learning objective alignment, and educational effectiveness assessment.""",
            verbose=True,
            allow_delegation=False,
            llm=self.custom_llm
        )
    
    def review_summaries(self, summaries: Dict[str, Any], research_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review generated summaries for quality and accuracy.
        
        Args:
            summaries: Generated summaries from ContentGeneratorAgent
            research_analysis: Original research analysis for comparison
            
        Returns:
            Dictionary containing review results and improvement suggestions
        """
        original_analysis = research_analysis.get("analysis", "")
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        review_results = {}
        
        for summary_type, summary_content in summaries.get("summaries", {}).items():
            review_results[summary_type] = self._review_single_summary(
                summary_content, original_analysis, difficulty_level, summary_type
            )
        
        return {
            "status": "success",
            "review_results": review_results,
            "overall_quality": self._assess_overall_quality(review_results),
            "improvement_suggestions": self._generate_improvement_suggestions(review_results)
        }
    
    def review_flashcards(self, flashcards: Dict[str, Any], research_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review generated flashcards for educational effectiveness.
        
        Args:
            flashcards: Generated flashcards from ContentGeneratorAgent
            research_analysis: Original research analysis for comparison
            
        Returns:
            Dictionary containing review results and suggestions
        """
        original_analysis = research_analysis.get("analysis", "")
        key_concepts = research_analysis.get("key_concepts", [])
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        review_results = {}
        
        for card_type, cards in flashcards.get("flashcards", {}).items():
            review_results[card_type] = self._review_flashcard_set(
                cards, original_analysis, key_concepts, difficulty_level, card_type
            )
        
        return {
            "status": "success",
            "review_results": review_results,
            "overall_quality": self._assess_overall_quality(review_results),
            "educational_effectiveness": self._assess_educational_effectiveness(review_results)
        }
    
    def review_quiz(self, quiz_questions: Dict[str, Any], research_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review generated quiz questions for accuracy and appropriateness.
        
        Args:
            quiz_questions: Generated quiz questions from ContentGeneratorAgent
            research_analysis: Original research analysis for comparison
            
        Returns:
            Dictionary containing review results and suggestions
        """
        original_analysis = research_analysis.get("analysis", "")
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        review_results = {}
        
        for question_type, questions in quiz_questions.get("quiz_questions", {}).items():
            review_results[question_type] = self._review_question_set(
                questions, original_analysis, difficulty_level, question_type
            )
        
        return {
            "status": "success",
            "review_results": review_results,
            "overall_quality": self._assess_overall_quality(review_results),
            "assessment_validity": self._assess_assessment_validity(review_results)
        }
    
    def _review_single_summary(self, summary: str, original_analysis: str, difficulty_level: str, summary_type: str) -> Dict[str, Any]:
        """Review a single summary for quality."""
        review_prompt = f"""
        Review the following {summary_type} summary for quality and educational effectiveness:
        
        SUMMARY TO REVIEW:
        {summary}
        
        ORIGINAL ANALYSIS:
        {original_analysis}
        
        TARGET DIFFICULTY: {difficulty_level}
        SUMMARY TYPE: {summary_type}
        
        Please evaluate:
        1. Accuracy - Does it correctly represent the original content?
        2. Completeness - Are key concepts covered appropriately for a {summary_type} summary?
        3. Clarity - Is it clear and easy to understand for {difficulty_level} level students?
        4. Appropriateness - Is the length and detail appropriate for {summary_type} format?
        
        Provide a score (1-10) for each criteria and overall recommendations.
        Format: ACCURACY: X/10, COMPLETENESS: X/10, CLARITY: X/10, APPROPRIATENESS: X/10
        RECOMMENDATIONS: [your suggestions]
        """
        
        review_response = self.llm_client.generate(
            prompt=review_prompt, 
            max_tokens=400, 
            temperature=0.2
        )
        
        return {
            "summary_type": summary_type,
            "review_text": review_response,
            "scores": self._extract_scores(review_response),
            "recommendations": self._extract_recommendations(review_response)
        }
    
    def _review_flashcard_set(self, cards: List[Dict], original_analysis: str, key_concepts: List[str], difficulty_level: str, card_type: str) -> Dict[str, Any]:
        """Review a set of flashcards."""
        cards_text = "\n".join([f"FRONT: {card.get('front', 'N/A')}\nBACK: {card.get('back', 'N/A')}\n---" for card in cards])
        
        review_prompt = f"""
        Review the following {card_type} flashcards for educational effectiveness:
        
        FLASHCARDS TO REVIEW:
        {cards_text}
        
        ORIGINAL ANALYSIS:
        {original_analysis[:500]}...
        
        KEY CONCEPTS:
        {chr(10).join(key_concepts[:5])}
        
        TARGET DIFFICULTY: {difficulty_level}
        CARD TYPE: {card_type}
        
        Please evaluate:
        1. Content Accuracy - Are the facts and concepts correct?
        2. Learning Value - Do these cards help with {difficulty_level} level learning?
        3. Clarity - Are the questions and answers clear?
        4. Concept Coverage - Do they cover important concepts?
        5. Card Quality - Are they well-formatted for {card_type} style?
        
        Provide scores (1-10) and specific improvement suggestions.
        """
        
        review_response = self.llm_client.generate(
            prompt=review_prompt, 
            max_tokens=500, 
            temperature=0.2
        )
        
        return {
            "card_type": card_type,
            "card_count": len(cards),
            "review_text": review_response,
            "scores": self._extract_scores(review_response),
            "recommendations": self._extract_recommendations(review_response)
        }
    
    def _review_question_set(self, questions: List[Dict], original_analysis: str, difficulty_level: str, question_type: str) -> Dict[str, Any]:
        """Review a set of quiz questions."""
        questions_text = ""
        for i, q in enumerate(questions, 1):
            if question_type == "mcq":
                options_text = "\n".join(q.get("options", []))
                questions_text += f"Q{i}: {q.get('question', 'N/A')}\n{options_text}\nCorrect: {q.get('correct', 'N/A')}\n---\n"
            else:
                questions_text += f"Q{i}: {q.get('question', 'N/A')}\nAnswer: {q.get('answer', 'N/A')}\n---\n"
        
        review_prompt = f"""
        Review the following {question_type} quiz questions for assessment quality:
        
        QUESTIONS TO REVIEW:
        {questions_text}
        
        ORIGINAL ANALYSIS:
        {original_analysis[:500]}...
        
        TARGET DIFFICULTY: {difficulty_level}
        QUESTION TYPE: {question_type}
        
        Please evaluate:
        1. Question Quality - Are questions well-constructed and clear?
        2. Content Alignment - Do they test understanding of key concepts?
        3. Difficulty Level - Are they appropriate for {difficulty_level} students?
        4. Answer Accuracy - Are the provided answers correct?
        5. Educational Value - Do they promote learning and understanding?
        
        Provide scores (1-10) and specific suggestions for improvement.
        """
        
        review_response = self.llm_client.generate(
            prompt=review_prompt, 
            max_tokens=500, 
            temperature=0.2
        )
        
        return {
            "question_type": question_type,
            "question_count": len(questions),
            "review_text": review_response,
            "scores": self._extract_scores(review_response),
            "recommendations": self._extract_recommendations(review_response)
        }
    
    def _extract_scores(self, review_text: str) -> Dict[str, int]:
        """Extract numerical scores from review text."""
        scores = {}
        lines = review_text.split('\n')
        for line in lines:
            line_upper = line.upper()
            for criterion in ['ACCURACY', 'COMPLETENESS', 'CLARITY', 'APPROPRIATENESS', 
                            'CONTENT ACCURACY', 'LEARNING VALUE', 'CONCEPT COVERAGE', 
                            'CARD QUALITY', 'QUESTION QUALITY', 'CONTENT ALIGNMENT', 
                            'DIFFICULTY LEVEL', 'ANSWER ACCURACY', 'EDUCATIONAL VALUE']:
                if criterion in line_upper and '/10' in line_upper:
                    try:
                        # Extract number before '/10'
                        parts = line_upper.split(criterion)
                        if len(parts) > 1:
                            score_part = parts[1].split('/10')[0].strip()
                            # Find the last number in the score part
                            score = int(''.join(filter(str.isdigit, score_part)))
                            if 1 <= score <= 10:
                                scores[criterion.lower().replace(' ', '_')] = score
                    except (ValueError, IndexError):
                        continue
        return scores
    
    def _extract_recommendations(self, review_text: str) -> str:
        """Extract recommendations from review text."""
        lines = review_text.split('\n')
        for line in lines:
            if 'RECOMMENDATION' in line.upper():
                return line.split(':', 1)[1].strip() if ':' in line else line.strip()
        return "No specific recommendations provided."
    
    def _assess_overall_quality(self, review_results: Dict[str, Any]) -> str:
        """Assess overall quality based on review results."""
        all_scores = []
        for result in review_results.values():
            scores = result.get("scores", {})
            all_scores.extend(scores.values())
        
        if not all_scores:
            return "unable_to_assess"
        
        avg_score = sum(all_scores) / len(all_scores)
        
        if avg_score >= 8:
            return "excellent"
        elif avg_score >= 6:
            return "good"
        elif avg_score >= 4:
            return "fair"
        else:
            return "needs_improvement"
    
    def _assess_educational_effectiveness(self, review_results: Dict[str, Any]) -> str:
        """Assess educational effectiveness of flashcards."""
        learning_scores = []
        for result in review_results.values():
            scores = result.get("scores", {})
            # Look for learning-related scores
            for key, score in scores.items():
                if any(term in key for term in ['learning', 'educational', 'concept']):
                    learning_scores.append(score)
        
        if not learning_scores:
            return "unable_to_assess"
        
        avg_score = sum(learning_scores) / len(learning_scores)
        
        if avg_score >= 8:
            return "highly_effective"
        elif avg_score >= 6:
            return "effective"
        elif avg_score >= 4:
            return "moderately_effective"
        else:
            return "low_effectiveness"
    
    def _assess_assessment_validity(self, review_results: Dict[str, Any]) -> str:
        """Assess validity of quiz questions as assessment tools."""
        assessment_scores = []
        for result in review_results.values():
            scores = result.get("scores", {})
            # Look for assessment-related scores
            for key, score in scores.items():
                if any(term in key for term in ['question', 'accuracy', 'alignment']):
                    assessment_scores.append(score)
        
        if not assessment_scores:
            return "unable_to_assess"
        
        avg_score = sum(assessment_scores) / len(assessment_scores)
        
        if avg_score >= 8:
            return "high_validity"
        elif avg_score >= 6:
            return "good_validity"
        elif avg_score >= 4:
            return "fair_validity"
        else:
            return "low_validity"
    
    def _generate_improvement_suggestions(self, review_results: Dict[str, Any]) -> List[str]:
        """Generate overall improvement suggestions based on review results."""
        suggestions = []
        
        # Collect all recommendations
        all_recommendations = []
        for result in review_results.values():
            rec = result.get("recommendations", "")
            if rec and rec != "No specific recommendations provided.":
                all_recommendations.append(rec)
        
        # Analyze common themes and generate suggestions
        common_themes = self._identify_common_themes(all_recommendations)
        
        for theme in common_themes:
            suggestions.append(f"Consider improving: {theme}")
        
        if not suggestions:
            suggestions.append("Content quality appears satisfactory based on review criteria.")
        
        return suggestions
    
    def _identify_common_themes(self, recommendations: List[str]) -> List[str]:
        """Identify common themes in recommendations."""
        themes = []
        all_text = " ".join(recommendations).lower()
        
        # Common improvement areas
        if any(word in all_text for word in ['clarity', 'clear', 'confusing']):
            themes.append("clarity and readability")
        if any(word in all_text for word in ['accuracy', 'correct', 'wrong', 'error']):
            themes.append("content accuracy")
        if any(word in all_text for word in ['complete', 'missing', 'incomplete']):
            themes.append("content completeness")
        if any(word in all_text for word in ['difficult', 'easy', 'level', 'appropriate']):
            themes.append("difficulty level alignment")
        if any(word in all_text for word in ['format', 'structure', 'organization']):
            themes.append("formatting and structure")
        
        return themes