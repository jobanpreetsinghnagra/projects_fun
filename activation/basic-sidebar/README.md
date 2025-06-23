# Activation Functions Visualizer

A Shiny web application for visualizing and exploring neural network activation functions interactively.

## Features

- **Four Activation Functions**: Sigmoid, ReLU, Linear, and Softmax
- **Interactive Controls**: Adjust input ranges, resolution, and parameters in real-time
- **Educational Tool**: Perfect for learning how different activation functions behave

## Activation Functions

| Function | Description |
|----------|-------------|
| **Sigmoid** | Maps inputs to (0,1) range - commonly used in binary classification |
| **ReLU** | Returns max(0,x) - most popular in hidden layers |
| **Linear** | Identity function f(x)=x - used in regression output layers |
| **Softmax** | Converts logits to probability distribution - used in multi-class classification |

## Usage

1. Select an activation function from the dropdown
2. Adjust the input range using the slider
3. For Softmax: specify number of classes to visualize
4. Watch the plot update in real-time

## Requirements

```bash
pip install shiny numpy matplotlib
```

## Run the App

```bash
shiny run app.py
```

Navigate to `http://localhost:8000` to use the application.