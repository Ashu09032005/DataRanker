from flask import Flask, render_template, request
from models import get_ranked_dataframe


app = Flask(__name__)
df_ranked = get_ranked_dataframe()

@app.route('/')
def index():
    return render_template('get_test_id.html')

@app.route('/getTestIdByRank', methods=['POST'])
def get_test_id_by_rank():
    rank = request.form.get('rank')
    model_name = request.form.get('model_name', '').upper()

    try:
        rank = int(rank)
    except:
        return "Invalid rank", 400

    lr = gb = None
    if model_name in ['LR', 'BOTH']:
        lr = df_ranked[df_ranked['Ranks by Logistic Regression'] == rank]['TestId'].dropna().tolist()
    if model_name in ['GB', 'BOTH']:
        gb = df_ranked[df_ranked['Ranks by Gradient Boost'] == rank]['TestId'].dropna().tolist()

    return render_template('get_test_id.html', rank=rank,model_name=model_name, lr=lr, gb=gb)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

