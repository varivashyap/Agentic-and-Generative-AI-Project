"""
Content Generation Tasks for Study Assistant CrewAI integration.
Defines tasks for the Content Generator Agent.
"""

from crewai import Task
from typing import Dict, Any, List


class ContentGenerationTasks:
    """Content generation task definitions for CrewAI workflow."""
    
    @staticmethod
    def generate_summaries_task(agent, research_analysis: Dict[str, Any], summary_types: List[str] = None) -> Task:
        """
        Create a task for generating summaries.
        
        Args:
            agent: The content generator agent
            research_analysis: Research analysis from research agent
            summary_types: Types of summaries to generate
            
        Returns:
            CrewAI Task for summary generation
        """
        if summary_types is None:
            summary_types = ["sentence", "paragraph", "section"]
        
        analysis_text = research_analysis.get("analysis", "")
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Generate high-quality summaries based on the research analysis:
            
            RESEARCH ANALYSIS:
            {analysis_text}
            
            DIFFICULTY LEVEL: {difficulty}
            SUMMARY TYPES NEEDED: {', '.join(summary_types)}
            
            Create summaries that are:
            1. Accurate to the source material
            2. Appropriate for {difficulty} level students
            3. Clear and well-structured
            4. Educationally valuable
            
            For each summary type:
            - Sentence: One comprehensive sentence capturing the main point
            - Paragraph: 3-5 sentences covering key concepts
            - Section: Multiple paragraphs with detailed coverage
            
            Ensure each summary serves its intended purpose for student learning.
            """,
            agent=agent,
            expected_output=f"Well-structured summaries in the requested formats: {', '.join(summary_types)}, appropriate for {difficulty} level students."
        )
    
    @staticmethod
    def generate_flashcards_task(agent, research_analysis: Dict[str, Any], card_types: List[str] = None) -> Task:
        """
        Create a task for generating flashcards.
        
        Args:
            agent: The content generator agent
            research_analysis: Research analysis from research agent
            card_types: Types of flashcards to generate
            
        Returns:
            CrewAI Task for flashcard generation
        """
        if card_types is None:
            card_types = ["definition", "concept", "cloze"]
        
        analysis_text = research_analysis.get("analysis", "")
        key_concepts = research_analysis.get("key_concepts", [])
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Generate effective flashcards based on the research analysis:
            
            RESEARCH ANALYSIS:
            {analysis_text}
            
            KEY CONCEPTS:
            {chr(10).join(key_concepts[:10])}
            
            DIFFICULTY LEVEL: {difficulty}
            CARD TYPES NEEDED: {', '.join(card_types)}
            
            Create flashcards that are:
            1. Focused on key concepts and important information
            2. Clear and unambiguous
            3. Appropriate for {difficulty} level students
            4. Effective for active recall and spaced repetition
            
            For each card type:
            - Definition: Term on front, clear definition on back
            - Concept: Question/scenario on front, explanation on back
            - Cloze: Sentence with key term deleted, complete sentence on back
            
            Aim for 5-8 cards per type, focusing on the most important concepts.
            """,
            agent=agent,
            expected_output=f"High-quality flashcards in the requested formats: {', '.join(card_types)}, optimized for learning and retention."
        )
    
    @staticmethod
    def generate_quiz_task(agent, research_analysis: Dict[str, Any], question_types: List[str] = None) -> Task:
        """
        Create a task for generating quiz questions.
        
        Args:
            agent: The content generator agent
            research_analysis: Research analysis from research agent
            question_types: Types of questions to generate
            
        Returns:
            CrewAI Task for quiz generation
        """
        if question_types is None:
            question_types = ["mcq", "short_answer"]
        
        analysis_text = research_analysis.get("analysis", "")
        key_concepts = research_analysis.get("key_concepts", [])
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Generate comprehensive quiz questions based on the research analysis:
            
            RESEARCH ANALYSIS:
            {analysis_text}
            
            KEY CONCEPTS:
            {chr(10).join(key_concepts[:10])}
            
            DIFFICULTY LEVEL: {difficulty}
            QUESTION TYPES NEEDED: {', '.join(question_types)}
            
            Create quiz questions that are:
            1. Test understanding, not just memorization
            2. Cover important concepts thoroughly
            3. Appropriate for {difficulty} level students
            4. Have clear, accurate answers
            5. Promote critical thinking
            
            For each question type:
            - MCQ: Clear question with 4 options, one correct answer, brief explanation
            - Short Answer: Open-ended questions requiring understanding
            - Numerical: Calculation-based questions if applicable to content
            
            Aim for 5-8 questions per type, covering key learning objectives.
            """,
            agent=agent,
            expected_output=f"Well-designed quiz questions in the requested formats: {', '.join(question_types)}, suitable for assessment and learning."
        )
    
    @staticmethod
    def comprehensive_generation_task(agent, research_analysis: Dict[str, Any]) -> Task:
        """
        Create a task for generating all types of study materials.
        
        Args:
            agent: The content generator agent
            research_analysis: Research analysis from research agent
            
        Returns:
            CrewAI Task for comprehensive content generation
        """
        analysis_text = research_analysis.get("analysis", "")
        difficulty = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Generate a comprehensive set of study materials based on the research analysis:
            
            RESEARCH ANALYSIS:
            {analysis_text}
            
            DIFFICULTY LEVEL: {difficulty}
            
            Create a complete study package including:
            
            1. SUMMARIES:
               - One sentence summary (main point)
               - Paragraph summary (key concepts)
               - Section summary (detailed coverage)
            
            2. FLASHCARDS:
               - Definition cards (terms and meanings)
               - Concept cards (understanding-based)
               - Cloze deletion cards (fill-in-the-blank)
            
            3. QUIZ QUESTIONS:
               - Multiple choice questions
               - Short answer questions
               - Numerical questions (if applicable)
            
            Ensure all materials are:
            - Educationally sound and accurate
            - Appropriate for {difficulty} level students
            - Complementary to each other
            - Focused on key learning objectives
            - Ready for immediate use by students
            
            Organize the output clearly by material type.
            """,
            agent=agent,
            expected_output="A comprehensive study package with summaries, flashcards, and quiz questions, all properly formatted and educationally effective."
        )