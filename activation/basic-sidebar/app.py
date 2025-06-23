import numpy as np
import matplotlib.pyplot as plt
from shiny.express import input, render, ui

# Page configuration
ui.page_opts(title="Neural Network Activation Functions")

# Define activation functions
def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))  # Clip to prevent overflow

def relu(x):
    return np.maximum(0, x)

def linear(x):
    return x

def softmax(z):
    # For visualization, we'll show how one component varies while others are fixed
    exp_z = np.exp(z - np.max(z))  # For numerical stability
    return exp_z / np.sum(exp_z)

# Sidebar with controls
with ui.sidebar():
    ui.h3("Activation Function Controls")
    
    ui.input_select(
        "activation", 
        "Select Activation Function", 
        choices={
            "sigmoid": "Sigmoid",
            "relu": "ReLU", 
            "linear": "Linear",
            "softmax": "Softmax"
        },
        selected="sigmoid"
    )
    
    ui.input_slider(
        "input_range", 
        "Input Range", 
        min=-20, 
        max=20, 
        value=[-10, 10],
        step=1
    )
    
    ui.input_numeric(
        "num_points",
        "Number of Points",
        value=1000,
        min=100,
        max=5000,
        step=100
    )
    
    # Conditional input for softmax
    ui.input_numeric(
        "softmax_classes",
        "Number of Classes (for Softmax)",
        value=3,
        min=2,
        max=5,
        step=1
    )

# Main content
ui.h2("Activation Function Visualization")

@render.text
def function_info():
    func = input.activation()
    info = {
        "sigmoid": "Sigmoid: σ(x) = 1/(1 + e^(-x)) - Maps input to (0,1) range",
        "relu": "ReLU: f(x) = max(0, x) - Returns 0 for negative inputs, x for positive",
        "linear": "Linear: f(x) = x - Identity function, no transformation",
        "softmax": "Softmax: σ(z_i) = e^(z_i) / Σe^(z_j) - Converts logits to probabilities"
    }
    return info.get(func, "")

@render.plot
def activation_plot():
    func = input.activation()
    x_min, x_max = input.input_range()
    num_points = input.num_points()
    
    # Create figure with custom styling
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if func == "softmax":
        # Special handling for softmax
        num_classes = input.softmax_classes()
        x = np.linspace(x_min, x_max, num_points)
        
        # Create multiple lines showing how each class probability changes
        # as we vary one logit while keeping others at 0
        colors = plt.cm.Set1(np.linspace(0, 1, num_classes))
        
        for i in range(num_classes):
            y_values = []
            for val in x:
                # Create logit vector with one varying component
                z = np.zeros(num_classes)
                z[i] = val  # Vary the i-th component
                s = softmax(z)
                y_values.append(s[i])
            
            ax.plot(x, y_values, label=f'Class {i+1}', color=colors[i], linewidth=2)
        
        ax.set_ylabel('Probability')
        ax.legend()
        ax.set_title(f"Softmax Function ({num_classes} classes)")
        
    else:
        # Handle other activation functions
        x = np.linspace(x_min, x_max, num_points)
        
        if func == "sigmoid":
            y = sigmoid(x)
            color = 'blue'
        elif func == "relu":
            y = relu(x)
            color = 'red'
        elif func == "linear":
            y = linear(x)
            color = 'green'
        
        ax.plot(x, y, color=color, linewidth=2)
        ax.set_ylabel('f(x)')
        ax.set_title(f"{func.capitalize()} Activation Function")
    
    # Styling
    ax.set_xlabel('Input (x)')
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero') 
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    return fig

@render.text  
def current_settings():
    return f"Current range: [{input.input_range()[0]}, {input.input_range()[1]}] with {input.num_points()} points"