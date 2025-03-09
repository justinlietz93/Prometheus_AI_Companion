#!/usr/bin/env python3
"""
Prometheus AI Prompt Extractor

This script extracts prompts from existing Python files with generate_*_prompt functions,
converts them to JSON format, and saves them in the prompt_library/prompts directory.
Handles syntax errors in prompt files such as missing commas in dictionaries.
"""

import os
import re
import json
import importlib.util
import sys
import ast
import glob

# Directory for storing extracted prompts
PROMPT_LIBRARY_DIR = "prompt_library/prompts"

def extract_prompts_directly_from_content(content, scenario):
    """Extract prompts directly from file content using regex - works even with syntax errors"""
    prompts = {}
    description = ""
    
    # Try to find a description
    description_match = re.search(r'description["\']?\s*:\s*["\']([^"\']+)["\']', content)
    if description_match:
        description = description_match.group(1)
    else:
        description = f"{scenario.replace('_', ' ').title()} Prompts"
    
    # Look for the prompts dictionary definition
    dict_match = re.search(r'prompts\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if dict_match:
        dict_content = dict_match.group(1)
        
        # Extract key-value pairs regardless of comma presence
        # This pattern looks for digit followed by colon followed by quoted text
        pattern = r'(\d+)\s*:\s*["\']([^"\']+)["\']'
        
        # Find all matches
        matches = re.findall(pattern, dict_content)
        for level, prompt_text in matches:
            prompts[int(level)] = prompt_text
            
    return prompts, description

def extract_prompts_from_file(file_path):
    """Extract prompts from a Python file and return them as a dictionary"""
    try:
        # Extract the scenario name from the filename or the function name
        filename = os.path.basename(file_path)
        
        # Try to extract scenario from function definition
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Look for generate_*_prompt function to get the scenario name
        function_match = re.search(r'def\s+generate_([a-zA-Z0-9_]+)_prompt', content)
        if function_match:
            scenario = function_match.group(1)
        elif filename.endswith("_prompt.py"):
            scenario = filename.replace("_prompt.py", "")
        else:
            # For files like api.py, use the filename
            scenario = filename.replace(".py", "")
        
        # First try direct extraction (best for files with syntax errors)
        prompts, description = extract_prompts_directly_from_content(content, scenario)
        
        # If we couldn't get prompts, try other methods
        if not prompts:
            # Try to import the module (may fail due to syntax errors)
            try:
                # Fix common syntax errors in the content for execution
                fixed_content = content
                
                # Add missing commas in dictionary definitions
                dict_match = re.search(r'prompts\s*=\s*\{(.*?)\}', fixed_content, re.DOTALL)
                if dict_match:
                    dict_content = dict_match.group(1)
                    # Add commas after each line that doesn't end with a comma
                    fixed_dict = re.sub(r'("[^"]*")\s*$', r'\1,', dict_content, flags=re.MULTILINE)
                    fixed_content = fixed_content.replace(dict_match.group(1), fixed_dict)
                
                # Create a temporary file with fixed content
                temp_file = f"{file_path}.temp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Try to import the fixed module
                try:
                    spec = importlib.util.spec_from_file_location(filename, temp_file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[filename] = module
                    spec.loader.exec_module(module)
                    
                    # Look for the generate_*_prompt function
                    function_name = f"generate_{scenario}_prompt"
                    if hasattr(module, function_name):
                        prompt_function = getattr(module, function_name)
                        for level in range(1, 11):
                            try:
                                prompt = prompt_function(level)
                                if isinstance(prompt, str) and not prompt.startswith("Error:") and not prompt.startswith("Invalid"):
                                    prompts[level] = prompt
                            except:
                                pass
                finally:
                    # Clean up the temporary file
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            except Exception as e:
                print(f"Warning: Could not import module {file_path}: {str(e)}")
                # Already have prompts from direct extraction
        
        # If we didn't get any valid prompts, the extraction failed
        if not prompts:
            print(f"Warning: No valid prompts found in {file_path}")
            return None
            
        return {
            "name": scenario,
            "description": description,
            "prompts": {str(k): v for k, v in prompts.items()}
        }
    except Exception as e:
        print(f"Error extracting prompts from {file_path}: {str(e)}")
        return None

def save_prompt_to_json(prompt_data):
    """Save prompt data to a JSON file"""
    if not prompt_data:
        return False
        
    try:
        # Create the output file path
        output_file = os.path.join(PROMPT_LIBRARY_DIR, f"{prompt_data['name']}.json")
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(prompt_data, f, indent=2)
            
        print(f"Saved prompts to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving prompts to JSON: {str(e)}")
        return False

def find_prompt_files():
    """Find all Python files with generate_*_prompt functions or prompt in the name"""
    prompt_files = []
    
    # Get absolute path of current directory
    root_dir = os.path.abspath(".")
    
    # First, prioritize remaining *_prompt.py files
    prompt_py_files = glob.glob(os.path.join(root_dir, "*_prompt.py"))
    for file_path in prompt_py_files:
        if os.path.isfile(file_path):
            prompt_files.append(file_path)
    
    # Then check for other Python files that might contain prompts
    all_py_files = glob.glob(os.path.join(root_dir, "*.py"))
    motivation_dir = os.path.join(root_dir, "motivation")
    if os.path.exists(motivation_dir):
        motivation_files = glob.glob(os.path.join(motivation_dir, "*.py"))
        all_py_files.extend(motivation_files)
    
    # Check each file for prompt-related content
    for file_path in all_py_files:
        # Skip if we already added it or if it's one of our script files
        basename = os.path.basename(file_path)
        if file_path in prompt_files or basename in ["extract_prompts.py", "prompt_generator_app.py", "test_prompt_library.py", "prompt_generator_qt.py"]:
            continue
            
        try:
            # Check file content for prompt functions or dictionaries
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                if re.search(r'def\s+generate_[a-zA-Z0-9_]+_prompt', content) or \
                   "prompts = {" in content:
                    prompt_files.append(file_path)
        except Exception as e:
            print(f"Warning: Could not check {file_path}: {str(e)}")
    
    return prompt_files

def main():
    """Extract prompts from all prompt files and save them to JSON"""
    # Ensure the output directory exists
    os.makedirs(PROMPT_LIBRARY_DIR, exist_ok=True)
    
    # Find all prompt files
    prompt_files = find_prompt_files()
    print(f"Found {len(prompt_files)} files with prompt generation functions")
    
    # Display all found files
    for file in prompt_files:
        print(f" - {os.path.basename(file)}")
    
    # Process each file
    success_count = 0
    failed_files = []
    successful_files = []
    
    for file_path in prompt_files:
        print(f"Processing {os.path.basename(file_path)}...")
        
        # Extract prompts
        prompt_data = extract_prompts_from_file(file_path)
        
        # Save to JSON if extraction was successful
        if prompt_data and save_prompt_to_json(prompt_data):
            success_count += 1
            successful_files.append(file_path)
        else:
            failed_files.append(os.path.basename(file_path))
    
    # Report results
    print(f"\nExtraction complete. Successfully processed {success_count} of {len(prompt_files)} files.")
    
    if failed_files:
        print(f"Failed to process {len(failed_files)} files:")
        for file in failed_files:
            print(f" - {file}")
    
    # Ask if the user wants to delete the original files
    if success_count > 0:
        print("\nWould you like to delete the original prompt files? (yes/no)")
        response = input().strip().lower()
        
        if response == "yes" or response == "y":
            deleted_count = 0
            for file_path in successful_files:
                try:
                    os.remove(file_path)
                    print(f"Deleted {os.path.basename(file_path)}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {os.path.basename(file_path)}: {str(e)}")
            
            print(f"\nDeleted {deleted_count} of {success_count} successfully processed files.")

if __name__ == "__main__":
    main() 