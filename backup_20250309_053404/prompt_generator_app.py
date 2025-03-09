#!/usr/bin/env python3
"""
Prompt Generator Application

A GUI application for selecting and generating prompts with different
urgency levels using the prompt library.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Ensure prompt_library is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the prompt library
from prompt_library.prompt_loader import PromptLibrary

class PromptGeneratorApp:
    """GUI Application for generating prompts with different urgency levels"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Prompt Generator")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)
        
        # Load the prompt library
        self.prompt_library = PromptLibrary()
        self.prompt_types = self.prompt_library.get_prompt_types()
        
        # Dictionary to map display names to actual prompt type names
        self.display_to_type = {}
        
        self.urgency_level = tk.IntVar(value=5)  # Default urgency level
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the application widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for selection
        left_panel = ttk.LabelFrame(main_frame, text="Prompt Selection", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Prompt type selection
        prompt_selection_frame = ttk.Frame(left_panel)
        prompt_selection_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(prompt_selection_frame, text=f"Available Prompt Types ({len(self.prompt_types)}):").pack(anchor=tk.W)
        
        # Scrollable list of prompt types
        prompt_scroll = ttk.Scrollbar(prompt_selection_frame)
        prompt_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.prompt_listbox = tk.Listbox(prompt_selection_frame, selectmode=tk.MULTIPLE,
                                        yscrollcommand=prompt_scroll.set, font=("Arial", 10))
        self.prompt_listbox.pack(fill=tk.BOTH, expand=True)
        prompt_scroll.config(command=self.prompt_listbox.yview)
        
        # Sort prompt types alphabetically for better display
        sorted_prompt_types = sorted(self.prompt_types)
        
        # Populate the listbox with prompt types
        for prompt_type in sorted_prompt_types:
            # Get the description for this prompt type
            description = self.prompt_library.get_prompt_description(prompt_type)
            display_text = f"{prompt_type.replace('_', ' ').title()}"
            
            # Store mapping of display name to actual prompt type
            self.display_to_type[display_text] = prompt_type
            
            # Add to listbox
            self.prompt_listbox.insert(tk.END, display_text)
        
        # Add select all/none buttons
        select_buttons_frame = ttk.Frame(left_panel)
        select_buttons_frame.pack(fill=tk.X, pady=(5, 10))
        
        select_all_button = ttk.Button(select_buttons_frame, text="Select All", 
                                     command=self.select_all_prompts)
        select_all_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        select_none_button = ttk.Button(select_buttons_frame, text="Select None", 
                                      command=self.select_no_prompts)
        select_none_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Urgency level slider
        urgency_frame = ttk.LabelFrame(left_panel, text="Urgency Level", padding="10")
        urgency_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(urgency_frame, text="Low").pack(side=tk.LEFT)
        urgency_slider = ttk.Scale(urgency_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                  variable=self.urgency_level)
        urgency_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(urgency_frame, text="High").pack(side=tk.LEFT)
        
        # Current urgency level display
        self.urgency_display = ttk.Label(urgency_frame, text="5")
        self.urgency_display.pack(side=tk.LEFT, padx=(5, 0))
        urgency_slider.config(command=self.update_urgency_display)
        
        # Buttons frame
        buttons_frame = ttk.Frame(left_panel)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Generate button
        generate_button = ttk.Button(buttons_frame, text="Generate Prompts", 
                                   command=self.generate_prompts)
        generate_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        # Copy button
        copy_button = ttk.Button(buttons_frame, text="Copy to Clipboard", 
                               command=self.copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Right panel for output
        right_panel = ttk.LabelFrame(main_frame, text="Generated Prompts", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, 
                                                   width=50, height=30, font=("Arial", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
    
    def select_all_prompts(self):
        """Select all prompt types in the listbox"""
        self.prompt_listbox.select_set(0, tk.END)
    
    def select_no_prompts(self):
        """Deselect all prompt types in the listbox"""
        self.prompt_listbox.selection_clear(0, tk.END)
        
    def update_urgency_display(self, value):
        """Update the urgency level display when slider is moved"""
        level = int(float(value))
        self.urgency_display.config(text=str(level))
        
    def generate_prompts(self):
        """Generate prompts based on selected types and urgency level"""
        # Get selected items
        selected_indices = self.prompt_listbox.curselection()
        
        # Clear the output text
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        
        if not selected_indices:
            self.output_text.insert(tk.END, "Please select at least one prompt type.")
            self.output_text.config(state=tk.DISABLED)
            return
        
        # Get the urgency level
        level = self.urgency_level.get()
        
        # Generate prompts for each selected type
        for index in selected_indices:
            # Get the display text
            display_text = self.prompt_listbox.get(index)
            
            # Convert to actual prompt type using our mapping dictionary
            prompt_type = self.display_to_type.get(display_text)
            if not prompt_type:
                # Fallback - convert the display text to a format similar to our prompt types
                prompt_type = display_text.lower().replace(' ', '_')
            
            # Get the description
            description = self.prompt_library.get_prompt_description(prompt_type)
            
            # Get the prompt
            prompt = self.prompt_library.get_prompt(prompt_type, level)
            
            # Add to output
            self.output_text.insert(tk.END, f"--- {display_text} (Level {level}) ---\n\n")
            if description:
                self.output_text.insert(tk.END, f"{description}\n\n")
            self.output_text.insert(tk.END, f"{prompt}\n\n")
            
        self.output_text.config(state=tk.DISABLED)
        
    def copy_to_clipboard(self):
        """Copy the generated prompts to the clipboard"""
        if not self.output_text.get(1.0, tk.END).strip():
            messagebox.showinfo("Copy to Clipboard", "Nothing to copy. Generate prompts first.")
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        messagebox.showinfo("Copy to Clipboard", "Prompts copied to clipboard!")

def main():
    """Run the prompt generator application"""
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 