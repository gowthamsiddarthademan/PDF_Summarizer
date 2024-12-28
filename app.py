from flask import Flask, request, jsonify, render_template
from transformers import pipeline, BartTokenizer
import PyPDF2
import os

app = Flask(__name__)

# Load the Hugging Face summarization model and tokenizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

# Function to split text into chunks that fit within the token limit
def chunk_text(text, max_tokens=1024):
    # Tokenize the text
    tokens = tokenizer.encode(text)
    # Split tokens into chunks that do not exceed the max_tokens limit
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    # Decode the token chunks back into text
    return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None

    if request.method == "POST":
        # Get the PDF file from the form
        file = request.files["pdf_file"]
        
        # Check if a file is uploaded
        if file and file.filename.endswith('.pdf'):
            # Read the PDF file
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Split the extracted text into chunks if it's too long
            if len(tokenizer.encode(text)) > 1024:
                text_chunks = chunk_text(text)
            else:
                text_chunks = [text]
            
            # Summarize each chunk and combine the results
            summaries = []
            for chunk in text_chunks:
                chunk_summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
                summaries.append(chunk_summary)
            summary = " ".join(summaries)

    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
