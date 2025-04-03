from flask import Flask, render_template, jsonify
import pandas
import numpy as np

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

if __name__ == "__main__":
    app.run(debug=True)
