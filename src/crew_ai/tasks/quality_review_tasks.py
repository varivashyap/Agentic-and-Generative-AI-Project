"""
Quality Review Tasks for Study Assistant CrewAI integration.
Defines tasks for the Quality Reviewer Agent.
"""

from crewai import Task
from typing import Dict, Any


class QualityReviewTasks:
    """Quality review task definitions for CrewAI workflow."""
    
    @staticmethod
    def review_summaries_task(agent, summaries: Dict[str, Any], research_analysis: Dict[str, Any]) -> Task:
        """
        Create a task for reviewing generated summaries.
        
        Args:
            agent: The quality reviewer agent
            summaries: Generated summaries to review
            research_analysis: Original research analysis for comparison
            
        Returns:
            CrewAI Task for summary review
        """
        original_analysis = research_analysis.get("analysis", "")
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Review the generated summaries for quality, accuracy, and educational effectiveness:
            
            SUMMARIES TO REVIEW:
            {summaries}
            
            ORIGINAL RESEARCH ANALYSIS:
            {original_analysis[:1500]}{"..." if len(original_analysis) > 1500 else ""}
            
            TARGET DIFFICULTY: {difficulty_level}
            
            Evaluate each summary on:
            1. ACCURACY: Does it correctly represent the original content?
            2. COMPLETENESS: Are key concepts covered appropriately?
            3. CLARITY: Is it clear and easy to understand for {difficulty_level} students?
            4. EDUCATIONAL VALUE: Will it help students learn effectively?
            5. FORMAT APPROPRIATENESS: Is it suitable for its intended purpose?
            
            For each summary type, provide:
            - Scores (1-10) for each evaluation criteria
            - Specific strengths and weaknesses
            - Concrete improvement suggestions
            - Overall quality assessment
            
            Focus on educational effectiveness and student learning outcomes.
            """,
            agent=agent,
            expected_output="Detailed quality review with scores, strengths, weaknesses, and specific improvement recommendations for each summary."
        )
    
    @staticmethod
    def review_flashcards_task(agent, flashcards: Dict[str, Any], research_analysis: Dict[str, Any]) -> Task:
        """
        Create a task for reviewing generated flashcards.
        
        Args:
            agent: The quality reviewer agent
            flashcards: Generated flashcards to review
            research_analysis: Original research analysis for comparison
            
        Returns:
            CrewAI Task for flashcard review
        """
        key_concepts = research_analysis.get("key_concepts", [])
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Review the generated flashcards for educational effectiveness and quality:
            
            FLASHCARDS TO REVIEW:
            {flashcards}
            
            KEY CONCEPTS FROM RESEARCH:
            {chr(10).join(key_concepts[:10])}
            
            TARGET DIFFICULTY: {difficulty_level}
            
            Evaluate the flashcards on:
            1. CONTENT ACCURACY: Are the facts and concepts correct?
            2. LEARNING EFFECTIVENESS: Do they promote active recall and retention?
            3. CLARITY: Are questions and answers clear and unambiguous?
            4. CONCEPT COVERAGE: Do they cover the most important concepts?
            5. CARD QUALITY: Are they well-formatted for their card type?
            6. DIFFICULTY ALIGNMENT: Are they appropriate for {difficulty_level} students?
            
            For each flashcard set, provide:
            - Educational effectiveness assessment
            - Content accuracy verification
            - Specific cards that need improvement
            - Suggestions for better learning outcomes
            - Overall quality rating
            
            Focus on how well these cards will help students learn and remember key concepts.
            """,
            agent=agent,
            expected_output="Comprehensive quality review focusing on educational effectiveness, with specific feedback on card quality and learning value."
        )
    
    @staticmethod
    def review_quiz_task(agent, quiz_questions: Dict[str, Any], research_analysis: Dict[str, Any]) -> Task:
        """
        Create a task for reviewing generated quiz questions.
        
        Args:
            agent: The quality reviewer agent
            quiz_questions: Generated quiz questions to review
            research_analysis: Original research analysis for comparison
            
        Returns:
            CrewAI Task for quiz review
        """
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Review the generated quiz questions for assessment quality and educational value:
            
            QUIZ QUESTIONS TO REVIEW:
            {quiz_questions}
            
            TARGET DIFFICULTY: {difficulty_level}
            
            Evaluate the quiz questions on:
            1. QUESTION QUALITY: Are questions well-constructed and clear?
            2. CONTENT ALIGNMENT: Do they test understanding of key concepts?
            3. DIFFICULTY APPROPRIATENESS: Are they suitable for {difficulty_level} students?
            4. ANSWER ACCURACY: Are the provided answers correct and complete?
            5. EDUCATIONAL VALUE: Do they promote learning and critical thinking?
            6. ASSESSMENT VALIDITY: Do they effectively measure student understanding?
            
            For each question type, analyze:
            - Question construction and clarity
            - Learning objectives alignment
            - Answer quality and explanations
            - Potential for student confusion
            - Assessment effectiveness
            
            Provide specific recommendations for:
            - Improving question wording
            - Better answer choices (for MCQ)
            - More effective assessment of understanding
            - Enhancing educational value
            
            Focus on creating fair, effective assessments that promote student learning.
            """,
            agent=agent,
            expected_output="Thorough assessment quality review with specific recommendations for improving question effectiveness and educational value."
        )
    
    @staticmethod
    def comprehensive_quality_review_task(agent, all_materials: Dict[str, Any], research_analysis: Dict[str, Any]) -> Task:
        """
        Create a task for comprehensive quality review of all generated materials.
        
        Args:
            agent: The quality reviewer agent
            all_materials: All generated study materials
            research_analysis: Original research analysis for comparison
            
        Returns:
            CrewAI Task for comprehensive review
        """
        difficulty_level = research_analysis.get("difficulty_level", "intermediate")
        
        return Task(
            description=f"""
            Conduct a comprehensive quality review of all generated study materials:
            
            MATERIALS TO REVIEW:
            {all_materials}
            
            ORIGINAL RESEARCH ANALYSIS:
            {research_analysis.get("analysis", "")[:1000]}{"..." if len(research_analysis.get("analysis", "")) > 1000 else ""}
            
            TARGET DIFFICULTY: {difficulty_level}
            
            Perform a holistic evaluation covering:
            
            1. OVERALL COHERENCE:
               - Do all materials work together as a cohesive study package?
               - Is there good coverage of key concepts across all formats?
               - Are difficulty levels consistent across materials?
            
            2. EDUCATIONAL EFFECTIVENESS:
               - Do the materials support different learning styles?
               - Is there good progression from summaries to active practice?
               - Will students achieve the learning objectives?
            
            3. QUALITY STANDARDS:
               - Content accuracy across all materials
               - Clarity and comprehensibility
               - Appropriate formatting and structure
            
            4. RECOMMENDATIONS:
               - Priority improvements for maximum impact
               - Suggestions for enhancing learning outcomes
               - Overall package rating and readiness assessment
            
            Provide a comprehensive quality assessment with:
            - Executive summary of overall quality
            - Strengths of the study package
            - Key areas for improvement
            - Specific action items for enhancement
            - Final recommendation for use
            """,
            agent=agent,
            expected_output="Comprehensive quality assessment with executive summary, detailed analysis, and actionable recommendations for the complete study materials package."
        )