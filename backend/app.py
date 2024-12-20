import os
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import matplotlib
from collections import Counter
import numpy as np
matplotlib.use('Agg')  # Set non-GUI backend before importing pyplot
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

genai.configure(api_key="your_api_key")
model = genai.GenerativeModel("gemini-1.5-flash")

# Ensure the storage directory exists
DOCUMENTS_DIR = "retrieved_documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

def extract_text_from_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        cleaned_text = ' '.join(text.split())
        return cleaned_text
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Preprocessing function to clean the document and query (lowercase, remove punctuation, split words)
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.split()

# Naive Bayes Algorithm
def naive_bayes_relevance(doc_tokens, query_tokens):
    doc_tf = Counter(doc_tokens)
    relevance_score = 0
    for word in query_tokens:
        relevance_score += doc_tf.get(word, 0)  # Add frequency of query words in document
    return relevance_score

# BM25 Algorithm
def bm25_relevance(doc_tokens, query_tokens, k1=1.5, b=0.75):
    doc_len = len(doc_tokens)
    avg_doc_len = doc_len  # For simplicity, assuming average document length is the length of this document
    doc_tf = Counter(doc_tokens)
    
    relevance_score = 0
    for word in query_tokens:
        idf = math.log((len(doc_tokens) - doc_tf.get(word, 0) + 0.5) / (doc_tf.get(word, 0) + 0.5) + 1.0)
        tf = doc_tf.get(word, 0)
        relevance_score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))
    return relevance_score

# BSBI Algorithm
def bsbi_relevance(doc_tokens, query_tokens):
    relevance_score = len(set(query_tokens) & set(doc_tokens))  # Intersection of query and document terms
    return relevance_score

# 1. Scraping Top 5 Google Links
def scrape_google_search(query):
    search_url = f"https://www.google.com/search?q={query}&num=10"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if "url?q=" in a["href"] and "webcache" not in a["href"]
    ]
    links = [link.split("url?q=")[1].split("&")[0] for link in links]

    documents = []
    collected_links = []
    for i, link in enumerate(links):
        if len(documents) >= 5:
            break
        try:
            text = extract_text_from_website(link)
            if text.strip() and "An error occurred" not in text:
                documents.append(text)
                collected_links.append(link)
                text_file_path = os.path.join(DOCUMENTS_DIR, f"document_{len(documents)}.txt")
                with open(text_file_path, "w", encoding="utf-8") as text_file:
                    text_file.write(text)
        except Exception as e:
            print(f"Error processing {link}: {e}")

    return documents[:5], collected_links[:5]

# 6. Evaluate Performance
@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get("query", "")
    documents, links = scrape_google_search(query)

    if len(documents) < 5:
        return jsonify({"error": "Failed to retrieve sufficient documents."}), 400

    # Process the query and documents
    query_tokens = preprocess(query)
    documents_tokens = [preprocess(doc) for doc in documents]

    # Calculate relevance scores using all three models
    naive_bayes_scores = [naive_bayes_relevance(doc_tokens, query_tokens) for doc_tokens in documents_tokens]
    bm25_scores = [bm25_relevance(doc_tokens, query_tokens) for doc_tokens in documents_tokens]
    bsbi_scores = [bsbi_relevance(doc_tokens, query_tokens) for doc_tokens in documents_tokens]

    # Calculate average scores for each algorithm
    avg_scores = [
        np.mean(naive_bayes_scores),
        np.mean(bm25_scores),
        np.mean(bsbi_scores)
    ]
    algorithms = ["Naive Bayes", "BM25", "BSBI"]
    best_algorithm = algorithms[np.argmax(avg_scores)]

    # Generate graph
    plt.figure(figsize=(10, 6))
    for scores, name in zip([naive_bayes_scores, bm25_scores, bsbi_scores], algorithms):
        plt.plot(range(len(scores)), scores, label=name)
    plt.xlabel("Document Index")
    plt.ylabel("Relevance Score")
    plt.title("Algorithm Performance on Query")
    plt.legend()

    # Saving to buffer for base64 encoding if necessary
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    # Combine documents and pass to the generative model
    context = "\n\n".join(documents)
    try:
        ai_response = model.generate_content(f"Context: {context}\n\nQuestion: {query}")
        answer = ai_response.text
    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

    return jsonify({
        "best_algorithm": best_algorithm,
        "graph": graph_base64,
        "documents": documents,
        "links": links,
        "naive_bayes_scores": naive_bayes_scores,
        "bm25_scores": bm25_scores,
        "bsbi_scores": bsbi_scores,
        "generative_output": answer
    })


if __name__ == "__main__":
    app.run(debug=True)
