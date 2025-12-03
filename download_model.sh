#!/bin/bash

# Model Download Helper Script
# This script helps download GGUF models for the Study Assistant

set -e

MODELS_DIR="$(dirname "$0")/models"
cd "$MODELS_DIR"

echo "🚀 Study Assistant Model Downloader"
echo "======================================="
echo ""

# Function to download with progress
download_model() {
    local url="$1"
    local filename="$2"
    local description="$3"
    
    echo "📥 Downloading: $description"
    echo "📁 File: $filename"
    echo "🔗 URL: $url"
    echo ""
    
    if command -v curl >/dev/null 2>&1; then
        curl -L --progress-bar -o "$filename" "$url"
    elif command -v wget >/dev/null 2>&1; then
        wget --progress=bar:force -O "$filename" "$url"
    else
        echo "❌ Error: Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    echo "✅ Downloaded: $filename"
    echo "📊 Size: $(du -h "$filename" | cut -f1)"
    echo ""
}

# Model options
echo "Available models:"
echo "1. Phi-3 Mini (1-2GB) - Fast, good for testing"
echo "2. Mistral 7B (4GB) - Balanced performance"
echo "3. Custom URL - Enter your own model URL"
echo ""

read -p "Choose a model (1-3): " choice

case $choice in
    1)
        echo "Selected: Phi-3 Mini"
        download_model \
            "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf" \
            "phi-3-mini-4k-instruct.Q4_K_M.gguf" \
            "Microsoft Phi-3 Mini 4K Instruct (Q4)"
        
        echo "📝 To use this model, update config/config.yaml:"
        echo "   llm:"
        echo "     local:"
        echo "       model: \"phi-3-mini-4k-instruct.Q4_K_M\""
        ;;
    2)
        echo "Selected: Mistral 7B"
        download_model \
            "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf" \
            "mistral-7b-instruct-v0.2.Q4_K_M.gguf" \
            "Mistral 7B Instruct v0.2 (Q4_K_M)"
        
        echo "📝 This model matches the default config, no changes needed!"
        ;;
    3)
        read -p "Enter model URL: " custom_url
        read -p "Enter filename (with .gguf extension): " custom_filename
        
        if [[ ! "$custom_filename" =~ \.gguf$ ]]; then
            custom_filename="${custom_filename}.gguf"
        fi
        
        download_model "$custom_url" "$custom_filename" "Custom Model"
        
        model_name="${custom_filename%.gguf}"
        echo "📝 To use this model, update config/config.yaml:"
        echo "   llm:"
        echo "     local:"
        echo "       model: \"$model_name\""
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Model download complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test the setup: python src/cli.py --help"
echo "2. Process a document: python src/cli.py process data/sample_lecture.pdf"
echo "3. Try CrewAI: python src/cli.py process data/sample_lecture.pdf --use-crewai"
echo ""
echo "📁 Models directory contents:"
ls -lh *.gguf 2>/dev/null || echo "   (No .gguf files found)"