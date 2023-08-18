# SentinelPost
A Personalized, Safe AI News Platform

SentinelPost is an open-source project aimed at building a personalized, unbiased news platform that leverages the power of AI. Our primary objective is to provide users with curated, summarized, and safe news content based on their preferences. Everyone is welcome to contribute to this project to make news consumption more engaging for everyone!

Key Features

Multimodal Summarization: The system leverages BART for text summarization and Stable Diffusion for a visual summary (thumbnail or short video clip) generation.

Toxic Content Detection and Removal: A toxicity detection module is integrated into the pipeline to ensure content safety by filtering out toxic text, image, or video content.

Content Curation and Personalization: The platform utilizes a recommendation system to curate news feeds personalized to each user's preferences, interests, and past behavior. (Future state)

## Prerequisites

Make sure you have the following installed on your system:
- Python (version 3.10.6 or higher (not 3.11+))
- pip (Python package manager)
  
Important: The current code version is designed exclusively for CUDA, enabling image generation module execution in local environments. Ensure that both CUDA version 11.7 and CUDNN are installed. Please be aware that PyTorch Release 22.05 is currently compatible only with CUDA 11.7.

## Getting Started

1. Clone the Repository
2. Navigate to the Project Directory - Change your current working directory to the project folder.
3. Create and activate a venv
4. Install requirements and run the app with streamlit run main.py

## Contributing

Feel free to contribute to this project by submitting pull requests!
