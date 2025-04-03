from flask import Flask
import pandas

app = Flask(__name__)

excel_file = "data/NIHMS1635539-supplement-1635539_Sup_tab_4.xlsx"

S4B_df = pandas.read_excel(excel_file, sheet_name="S4B limma results", skiprows = 2)
S4A_df = pandas.read_excel(excel_file, sheet_name="S4A values", skiprows = 2)

@app.route("/")
def index():
    return "My name is Mihnea"

if __name__ == "__main__":
    app.run(debug=True)
