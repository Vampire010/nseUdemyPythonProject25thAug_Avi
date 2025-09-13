import os
import re
import sys
import pandas as pd
import docx
import PyPDF2
from PIL import Image
import pytesseract
from transformers import pipeline
from pdf2image import convert_from_path
import time  # Import time module for execution time measurement
from datetime import datetime  # Import datetime for timestamp generation


# -------------------------
# Load FinBERT model
# -------------------------
finbert_nlp = pipeline("sentiment-analysis",
                       model="yiyanghkust/finbert-tone",
                       tokenizer="yiyanghkust/finbert-tone")

# -------------------------
# Keyword dictionary
# -------------------------
POSITIVE_KEYWORDS = {
    "profit", "growth", "increase", "gain", "expansion",
    "dividend", "bonus", "approval", "surplus", "record",
    "upgrade", "buyback", "contract", "acquisition",
    "allotment", "revenue", "order win", "clearance","no penalty"
}

NEGATIVE_KEYWORDS = {
    "loss", "decline", "drop", "decrease", "penalty",
    "lawsuit", "fine", "default", "bankruptcy", "insolvency",
    "fraud", "resignation", "delay", "cancellation", "adverse",
    "risk", "slowdown", "weak", "strike", "downgrade", "deficit"
}

# -------------------------
# File Text Extractor
# -------------------------
def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    elif ext == ".pdf":
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            # OCR fallback for scanned PDFs
            pages = convert_from_path(file_path)
            for page_img in pages:
                text += pytesseract.image_to_string(page_img) + "\n"
        return text

    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path, dtype=str)
        return df.fillna("").astype(str).apply(lambda row: " ".join(row), axis=1).str.cat(sep="\n")

    elif ext == ".csv":
        df = pd.read_csv(file_path, dtype=str)
        return df.fillna("").astype(str).apply(lambda row: " ".join(row), axis=1).str.cat(sep="\n")

    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)

    return ""


# -------------------------
# Cleaning
# -------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------
# Keyword sentiment with highlights
# -------------------------
def keyword_sentiment(text: str):
    t = text.lower()
    found_pos = [kw for kw in POSITIVE_KEYWORDS if kw in t]
    found_neg = [kw for kw in NEGATIVE_KEYWORDS if kw in t]
    if len(found_pos) > len(found_neg):
        return "Positive", found_pos, found_neg
    elif len(found_neg) > len(found_pos):
        return "Negative", found_pos, found_neg
    else:
        return "Neutral", found_pos, found_neg


# -------------------------
# FinBERT sentiment
# -------------------------
def model_sentiment(text: str):
    if len(text) > 1000:  # FinBERT input limit
        text_for_model = text[:1000]
    else:
        text_for_model = text

    try:
        result = finbert_nlp(text_for_model)
        if result and isinstance(result, list):
            best = max(result, key=lambda x: x["score"])
            return best["label"].capitalize(), best["score"]
    except Exception as e:
        print(f"[ERROR] Model sentiment failed: {e}")
    return "Neutral", 0.0


# -------------------------
# Analyzer
# -------------------------
def analyze_file(file_path: str) -> dict:
    text = extract_text(file_path)
    if not text.strip():
        return {
            "file": file_path,
            "sentiment": "Neutral",
            "reason": "No readable text",
            "keywords_positive": [],
            "keywords_negative": [],
            "highlighted_text": "",
            "model_sentiment": {"label": "Neutral", "score": 0.0}
        }

    text = clean_text(text)

    kw_sent, found_pos, found_neg = keyword_sentiment(text)
    mod_sent, mod_score = model_sentiment(text)

    # Decision: trust model if score >= 0.70 else fallback to keywords
    threshold = 0.70
    if mod_score >= threshold:
        final = mod_sent
        reason = f"FinBERT confident ({mod_score:.2f})"
    else:
        final = kw_sent
        reason = f"FinBERT weak ({mod_score:.2f}), keywords used"

    # Highlight keywords in text (HTML span tags)
    highlighted = text
    for kw in found_pos:
        highlighted = re.sub(rf"\b{kw}\b", f"<span style='background-color: #d4edda; color: #155724; font-weight:bold'>{kw}</span>", highlighted, flags=re.IGNORECASE)
    for kw in found_neg:
        highlighted = re.sub(rf"\b{kw}\b", f"<span style='background-color: #f8d7da; color: #721c24; font-weight:bold'>{kw}</span>", highlighted, flags=re.IGNORECASE)

    return {
        "file": file_path,
        "sentiment": final,
        "reason": reason,
        "keywords_positive": found_pos,
        "keywords_negative": found_neg,
        "highlighted_text": highlighted,
        "model_sentiment": {"label": mod_sent, "score": mod_score}
    }


