"""
Content Generator Agent for Study Assistant CrewAI integration.
Specializes in creating summaries, flashcards, and quizzes based on research insights.
"""

import logging
from typing import Dict, Any, Optional, List
from crewai import Agent

from .research_agent import CustomLlamaLLM
from ...generation.llm_client import LLMClient
from ...config import get_config

logger = logging.getLogger(__name__)


class ContentGeneratorAgent:
    """
    Content Generator Agent for creating educational study materials.
    
    This agent specializes in:
    - Summary generation at multiple levels
    - Flashcard creation (definition, concept, cloze)
    - Quiz question generation (MCQ, short-answer, numerical)
    - Content adaptation based on difficulty level
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the Content Generator Agent.
        
        Args:
            llm_client: Optional LLMClient instance. If None, creates a new one.
        """
        self.config = get_config()
        self.llm_client = llm_client or LLMClient()
        self.custom_llm = CustomLlamaLLM(self.llm_client)
        
        # Create the CrewAI agent
        self.agent = Agent(
            role='Educational Content Creator',
            goal='Generate high-quality study materials including summaries, flashcards, and quizzes based on research analysis',
            backstory="""You are an expert educational content creator with years of experience in developing
            effective learning materials. You understand how to adapt content for different learning styles and
            difficulty levels. Your expertise lies in creating clear, concise, and pedagogically sound study
            materials that help students learn and retain information effectively.""",
            verbose=True,
            allow_delegation=False,
            llm=self.custom_llm
        )
    
    def generate_summaries(self, research_analysis: Dict[str, Any], content_type: str = "all") -> Dict[str, Any]:
        """
        Generate summaries based on research analysis.
        
        Args:
            research_analysis: Research insights from ResearchAgent
            content_type: Type of summaries to generate ("sentence", "paragraph", "section", "all")
            
        Returns:
            Dictionary containing generated summaries
        """
        analysis_text = research_analysis.get("analysis", "")
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        summaries = {}
        
        if content_type in ["sentence", "all"]:
            summaries["sentence"] = self._generate_sentence_summary(analysis_text, difficulty)
        
        if content_type in ["paragraph", "all"]:
            summaries["paragraph"] = self._generate_paragraph_summary(analysis_text, difficulty)
            
        if content_type in ["section", "all"]:
            summaries["section"] = self._generate_section_summary(analysis_text, difficulty)
        
        return {
            "status": "success",
            "summaries": summaries,
            "difficulty_level": difficulty
        }
    
    def generate_flashcards(self, research_analysis: Dict[str, Any], card_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate flashcards based on research analysis.
        
        Args:
            research_analysis: Research insights from ResearchAgent
            card_types: Types of flashcards to generate (["definition", "concept", "cloze"])
            
        Returns:
            Dictionary containing generated flashcards
        """
        if card_types is None:
            card_types = ["definition", "concept", "cloze"]
        
        analysis_text = research_analysis.get("analysis", "")
        key_concepts = research_analysis.get("key_concepts", [])
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        flashcards = {}
        
        for card_type in card_types:
            if card_type == "definition":
                flashcards["definition"] = self._generate_definition_cards(analysis_text, key_concepts, difficulty)
            elif card_type == "concept":
                flashcards["concept"] = self._generate_concept_cards(analysis_text, key_concepts, difficulty)
            elif card_type == "cloze":
                flashcards["cloze"] = self._generate_cloze_cards(analysis_text, key_concepts, difficulty)
        
        return {
            "status": "success",
            "flashcards": flashcards,
            "total_cards": sum(len(cards) for cards in flashcards.values()),
            "difficulty_level": difficulty
        }
    
    def generate_quiz(self, research_analysis: Dict[str, Any], question_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate quiz questions based on research analysis.
        
        Args:
            research_analysis: Research insights from ResearchAgent
            question_types: Types of questions to generate (["mcq", "short_answer", "numerical"])
            
        Returns:
            Dictionary containing generated quiz questions
        """
        if question_types is None:
            question_types = ["mcq", "short_answer"]
        
        analysis_text = research_analysis.get("analysis", "")
        key_concepts = research_analysis.get("key_concepts", [])
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        quiz_questions = {}
        
        for question_type in question_types:
            if question_type == "mcq":
                quiz_questions["mcq"] = self._generate_mcq_questions(analysis_text, key_concepts, difficulty)
            elif question_type == "short_answer":
                quiz_questions["short_answer"] = self._generate_short_answer_questions(analysis_text, key_concepts, difficulty)
            elif question_type == "numerical":
                quiz_questions["numerical"] = self._generate_numerical_questions(analysis_text, key_concepts, difficulty)
        
        return {
            "status": "success",
            "quiz_questions": quiz_questions,
            "total_questions": sum(len(questions) for questions in quiz_questions.values()),
            "difficulty_level": difficulty
        }
    
    def _generate_sentence_summary(self, analysis_text: str, difficulty: str) -> str:
        """Generate a one-sentence summary."""
        prompt = f"""
        Based on the following analysis, create a single, comprehensive sentence that captures the main point:
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Create ONE clear, concise sentence that summarizes the most important concept.
        """
        
        return self.llm_client.generate(prompt=prompt, max_tokens=100, temperature=0.3)
    
    def _generate_paragraph_summary(self, analysis_text: str, difficulty: str) -> str:
        """Generate a paragraph-length summary."""
        prompt = f"""
        Based on the following analysis, create a paragraph summary (3-5 sentences):
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Create a paragraph that covers the key concepts and main ideas, appropriate for {difficulty} level students.
        """
        
        return self.llm_client.generate(prompt=prompt, max_tokens=300, temperature=0.3)
    
    def _generate_section_summary(self, analysis_text: str, difficulty: str) -> str:
        """Generate a section-length summary."""
        prompt = f"""
        Based on the following analysis, create a detailed section summary (multiple paragraphs):
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Create a comprehensive summary with multiple paragraphs, covering all important concepts and their relationships.
        Appropriate for {difficulty} level students.
        """
        
        return self.llm_client.generate(prompt=prompt, max_tokens=800, temperature=0.3)
    
    def _generate_definition_cards(self, analysis_text: str, key_concepts: List[str], difficulty: str) -> List[Dict[str, str]]:
        """Generate definition-style flashcards."""
        prompt = f"""
        Based on the following analysis and key concepts, create 5 definition flashcards:
        
        ANALYSIS:
        {analysis_text}
        
        KEY CONCEPTS:
        {chr(10).join(key_concepts)}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Format each flashcard as:
        FRONT: [Term]
        BACK: [Definition]
        ---
        
        Create clear, accurate definitions appropriate for {difficulty} level students.
        """
        
        response = self.llm_client.generate(prompt=prompt, max_tokens=600, temperature=0.3)
        return self._parse_flashcards(response)
    
    def _generate_concept_cards(self, analysis_text: str, key_concepts: List[str], difficulty: str) -> List[Dict[str, str]]:
        """Generate concept-style flashcards."""
        prompt = f"""
        Based on the following analysis, create 5 concept flashcards:
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Format each flashcard as:
        FRONT: [Concept or Question]
        BACK: [Explanation or Answer]
        ---
        
        Focus on understanding and application rather than just definitions.
        """
        
        response = self.llm_client.generate(prompt=prompt, max_tokens=600, temperature=0.3)
        return self._parse_flashcards(response)
    
    def _generate_cloze_cards(self, analysis_text: str, key_concepts: List[str], difficulty: str) -> List[Dict[str, str]]:
        """Generate cloze-deletion flashcards."""
        prompt = f"""
        Based on the following analysis, create 5 cloze deletion flashcards:
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Format each flashcard as:
        FRONT: [Sentence with {{c1::missing word}}]
        BACK: [Complete sentence]
        ---
        
        Use important terms and concepts for the cloze deletions.
        """
        
        response = self.llm_client.generate(prompt=prompt, max_tokens=600, temperature=0.3)
        return self._parse_flashcards(response)
    
    def _generate_mcq_questions(self, analysis_text: str, key_concepts: List[str], difficulty: str) -> List[Dict[str, Any]]:
        """Generate multiple choice questions."""
        prompt = f"""
        Based on the following analysis, create 5 multiple choice questions:
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Format each question as:
        QUESTION: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        CORRECT: [A/B/C/D]
        EXPLANATION: [Why this answer is correct]
        ---
        
        Make questions appropriate for {difficulty} level students.
        """
        
        response = self.llm_client.generate(prompt=prompt, max_tokens=800, temperature=0.3)
        return self._parse_mcq_questions(response)
    
    def _generate_short_answer_questions(self, analysis_text: str, key_concepts: List[str], difficulty: str) -> List[Dict[str, str]]:
        """Generate short answer questions."""
        prompt = f"""
        Based on the following analysis, create 5 short answer questions:
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Format each question as:
        QUESTION: [Question text]
        ANSWER: [Expected answer]
        ---
        
        Create questions that require understanding, not just memorization.
        """
        
        response = self.llm_client.generate(prompt=prompt, max_tokens=600, temperature=0.3)
        return self._parse_short_answer_questions(response)
    
    def _generate_numerical_questions(self, analysis_text: str, key_concepts: List[str], difficulty: str) -> List[Dict[str, str]]:
        """Generate numerical questions if applicable."""
        prompt = f"""
        Based on the following analysis, create numerical questions if the content involves calculations:
        
        ANALYSIS:
        {analysis_text}
        
        DIFFICULTY LEVEL: {difficulty}
        
        Only create numerical questions if the content involves math, calculations, or quantitative data.
        Format each question as:
        QUESTION: [Question with numerical problem]
        ANSWER: [Numerical answer with units if applicable]
        SOLUTION: [Step-by-step solution]
        ---
        
        If no numerical content is present, respond with "No numerical questions applicable."
        """
        
        response = self.llm_client.generate(prompt=prompt, max_tokens=600, temperature=0.3)
        if "no numerical questions applicable" in response.lower():
            return []
        return self._parse_numerical_questions(response)
    
    def _parse_flashcards(self, response: str) -> List[Dict[str, str]]:
        """Parse flashcard response into structured format."""
        cards = []
        sections = response.split('---')
        for section in sections:
            lines = section.strip().split('\n')
            front, back = "", ""
            for line in lines:
                if line.startswith('FRONT:'):
                    front = line.replace('FRONT:', '').strip()
                elif line.startswith('BACK:'):
                    back = line.replace('BACK:', '').strip()
            if front and back:
                cards.append({"front": front, "back": back})
        return cards
    
    def _parse_mcq_questions(self, response: str) -> List[Dict[str, Any]]:
        """Parse MCQ response into structured format."""
        questions = []
        sections = response.split('---')
        for section in sections:
            lines = section.strip().split('\n')
            question_data = {}
            options = []
            for line in lines:
                if line.startswith('QUESTION:'):
                    question_data["question"] = line.replace('QUESTION:', '').strip()
                elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                    options.append(line.strip())
                elif line.startswith('CORRECT:'):
                    question_data["correct"] = line.replace('CORRECT:', '').strip()
                elif line.startswith('EXPLANATION:'):
                    question_data["explanation"] = line.replace('EXPLANATION:', '').strip()
            
            if "question" in question_data and options:
                question_data["options"] = options
                questions.append(question_data)
        return questions
    
    def _parse_short_answer_questions(self, response: str) -> List[Dict[str, str]]:
        """Parse short answer response into structured format."""
        questions = []
        sections = response.split('---')
        for section in sections:
            lines = section.strip().split('\n')
            question, answer = "", ""
            for line in lines:
                if line.startswith('QUESTION:'):
                    question = line.replace('QUESTION:', '').strip()
                elif line.startswith('ANSWER:'):
                    answer = line.replace('ANSWER:', '').strip()
            if question and answer:
                questions.append({"question": question, "answer": answer})
        return questions
    
    def _parse_numerical_questions(self, response: str) -> List[Dict[str, str]]:
        """Parse numerical response into structured format."""
        questions = []
        sections = response.split('---')
        for section in sections:
            lines = section.strip().split('\n')
            question_data = {}
            for line in lines:
                if line.startswith('QUESTION:'):
                    question_data["question"] = line.replace('QUESTION:', '').strip()
                elif line.startswith('ANSWER:'):
                    question_data["answer"] = line.replace('ANSWER:', '').strip()
                elif line.startswith('SOLUTION:'):
                    question_data["solution"] = line.replace('SOLUTION:', '').strip()
            
            if "question" in question_data and "answer" in question_data:
                questions.append(question_data)
        return questions