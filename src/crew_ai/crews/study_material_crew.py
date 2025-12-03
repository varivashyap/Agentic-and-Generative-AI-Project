"""
Study Material Crew for orchestrating multi-agent study content generation.
"""

import logging
from typing import Dict, Any, List, Optional
from crewai import Crew, Process

from ..agents.research_agent import ResearchAgent
from ..agents.content_generator import ContentGeneratorAgent
from ..agents.quality_reviewer import QualityReviewerAgent
from ..tasks.research_tasks import ResearchTasks
from ..tasks.content_generation_tasks import ContentGenerationTasks
from ..tasks.quality_review_tasks import QualityReviewTasks
from ...generation.llm_client import LLMClient

logger = logging.getLogger(__name__)


class StudyMaterialCrew:
    """
    CrewAI crew for collaborative study material generation.
    
    Orchestrates Research Agent, Content Generator Agent, and Quality Reviewer Agent
    to produce high-quality study materials through collaborative AI workflow.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the Study Material Crew.
        
        Args:
            llm_client: Optional shared LLM client for all agents
        """
        self.llm_client = llm_client or LLMClient()
        
        # Initialize agents
        self.research_agent = ResearchAgent(self.llm_client)
        self.content_generator = ContentGeneratorAgent(self.llm_client)
        self.quality_reviewer = QualityReviewerAgent(self.llm_client)
        
        logger.info("StudyMaterialCrew initialized with all agents")
    
    def generate_comprehensive_study_materials(
        self, 
        document_content: str, 
        rag_context: str = "",
        content_types: List[str] = None,
        enable_quality_review: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive study materials using multi-agent collaboration.
        
        Args:
            document_content: The main document content to process
            rag_context: Additional RAG context from retrieval
            content_types: Types of content to generate (["summaries", "flashcards", "quiz"])
            enable_quality_review: Whether to include quality review step
            
        Returns:
            Dictionary containing all generated study materials and reviews
        """
        if content_types is None:
            content_types = ["summaries", "flashcards", "quiz"]
        
        try:
            logger.info("Starting comprehensive study material generation with CrewAI")
            
            # Step 1: Research and Analysis
            research_task = ResearchTasks.analyze_document_task(
                agent=self.research_agent.agent,
                document_content=document_content,
                rag_context=rag_context
            )
            
            # Step 2: Content Generation Tasks
            content_tasks = []
            
            if "summaries" in content_types:
                summary_task = ContentGenerationTasks.generate_summaries_task(
                    agent=self.content_generator.agent,
                    research_analysis={"analysis": "Previous research analysis will be passed here"},
                    summary_types=["sentence", "paragraph", "section"]
                )
                content_tasks.append(summary_task)
            
            if "flashcards" in content_types:
                flashcard_task = ContentGenerationTasks.generate_flashcards_task(
                    agent=self.content_generator.agent,
                    research_analysis={"analysis": "Previous research analysis will be passed here"},
                    card_types=["definition", "concept", "cloze"]
                )
                content_tasks.append(flashcard_task)
            
            if "quiz" in content_types:
                quiz_task = ContentGenerationTasks.generate_quiz_task(
                    agent=self.content_generator.agent,
                    research_analysis={"analysis": "Previous research analysis will be passed here"},
                    question_types=["mcq", "short_answer"]
                )
                content_tasks.append(quiz_task)
            
            # Step 3: Quality Review (if enabled)
            review_tasks = []
            if enable_quality_review:
                comprehensive_review_task = QualityReviewTasks.comprehensive_quality_review_task(
                    agent=self.quality_reviewer.agent,
                    all_materials={"materials": "Generated materials will be passed here"},
                    research_analysis={"analysis": "Research analysis will be passed here"}
                )
                review_tasks.append(comprehensive_review_task)
            
            # Create and execute crew
            all_tasks = [research_task] + content_tasks + review_tasks
            
            crew = Crew(
                agents=[
                    self.research_agent.agent,
                    self.content_generator.agent,
                    self.quality_reviewer.agent
                ],
                tasks=all_tasks,
                process=Process.sequential,  # Sequential process for dependency management
                verbose=True
            )
            
            # Execute the crew workflow
            logger.info("Executing CrewAI workflow...")
            result = crew.kickoff()
            
            # For now, we'll modify the workflow to focus on getting the research analysis
            # In CrewAI 0.1.32, we can only get the final output, so let's restructure
            
            # If we only want summary, execute research + content generation workflow
            if len(content_types) == 1 and ('summary' in content_types or 'summaries' in content_types):
                # Create summary generation task for Content Generator
                from ..tasks.content_generation_tasks import ContentGenerationTasks
                summary_task = ContentGenerationTasks.generate_summaries_task(
                    agent=self.content_generator.agent,
                    research_analysis={"analysis": "Research analysis will be available from previous task"}
                )
                
                # Create a simplified crew with research + content generation for summaries
                summary_crew = Crew(
                    agents=[self.research_agent.agent, self.content_generator.agent],
                    tasks=[research_task, summary_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                logger.info("Executing simplified research + content generation workflow for summary...")
                content_result = summary_crew.kickoff()
                
                # Use the content generation result as our main output
                result = content_result
            
            # Process and format results
            formatted_results = self._format_crew_results(result, content_types, enable_quality_review)
            
            logger.info("CrewAI workflow completed successfully")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in CrewAI workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": {}
            }
    
    def generate_summaries_with_review(self, document_content: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Generate summaries with quality review using focused crew workflow.
        
        Args:
            document_content: Document content to summarize
            rag_context: Additional RAG context
            
        Returns:
            Dictionary containing summaries and review results
        """
        try:
            logger.info("Starting summary generation with quality review")
            
            # Research task
            research_task = ResearchTasks.analyze_document_task(
                agent=self.research_agent.agent,
                document_content=document_content,
                rag_context=rag_context
            )
            
            # Summary generation task
            summary_task = ContentGenerationTasks.generate_summaries_task(
                agent=self.content_generator.agent,
                research_analysis={"analysis": "Research analysis placeholder"},
                summary_types=["sentence", "paragraph", "section"]
            )
            
            # Summary review task
            review_task = QualityReviewTasks.review_summaries_task(
                agent=self.quality_reviewer.agent,
                summaries={"summaries": "Generated summaries placeholder"},
                research_analysis={"analysis": "Research analysis placeholder"}
            )
            
            # Create focused crew for summaries
            crew = Crew(
                agents=[
                    self.research_agent.agent,
                    self.content_generator.agent,
                    self.quality_reviewer.agent
                ],
                tasks=[research_task, summary_task, review_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "status": "success",
                "workflow_type": "summaries_with_review",
                "results": result
            }
            
        except Exception as e:
            logger.error(f"Error in summary generation workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_type": "summaries_with_review"
            }
    
    def generate_flashcards_with_review(self, document_content: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Generate flashcards with quality review using focused crew workflow.
        
        Args:
            document_content: Document content for flashcard creation
            rag_context: Additional RAG context
            
        Returns:
            Dictionary containing flashcards and review results
        """
        try:
            logger.info("Starting flashcard generation with quality review")
            
            # Research task
            research_task = ResearchTasks.analyze_document_task(
                agent=self.research_agent.agent,
                document_content=document_content,
                rag_context=rag_context
            )
            
            # Flashcard generation task
            flashcard_task = ContentGenerationTasks.generate_flashcards_task(
                agent=self.content_generator.agent,
                research_analysis={"analysis": "Research analysis placeholder"},
                card_types=["definition", "concept", "cloze"]
            )
            
            # Flashcard review task
            review_task = QualityReviewTasks.review_flashcards_task(
                agent=self.quality_reviewer.agent,
                flashcards={"flashcards": "Generated flashcards placeholder"},
                research_analysis={"analysis": "Research analysis placeholder"}
            )
            
            # Create focused crew for flashcards
            crew = Crew(
                agents=[
                    self.research_agent.agent,
                    self.content_generator.agent,
                    self.quality_reviewer.agent
                ],
                tasks=[research_task, flashcard_task, review_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "status": "success",
                "workflow_type": "flashcards_with_review",
                "results": result
            }
            
        except Exception as e:
            logger.error(f"Error in flashcard generation workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_type": "flashcards_with_review"
            }
    
    def generate_quiz_with_review(self, document_content: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Generate quiz questions with quality review using focused crew workflow.
        
        Args:
            document_content: Document content for quiz creation
            rag_context: Additional RAG context
            
        Returns:
            Dictionary containing quiz questions and review results
        """
        try:
            logger.info("Starting quiz generation with quality review")
            
            # Research task
            research_task = ResearchTasks.analyze_document_task(
                agent=self.research_agent.agent,
                document_content=document_content,
                rag_context=rag_context
            )
            
            # Quiz generation task
            quiz_task = ContentGenerationTasks.generate_quiz_task(
                agent=self.content_generator.agent,
                research_analysis={"analysis": "Research analysis placeholder"},
                question_types=["mcq", "short_answer"]
            )
            
            # Quiz review task
            review_task = QualityReviewTasks.review_quiz_task(
                agent=self.quality_reviewer.agent,
                quiz_questions={"quiz_questions": "Generated quiz questions placeholder"},
                research_analysis={"analysis": "Research analysis placeholder"}
            )
            
            # Create focused crew for quiz
            crew = Crew(
                agents=[
                    self.research_agent.agent,
                    self.content_generator.agent,
                    self.quality_reviewer.agent
                ],
                tasks=[research_task, quiz_task, review_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "status": "success",
                "workflow_type": "quiz_with_review",
                "results": result
            }
            
        except Exception as e:
            logger.error(f"Error in quiz generation workflow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_type": "quiz_with_review"
            }
    
    def _format_crew_results(self, crew_result: Any, content_types: List[str], enable_quality_review: bool) -> Dict[str, Any]:
        """
        Format CrewAI results into structured output.
        
        Args:
            crew_result: Raw result from CrewAI execution
            content_types: Types of content that were generated
            enable_quality_review: Whether quality review was enabled
            
        Returns:
            Formatted results dictionary
        """
        try:
            # Convert crew result to string if needed
            result_text = str(crew_result) if crew_result else ""
            
            formatted_results = {
                "status": "success",
                "workflow_type": "comprehensive" if len(content_types) > 1 else content_types[0],
                "content_types_generated": content_types,
                "quality_review_enabled": enable_quality_review,
                "raw_output": result_text,
                "generated_materials": {},
                "quality_reviews": {}
            }
            
            # Extract the actual summary from the CrewAI result
            # The result_text contains the Research Agent's analysis
            if "summary" in content_types or "summaries" in content_types:
                # Use the raw output as the summary for now
                # In production, you could parse this more sophisticatedly
                summary_content = result_text if result_text else "No summary generated"
                
                formatted_results["generated_materials"]["summaries"] = {
                    "sentence": summary_content[:200] + "..." if len(summary_content) > 200 else summary_content,
                    "paragraph": summary_content,
                    "section": summary_content
                }
                # Also add direct summary key for easier access
                formatted_results["summary"] = summary_content
            
            if "flashcards" in content_types:
                formatted_results["generated_materials"]["flashcards"] = {
                    "definition": "Generated definition cards would be extracted here",
                    "concept": "Generated concept cards would be extracted here",
                    "cloze": "Generated cloze cards would be extracted here"
                }
            
            if "quiz" in content_types:
                formatted_results["generated_materials"]["quiz"] = {
                    "mcq": "Generated MCQ questions would be extracted here",
                    "short_answer": "Generated short answer questions would be extracted here"
                }
            
            if enable_quality_review:
                formatted_results["quality_reviews"]["overall_assessment"] = "Quality review results would be extracted here"
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error formatting crew results: {e}")
            return {
                "status": "error",
                "error": f"Failed to format results: {str(e)}",
                "raw_output": str(crew_result) if crew_result else ""
            }