# -------------------------
# Generate Interactive HTML Report
# -------------------------
def generate_html_report(results, output_file="nse_sentiment_report.html"):
    # Count summary
    summary = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for r in results:
        summary[r["sentiment"]] += 1
    total = sum(summary.values())

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""
        <html><head><meta charset='utf-8'>
        <title>NSE Sentiment Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        .doc { border:1px solid #ccc; border-radius:8px; margin:10px 0; padding:10px; }
        .Positive { border-left: 6px solid #28a745; }
        .Negative { border-left: 6px solid #dc3545; }
        .Neutral { border-left: 6px solid #6c757d; }
        .content { display:none; margin-top:10px; padding:10px; background:#fafafa; max-height:300px; overflow:auto; }
        .toggle { cursor:pointer; color:#007bff; text-decoration:underline; }
        .search-box { margin-bottom:20px; }
        canvas { max-width: 400px; margin-bottom: 20px; }
        .toc { margin-bottom: 20px; }
        .toc a { text-decoration: none; color: #007bff; display: block; margin: 5px 0; }
        </style>
        <script>
        function toggleContent(id) {
            var el = document.getElementById(id);
            el.style.display = (el.style.display === "none") ? "block" : "none";
        }
        function filterSentiment(sent) {
            var docs = document.getElementsByClassName("doc");
            for (var i=0; i<docs.length; i++) {
                if (sent==="All" || docs[i].classList.contains(sent)) {
                    docs[i].style.display = "block";
                } else {
                    docs[i].style.display = "none";
                }
            }
        }
        function searchText() {
            var input = document.getElementById("search").value.toLowerCase();
            var docs = document.getElementsByClassName("doc");
            for (var i=0; i<docs.length; i++) {
                if (docs[i].innerText.toLowerCase().includes(input)) {
                    docs[i].style.display = "block";
                } else {
                    docs[i].style.display = "none";
                }
            }
        }
        </script>
        </head><body>
        <h1>NSE Corporate Filings Sentiment Analysis</h1>
        <canvas id="summaryChart"></canvas>
        <div class="search-box">
          <input type="text" id="search" onkeyup="searchText()" placeholder="🔍 Search text..." style="padding:5px; width:250px;">
          <select onchange="filterSentiment(this.value)" style="padding:5px;">
            <option value="All">Show All</option>
            <option value="Positive">Positive</option>
            <option value="Negative">Negative</option>
            <option value="Neutral">Neutral</option>
          </select>
        </div>
        <h2>Summary</h2>
        <p><b>Total Documents:</b> {total}</p>
        <p><b>Positive:</b> {summary['Positive']} ({(summary['Positive']/total)*100:.2f}%)</p>
        <p><b>Negative:</b> {summary['Negative']} ({(summary['Negative']/total)*100:.2f}%)</p>
        <p><b>Neutral:</b> {summary['Neutral']} ({(summary['Neutral']/total)*100:.2f}%)</p>
        <h2>Table of Contents</h2>
        <div class="toc">
        """)

        # Table of Contents
        for idx, res in enumerate(results):
            f.write(f"<a href='#doc{idx}'>{os.path.basename(res['file'])} → {res['sentiment']}</a>")

        f.write("</div>")

        # Chart.js data
        f.write(f"""
        <script>
        var ctx = document.getElementById('summaryChart').getContext('2d');
        new Chart(ctx, {{
            type: 'pie',
            data: {{
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{{
                    data: [{summary['Positive']}, {summary['Negative']}, {summary['Neutral']}],
                    backgroundColor: ['#28a745', '#dc3545', '#6c757d']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }},
                    title: {{ display: true, text: 'Sentiment Distribution' }}
                }}
            }}
        }});
        </script>
        """)

        # Document details grouped by sentiment
        for idx, res in enumerate(results):
            f.write(f"<div id='doc{idx}' class='doc {res['sentiment']}'>")
            f.write(f"<h2>{os.path.basename(res['file'])} → {res['sentiment']}</h2>")
            f.write(f"<p><b>Reason:</b> {res['reason']}</p>")
            f.write(f"<p><b>Positive Keywords:</b> {', '.join(res['keywords_positive']) or 'None'}</p>")
            f.write(f"<p><b>Negative Keywords:</b> {', '.join(res['keywords_negative']) or 'None'}</p>")
            f.write(f"<p class='toggle' onclick=\"toggleContent('c{idx}')\">▶ Show/Hide Extracted Text</p>")
            f.write(f"<div id='c{idx}' class='content'>{res['highlighted_text']}</div>")
            f.write("</div>")

        f.write("</body></html>")
    print(f"📄 Interactive HTML report generated → {output_file}")


# -------------------------
# Main Runner
# -------------------------
if __name__ == "__main__":
    start_time = time.time()  # Start the timer

    results = []

    # Single file mode
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if os.path.isfile(input_path):
            print(f"🔎 Analyzing single file: {input_path}")
            results.append(analyze_file(input_path))
        else:
            print(f"❌ File not found: {input_path}")
            sys.exit(1)
    else:
        # Folder mode
        folder = r"./exportedData/nse_announcements/DocumentsToAnalyze"
        os.makedirs(folder, exist_ok=True)
        print(f"📂 Analyzing all files in folder: {folder}")
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath):
                print(f"🔎 Analyzing {fname} ...")
                results.append(analyze_file(fpath))

    if results:
        # Generate timestamp for file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = r"./exportedData/nse_announcements/AnalysisReport"
        os.makedirs(output_folder, exist_ok=True)

        # Save results to CSV with timestamp
        csv_file = os.path.join(output_folder, f"nse_sentiment_results_{timestamp}.csv")
        pd.DataFrame(results).drop(columns=["highlighted_text"]).to_csv(csv_file, index=False)

        # Generate HTML report with timestamp
        html_file = os.path.join(output_folder, f"nse_sentiment_report_{timestamp}.html")
        generate_html_report(results, output_file=html_file)

        print(f"\n✅ Analysis complete → Results saved in:")
        print(f"   - CSV: {csv_file}")
        print(f"   - HTML: {html_file}")
    else:
        print("⚠️ No files found.")

    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n⏱️ Total Execution Time: {execution_time:.2f} seconds")