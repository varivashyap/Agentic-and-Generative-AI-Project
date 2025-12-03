"""
Example usage of CrewAI integration for Study Assistant.
Demonstrates how to use the enhanced multi-agent workflows.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_crewai_usage():
    """Basic example of using CrewAI enhanced generation."""
    print("=== CrewAI Basic Usage Example ===")
    
    try:
        from src.pipeline import StudyAssistantPipeline
        
        # Initialize pipeline (CrewAI will be auto-detected and initialized)
        pipeline = StudyAssistantPipeline()
        
        # Check if CrewAI is available
        if pipeline.is_crewai_available():
            print("✓ CrewAI is available and ready")
            status = pipeline.get_crewai_status()
            print(f"Status: {status}")
        else:
            print("✗ CrewAI is not available")
            return
        
        # Example file path (replace with your actual file)
        sample_file = Path("data/sample_lecture.pdf")
        
        if not sample_file.exists():
            print(f"Sample file not found: {sample_file}")
            print("Please place a PDF file at data/sample_lecture.pdf or update the path")
            return
        
        # Generate complete study package with CrewAI
        print("\n🤖 Generating complete study package with CrewAI...")
        result = pipeline.generate_complete_study_package(
            file_path=str(sample_file),
            use_crewai=True
        )
        
        print(f"Generation status: {result.get('status')}")
        print(f"Generation method: {result.get('generation_method')}")
        print(f"Content types: {result.get('content_types_generated', [])}")
        
        if result.get('status') == 'success':
            print("✓ Study materials generated successfully!")
            
            # Show overview of generated materials
            materials = result.get('generated_materials', {})
            for material_type, content in materials.items():
                print(f"  - {material_type}: Generated")
                
        else:
            print(f"✗ Generation failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Example failed: {e}")


def example_focused_workflows():
    """Example of using focused CrewAI workflows for specific content types."""
    print("\n=== CrewAI Focused Workflows Example ===")
    
    try:
        from src.pipeline import StudyAssistantPipeline
        
        pipeline = StudyAssistantPipeline()
        
        if not pipeline.is_crewai_available():
            print("CrewAI not available")
            return
        
        sample_file = Path("data/sample_lecture.pdf")
        if not sample_file.exists():
            print("Sample file not found")
            return
        
        # Generate enhanced summaries only
        print("\n📄 Generating enhanced summaries...")
        summaries_result = pipeline.generate_crewai_summaries(str(sample_file))
        
        if summaries_result.get('status') == 'success':
            print("✓ Enhanced summaries generated")
        else:
            print(f"✗ Summary generation failed: {summaries_result.get('error')}")
        
        # Generate enhanced flashcards only
        print("\n🃏 Generating enhanced flashcards...")
        flashcards_result = pipeline.generate_crewai_flashcards(str(sample_file))
        
        if flashcards_result.get('status') == 'success':
            print("✓ Enhanced flashcards generated")
        else:
            print(f"✗ Flashcard generation failed: {flashcards_result.get('error')}")
        
        # Generate enhanced quiz only
        print("\n❓ Generating enhanced quiz...")
        quiz_result = pipeline.generate_crewai_quiz(str(sample_file))
        
        if quiz_result.get('status') == 'success':
            print("✓ Enhanced quiz generated")
        else:
            print(f"✗ Quiz generation failed: {quiz_result.get('error')}")
            
    except Exception as e:
        logger.error(f"Focused workflow example failed: {e}")


def example_custom_workflow():
    """Example of using custom CrewAI workflow parameters."""
    print("\n=== CrewAI Custom Workflow Example ===")
    
    try:
        from src.pipeline import StudyAssistantPipeline
        
        pipeline = StudyAssistantPipeline()
        
        if not pipeline.is_crewai_available():
            print("CrewAI not available")
            return
        
        sample_file = Path("data/sample_lecture.pdf")
        if not sample_file.exists():
            print("Sample file not found")
            return
        
        # Custom workflow: Only summaries and flashcards, with quality review
        print("\n⚙️ Running custom workflow (summaries + flashcards)...")
        
        result = pipeline.generate_enhanced_study_materials(
            file_path=str(sample_file),
            content_types=["summaries", "flashcards"],  # Only these types
            workflow_type="focused",                     # Focused workflow
            enable_quality_review=True,                  # Enable quality review
            use_crewai=True
        )
        
        print(f"Custom workflow status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print("✓ Custom workflow completed successfully!")
            
            # Show orchestrator metadata
            metadata = result.get('orchestrator_metadata', {})
            print(f"  Workflow type: {metadata.get('workflow_type')}")
            print(f"  Content types: {metadata.get('content_types_requested')}")
            print(f"  Quality review: {metadata.get('quality_review_enabled')}")
            print(f"  Model used: {metadata.get('model_used')}")
        else:
            print(f"✗ Custom workflow failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Custom workflow example failed: {e}")


def example_api_usage():
    """Example of using CrewAI via API endpoints."""
    print("\n=== CrewAI API Usage Example ===")
    
    try:
        import requests
        import json
        
        # Base URL for the MCP server (adjust if running on different host/port)
        base_url = "http://localhost:5000"
        
        # Check CrewAI status
        print("🔍 Checking CrewAI status...")
        response = requests.get(f"{base_url}/crewai/status")
        
        if response.status_code == 200:
            status = response.json()
            print(f"CrewAI status: {status.get('status')}")
            
            if status.get('status') == 'available':
                print("✓ CrewAI API is ready")
            else:
                print("✗ CrewAI API not available")
                return
        else:
            print(f"✗ Failed to check status: {response.status_code}")
            return
        
        # List available workflows
        print("\n📋 Available workflows:")
        response = requests.get(f"{base_url}/crewai/workflows")
        
        if response.status_code == 200:
            workflows = response.json()
            for workflow in workflows.get('workflows', []):
                description = workflows.get('description', {}).get(workflow, 'No description')
                print(f"  - {workflow}: {description}")
        
        print("\n💡 To use the API:")
        print("1. First upload a file using POST /upload")
        print("2. Then use the file_id with CrewAI endpoints:")
        print("   - POST /crewai/process (comprehensive workflow)")
        print("   - POST /crewai/enhanced-summaries")
        print("   - POST /crewai/enhanced-flashcards") 
        print("   - POST /crewai/enhanced-quiz")
        print("   - POST /crewai/complete-package")
        
        # Example API request body
        example_request = {
            "file_id": "your_uploaded_file_id",
            "workflow_type": "comprehensive",
            "content_types": ["summaries", "flashcards", "quiz"],
            "enable_quality_review": True,
            "model": "default",
            "user_id": "user123"
        }
        
        print(f"\nExample request body for /crewai/process:")
        print(json.dumps(example_request, indent=2))
        
    except ImportError:
        print("requests library not available. Install with: pip install requests")
    except Exception as e:
        logger.error(f"API example failed: {e}")


def example_comparison():
    """Example comparing standard pipeline vs CrewAI enhanced generation."""
    print("\n=== Standard vs CrewAI Comparison Example ===")
    
    try:
        from src.pipeline import StudyAssistantPipeline
        import time
        
        pipeline = StudyAssistantPipeline()
        
        sample_file = Path("data/sample_lecture.pdf")
        if not sample_file.exists():
            print("Sample file not found")
            return
        
        # Standard pipeline generation
        print("\n🔧 Generating with standard pipeline...")
        start_time = time.time()
        
        standard_result = pipeline.generate_enhanced_study_materials(
            file_path=str(sample_file),
            content_types=["summaries"],
            use_crewai=False  # Force standard pipeline
        )
        
        standard_time = time.time() - start_time
        print(f"Standard pipeline completed in {standard_time:.2f} seconds")
        print(f"Method: {standard_result.get('generation_method')}")
        
        # CrewAI enhanced generation (if available)
        if pipeline.is_crewai_available():
            print("\n🤖 Generating with CrewAI enhanced workflow...")
            start_time = time.time()
            
            crewai_result = pipeline.generate_enhanced_study_materials(
                file_path=str(sample_file),
                content_types=["summaries"],
                workflow_type="summaries",
                use_crewai=True
            )
            
            crewai_time = time.time() - start_time
            print(f"CrewAI workflow completed in {crewai_time:.2f} seconds")
            print(f"Method: {crewai_result.get('generation_method')}")
            
            # Compare results
            print(f"\n📊 Comparison:")
            print(f"Standard time: {standard_time:.2f}s")
            print(f"CrewAI time: {crewai_time:.2f}s")
            print(f"Time difference: {crewai_time - standard_time:.2f}s")
            
            if crewai_result.get('orchestrator_metadata'):
                print("CrewAI includes additional features:")
                print("  - Research analysis")
                print("  - Quality review")
                print("  - Multi-agent collaboration")
        else:
            print("CrewAI not available for comparison")
            
    except Exception as e:
        logger.error(f"Comparison example failed: {e}")


if __name__ == "__main__":
    print("CrewAI Integration Examples for Study Assistant")
    print("=" * 50)
    
    # Run all examples
    example_basic_crewai_usage()
    example_focused_workflows() 
    example_custom_workflow()
    example_api_usage()
    example_comparison()
    
    print("\n✅ Examples completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set up your model in models/ directory")
    print("3. Place PDF files in data/ directory")
    print("4. Run the examples with your own files")
    print("5. Start the MCP server: python mcp_server/server.py")
    print("6. Use the web frontend or API endpoints")