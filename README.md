# Stock Stock: Financial Analysis System

## Overview

"Stock Stock" is a cutting-edge financial analysis system, harnessing the power of Big Data to provide deep market insights. This project integrates both structured and unstructured data to offer valuable stock insights, using a combination of PostgreSQL for structured financial data and MongoDB with Llama 2 for unstructured earnings call scripts.

## Team Members

- Benjamin Tan
- Nien-Ting Lee
- Shashvat Joshi
- Siyuan Zhu
- Wenxuan Wu
- Zhiying Li

## Project Structure

### PostgreSQL Part
The PostgreSQL part of the project handles structured financial data, including:

- Historical prices
- Financial ratios
- Cash flow statements
- Income statements
- Balance sheets
- Insider trading statistics
- Revenue segmentation (both product and geographical)

This data is extracted using Python scripts from the Financial Modelling Prep API and stored in a star schema in PostgreSQL. 

### MongoDB and LLM Part
The MongoDB and LLM (Large Language Model) part, hosted on our group member's GitHub repository [here](https://github.com/BenjaminTanYuDa/Generative-AI-RAG-with-Llama2), handles unstructured data, primarily earnings call scripts. This part includes:

- Extracting and loading earnings call text data into MongoDB
- Transforming text data into vectors using an embedding model
- Implementing sentiment analysis via Llama 2

## Technology Stack

- **PostgreSQL**: For storing and managing structured financial data.
- **MongoDB**: For storing and managing unstructured earnings call scripts data.
- **Llama 2**: For sentiment analysis and generating natural language insights.
- **Python**: For data extraction, transformation, and loading (ETL) processes.
- **Streamlit**: For the front-end dashboard to present data insights.
