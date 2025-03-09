import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import importlib.util
import sys
import os

# Add the project root to Python path so we can import the prompt_library
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from prometheus_prompt_generator.data.prompt_manager import PromptManager
except ImportError:
    print("Error importing PromptManager. Fixing import paths...")
    from prometheus_prompt_generator.data.fix_imports import fix_import_paths
    fix_import_paths()
    from prometheus_prompt_generator.data.prompt_manager import PromptManager

class PromptGeneratorApp:
    """GUI Application for generating prompts at different urgency levels"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Prompt Generator")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Load prompt manager
        self.prompt_manager = PromptManager()
        self.prompt_manager.load_all_prompts()
        self.prompt_types = self.prompt_manager.get_available_prompt_types()
        
        self.selected_prompts = []
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
        
        ttk.Label(prompt_selection_frame, text="Available Prompt Types:").pack(anchor=tk.W)
        
        # Scrollable list of checkboxes for prompt types
        prompt_scroll = ttk.Scrollbar(prompt_selection_frame)
        prompt_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.prompt_listbox = tk.Listbox(prompt_selection_frame, selectmode=tk.MULTIPLE,
                                        yscrollcommand=prompt_scroll.set)
        self.prompt_listbox.pack(fill=tk.BOTH, expand=True)
        prompt_scroll.config(command=self.prompt_listbox.yview)
        
        # Populate the listbox with prompt types
        for prompt_type in self.prompt_types:
            self.prompt_listbox.insert(tk.END, prompt_type)
        
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
                                                   width=50, height=30)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
        
    def update_urgency_display(self, value):
        """Update the urgency level display when slider is moved"""
        level = int(float(value))
        self.urgency_display.config(text=str(level))
        
    def generate_prompts(self):
        """Generate prompts based on selected types and urgency level"""
        # Get selected prompt types
        selected_indices = self.prompt_listbox.curselection()
        selected_types = [self.prompt_types[i] for i in selected_indices]
        
        # Clear the output text
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        
        if not selected_types:
            self.output_text.insert(tk.END, "Please select at least one prompt type.")
            self.output_text.config(state=tk.DISABLED)
            return
        
        # Get the urgency level
        level = self.urgency_level.get()
        
        # Generate prompts for each selected type
        for prompt_type in selected_types:
            prompt = self.prompt_manager.get_prompt(prompt_type, level)
            
            # Add to output
            self.output_text.insert(tk.END, f"--- {prompt_type.upper()} PROMPT (Level {level}) ---\n\n")
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

if __name__ == "__main__":
    # Make sure importlib.util is available (Python 3.5+)
    if importlib.util is None:
        print("This application requires Python 3.5 or newer.")
        sys.exit(1)
        
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop() 