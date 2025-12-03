#!/usr/bin/env python3
"""
CrewAI CLI for Study Assistant
Simple command-line interface for testing CrewAI enhanced generation.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import StudyAssistantPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_crewai_status(pipeline):
    """Check and display CrewAI status."""
    print("🔍 Checking CrewAI status...")
    
    if pipeline.is_crewai_available():
        print("✅ CrewAI is available and ready")
        status = pipeline.get_crewai_status()
        
        print(f"Model: {status.get('llm_model', 'unknown')}")
        print(f"Default workflow: {status.get('default_workflow')}")
        print(f"Quality review: {status.get('quality_review_enabled')}")
        
        agents = status.get('agents_available', {})
        print("Agents available:")
        for agent, available in agents.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {agent}")
        
        return True
    else:
        print("❌ CrewAI is not available")
        print("Make sure you have installed the CrewAI dependencies:")
        print("  pip install crewai langchain langchain-community")
        return False


def generate_materials(pipeline, file_path, content_types, workflow_type, output_file=None):
    """Generate study materials using CrewAI."""
    print(f"\n🤖 Generating {', '.join(content_types)} using {workflow_type} workflow...")
    print(f"Processing file: {file_path}")
    
    try:
        result = pipeline.generate_enhanced_study_materials(
            file_path=file_path,
            content_types=content_types,
            workflow_type=workflow_type,
            enable_quality_review=True,
            use_crewai=True
        )
        
        if result.get('status') == 'success':
            print("✅ Generation completed successfully!")
            
            # Display summary
            method = result.get('generation_method', 'unknown')
            print(f"Generation method: {method}")
            
            if 'orchestrator_metadata' in result:
                metadata = result['orchestrator_metadata']
                print(f"Model used: {metadata.get('model_used', 'unknown')}")
                print(f"Quality review: {'enabled' if metadata.get('quality_review_enabled') else 'disabled'}")
            
            # Show generated content types
            materials = result.get('generated_materials', {})
            print("Generated materials:")
            for material_type in materials:
                print(f"  ✅ {material_type}")
            
            # Save results if output file specified
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to: {output_file}")
            
            return True
            
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return False


def list_workflows(pipeline):
    """List available CrewAI workflows."""
    print("\n📋 Available CrewAI workflows:")
    
    if not pipeline.is_crewai_available():
        print("CrewAI not available")
        return
    
    try:
        workflows = pipeline.crewai_orchestrator.get_supported_workflows()
        content_types = pipeline.crewai_orchestrator.get_supported_content_types()
        
        for workflow in workflows:
            print(f"  • {workflow}")
        
        print(f"\n📄 Supported content types: {', '.join(content_types)}")
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="CrewAI CLI for Study Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check CrewAI status
  python crewai_cli.py --status
  
  # List available workflows
  python crewai_cli.py --list-workflows
  
  # Generate complete study package
  python crewai_cli.py --file data/lecture.pdf --complete
  
  # Generate only summaries with comprehensive workflow
  python crewai_cli.py --file data/lecture.pdf --content summaries --workflow comprehensive
  
  # Generate flashcards and quiz with output file
  python crewai_cli.py --file data/lecture.pdf --content flashcards quiz --output results.json
        """
    )
    
    # File input
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Input file path (PDF, MP3, etc.)'
    )
    
    # Content types
    parser.add_argument(
        '--content', '-c',
        nargs='+',
        choices=['summaries', 'flashcards', 'quiz'],
        default=['summaries', 'flashcards', 'quiz'],
        help='Content types to generate (default: all)'
    )
    
    # Workflow type
    parser.add_argument(
        '--workflow', '-w',
        choices=['comprehensive', 'focused', 'summaries', 'flashcards', 'quiz'],
        default='comprehensive',
        help='CrewAI workflow type (default: comprehensive)'
    )
    
    # Output file
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output JSON file for results'
    )
    
    # Status and info commands
    parser.add_argument(
        '--status',
        action='store_true',
        help='Check CrewAI status'
    )
    
    parser.add_argument(
        '--list-workflows',
        action='store_true',
        help='List available workflows'
    )
    
    # Convenience flags
    parser.add_argument(
        '--complete',
        action='store_true',
        help='Generate complete study package (all content types)'
    )
    
    # Model selection
    parser.add_argument(
        '--model', '-m',
        type=str,
        help='Model name to use (optional)'
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    print("🚀 Initializing Study Assistant Pipeline...")
    try:
        pipeline = StudyAssistantPipeline()
        print("✅ Pipeline initialized")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return 1
    
    # Load specific model if requested
    if args.model:
        print(f"🔄 Loading model: {args.model}")
        try:
            pipeline.reload_model(args.model)
            print(f"✅ Model loaded: {args.model}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return 1
    
    # Handle different commands
    if args.status:
        check_crewai_status(pipeline)
        return 0
    
    if args.list_workflows:
        list_workflows(pipeline)
        return 0
    
    # Generation commands require a file
    if not args.file:
        print("❌ No input file specified. Use --file to specify a file.")
        print("Use --help for more information.")
        return 1
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 1
    
    # Check CrewAI availability
    if not check_crewai_status(pipeline):
        return 1
    
    # Determine content types
    if args.complete:
        content_types = ['summaries', 'flashcards', 'quiz']
    else:
        content_types = args.content
    
    # Generate materials
    success = generate_materials(
        pipeline=pipeline,
        file_path=str(file_path),
        content_types=content_types,
        workflow_type=args.workflow,
        output_file=args.output
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())