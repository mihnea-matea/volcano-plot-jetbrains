from flask import Flask, render_template, jsonify
import pandas
import numpy as np
import requests

app = Flask(__name__)

excel_file = "data/NIHMS1635539-supplement-1635539_Sup_tab_4.xlsx"

S4B_df = pandas.read_excel(excel_file, sheet_name="S4B limma results", skiprows = 2)
S4A_df = pandas.read_excel(excel_file, sheet_name="S4A values", skiprows = 2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/volcano-data")
def get_volcano_data():
    S4B_df["negLog10P"] = -np.log10(S4B_df["adj.P.Val"]) # this is for 0.01 significance metric 

    volcano_data = []
    for i, row in S4B_df.iterrows():
        entry = {
            "gene": row["EntrezGeneSymbol"],
            "logFC": row["logFC"],
            "negLog10P": row["negLog10P"]
        }
        volcano_data.append(entry)

    return jsonify(volcano_data)

@app.route("/api/boxplot-data/<gene_name>")
def get_boxplot_data(gene_name):
    gene_data = S4A_df[S4A_df["EntrezGeneSymbol"] == gene_name]
    
    all_columns = S4A_df.columns.tolist()
    start_index = all_columns.index("Set002.H4.OD12.dup")
    donor_columns = all_columns[start_index:]
    old_columns = [col for col in donor_columns if "OD" in str(col)]
    young_columns = [col for col in donor_columns if "YD" in str(col)]
    old_values = gene_data[old_columns].values.flatten().tolist()
    young_values = gene_data[young_columns].values.flatten().tolist()

    return jsonify({
        "gene": gene_name,
        "young": young_values,
        "old": old_values
    })

@app.route("/api/gene-info/<gene_name>")
def gene_info(gene_name):
    try:
        query = f"symbol:{gene_name}&species=human"
        url = f"https://mygene.info/v3/query?q={query}"

        response = requests.get(url)
        data = response.json()
        if "hits" not in data or len(data["hits"]) == 0:
            return jsonify({
                "papers": [],
                "error": f"No gene found for symbol: {gene_name}"
            })
        gene_id = data["hits"][0]["_id"]
        detail_url = f"https://mygene.info/v3/gene/{gene_id}"
        details = requests.get(detail_url).json()
        papers = []
        if "generif" in details:
            for entry in details["generif"]:
                if "pubmed" in entry and "text" in entry:
                    paper_info = {
                        "pmid": entry["pubmed"],
                        "title": entry["text"],
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{entry['pubmed']}/"
                    }
                    papers.append(paper_info)
        return jsonify({
            "gene": gene_name,
            "papers": papers[:5] # we will only show the first 5 such associations (could be too many) 
        })

    except Exception as err:
        return jsonify({
            "error": str(err)
        })


if __name__ == "__main__":
    app.run(debug=True)
