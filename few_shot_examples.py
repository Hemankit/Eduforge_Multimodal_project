"""Example input–output pairs for few-shot learning.

These are concrete examples of ContentInput → ContentOutput mappings
that conform (approximately) to the schemas in input_schema.py
and output_schema.py. Can serialize these to JSON and include
in prompts as few-shot demonstrations.
"""

from typing import List, Dict, Any

# Each example is a dict with two keys:
# - "input":  an example ContentInput-like payload
# - "output": an example ContentOutput-like payload

FEW_SHOT_EXAMPLES: List[Dict[str, Any]] = [
    {
        "input": {
            "topic": "Gradient Descent",
            "audience": "beginner",
            "constraints": {
                "max_duration_sec": 180,
                "examples": 2,
                "visual_style": "detailed",
            },
        },
        "output": {
            "learning_objectives": [
                "Understand gradient descent as a method for minimizing a function.",
                "Explain intuitively how taking steps along the negative gradient reduces loss.",
            ],
            "sections": [
                {
                    "title": "What Is Gradient Descent?",
                    "script": "Gradient descent is a method for finding a function's minimum by taking small, repeated steps in the direction that most quickly decreases the function's value. You start from an initial guess, compute the slope (gradient) at that point, and move a little bit in the opposite direction of that slope.",
                    "visual_plan": "Show a 2D curve with a ball rolling downhill along the loss surface, highlighting the current point and direction of steepest descent.",
                    "duration_sec": 60,
                    "key_terms": ["loss function", "gradient", "learning rate"],
                    "diagram_type": "flowchart",
                    "mermaid_source": """flowchart TD
    A[Start: Initialize random weights] --> B[Compute loss]
    B --> C[Calculate gradient]
    C --> D{Gradient close to zero?}
    D -->|No| E[Update weights: w = w - α∇L]
    E --> B
    D -->|Yes| F[Stop: Found minimum]""",
                },
                {
                    "title": "Everyday Intuition for Gradient Descent",
                    "script": "Imagine you are standing on a foggy hill and you want to reach the bottom. You cannot see far, but you can feel the slope under your feet. If you always take a step in the direction that feels most downhill, you will gradually move toward a low point. Gradient descent works the same way in math: it uses the local slope to decide which way to move next.",
                    "visual_plan": "Illustrate a person on a hill taking small steps downhill with arrows indicating the direction of steepest descent.",
                    "duration_sec": 70,
                    "key_terms": ["steepest descent", "local minimum"],
                },
            ],
            "prerequisites": ["Basic understanding of functions", "Concept of a graph"],
            # total_duration_sec would normally be computed by the model_validator
            "total_duration_sec": 130,
        },
    },
    {
        "input": {
            "topic": "Overfitting in Machine Learning",
            "audience": "intermediate",
            "constraints": {
                "max_duration_sec": 300,
                "examples": 2,
                "visual_style": "minimal",
            },
        },
        "output": {
            "learning_objectives": [
                "Describe what overfitting is and why it occurs in machine learning models.",
                "Compare overfitting to underfitting using intuitive and graphical explanations.",
            ],
            "sections": [
                {
                    "title": "Defining Overfitting and Underfitting",
                    "script": "Overfitting happens when a model learns patterns that are too specific to the training data, including noise, so it performs well on seen data but poorly on new data. Underfitting is the opposite problem: the model is too simple to capture important patterns, so it performs poorly even on training data.",
                    "visual_plan": "Side-by-side plots: one model that is too simple, one that fits training points perfectly with a wiggly curve, and one with a balanced fit.",
                    "duration_sec": 80,
                    "key_terms": ["training data", "generalization", "underfitting"],
                },
                {
                    "title": "Examples and Prevention of Overfitting",
                    "script": "A classic example of overfitting is a high-degree polynomial that passes through every training point but oscillates wildly between them. To prevent overfitting, we can use techniques such as regularization, collecting more data, or early stopping based on validation performance.",
                    "visual_plan": "Show a noisy dataset with a smooth line, an overly complex curve, and a regularized curve that captures the main trend.",
                    "duration_sec": 90,
                    "key_terms": ["regularization", "validation set", "early stopping"],
                },
            ],
            "prerequisites": ["Basic supervised learning", "Train/test split"],
            "total_duration_sec": 170,
        },
    },
    {
        "input": {
            "topic": "Binary Search",
            "audience": "beginner",
            "constraints": {
                "max_duration_sec": 150,
                "examples": 1,
                "visual_style": "animated",
            },
        },
        "output": {
            "learning_objectives": [
                "Explain the idea of binary search on a sorted list.",
                "Trace the steps of binary search on a small example.",
            ],
            "sections": [
                {
                    "title": "Idea of Binary Search",
                    "script": "Binary search is a fast way to find an item in a sorted list. Instead of checking every element one by one, you repeatedly look at the middle element and decide whether the target must be to the left or right, cutting the search space in half each time.",
                    "visual_plan": "Show a horizontal array of sorted numbers with a moving highlight that jumps to the middle, then to a half, then to a quarter.",
                    "duration_sec": 60,
                    "key_terms": ["sorted array", "midpoint", "search space"],
                },
                {
                    "title": "Step-by-Step Example",
                    "script": "Suppose you search for the number 23 in the sorted list [3, 8, 12, 17, 23, 31, 39]. First, check the middle element (17). Since 23 is larger, you ignore the left half. Next, look at the middle of the remaining right half, which is 31. Because 23 is smaller, you move left to 23 and find the target.",
                    "visual_plan": "Animate brackets shrinking around the portion of the list still under consideration, highlighting comparisons at each step.",
                    "duration_sec": 70,
                    "key_terms": ["comparison", "logarithmic time"],
                },
            ],
            "prerequisites": ["Understanding of sorted lists"],
            "total_duration_sec": 130,
        },
    },
    {
        "input": {
            "topic": "Backpropagation",
            "audience": "advanced",
            "constraints": {
                "max_duration_sec": 420,
                "examples": 2,
                "visual_style": "detailed",
            },
        },
        "output": {
            "learning_objectives": [
                "Derive the backpropagation algorithm for a simple feedforward neural network.",
                "Interpret gradients as signals flowing backward through the network.",
            ],
            "sections": [
                {
                    "title": "Setting Up the Network and Loss",
                    "script": "Consider a feedforward neural network with one hidden layer and a differentiable loss function. Each neuron computes a weighted sum of its inputs followed by a nonlinearity. Our goal is to compute how a small change in each weight affects the final loss value so that we can adjust the weights to reduce the loss.",
                    "visual_plan": "Diagram of a small feedforward network with labeled weights, activations, and loss at the output node.",
                    "duration_sec": 90,
                    "key_terms": ["feedforward network", "loss function", "activation"],
                },
                {
                    "title": "Gradient Flow and Chain Rule",
                    "script": "Backpropagation applies the chain rule of calculus systematically through the network. Starting from the loss at the output layer, we compute gradients with respect to each neuron's output, then propagate these gradients backward to obtain gradients with respect to weights and inputs. This backward pass reuses intermediate quantities from the forward pass, making the computation efficient.",
                    "visual_plan": "Show arrows carrying gradient values from the output layer back through hidden layers, with annotations of partial derivatives.",
                    "duration_sec": 120,
                    "key_terms": ["chain rule", "gradient", "backward pass"],
                },
            ],
            "prerequisites": ["Multivariable calculus", "Matrix notation", "Forward pass in neural networks"],
            "total_duration_sec": 210,
        },
    },
    {
        "input": {
            "topic": "Confusion Matrix in Classification",
            "audience": "intermediate",
            "constraints": {
                "max_duration_sec": 240,
                "examples": 1,
                "visual_style": "detailed",
            },
        },
        "output": {
            "learning_objectives": [
                "Define a confusion matrix and its main components.",
                "Use a small example to compute accuracy, precision, and recall from a confusion matrix.",
            ],
            "sections": [
                {
                    "title": "Understanding the Confusion Matrix",
                    "script": "A confusion matrix summarizes how often a classification model's predictions match the true labels. For binary classification, it tracks true positives, true negatives, false positives, and false negatives. Each cell counts how many examples fall into that category.",
                    "visual_plan": "Show a 2x2 table labeled with TP, TN, FP, FN, with arrows to simple definitions.",
                    "duration_sec": 80,
                    "key_terms": ["true positive", "false negative", "binary classification"],
                },
                {
                    "title": "Metrics From the Confusion Matrix",
                    "script": "Given a confusion matrix, you can compute common metrics. Accuracy measures the fraction of all predictions that are correct. Precision focuses on how many predicted positives are truly positive, while recall focuses on how many actual positives were correctly identified. These metrics help you understand different aspects of model performance.",
                    "visual_plan": "Show formulas for accuracy, precision, and recall next to a small numeric confusion matrix example.",
                    "duration_sec": 90,
                    "key_terms": ["accuracy", "precision", "recall"],
                },
            ],
            "prerequisites": ["Basic classification tasks", "Notion of true/false predictions"],
            "total_duration_sec": 170,
        },
    },
]
