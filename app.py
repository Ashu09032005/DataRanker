from flask import Flask, render_template, request, jsonify
from models import get_ranked_dataframe

app = Flask(__name__)
df_ranked = None  # global dataset

@app.route('/')
def index():
    return render_template('get_test_id.html')

@app.route('/Train_data', methods=['GET'])
def train_data():
    global df_ranked
    df_ranked = get_ranked_dataframe()
    return jsonify({"status": "ok"})

@app.route('/getTestIdByRank', methods=['GET', 'POST'])
def get_test_id_by_rank():
    global df_ranked
    if df_ranked is None:
        return jsonify({"error": "Model not trained. Please call /Train_data first."}), 400

    if request.is_json:
        data = request.get_json()
        rank = data.get('rank')
        model_name = data.get('model_name', '').upper()
    else:
        rank = request.values.get('rank')
        model_name = request.values.get('model_name', '').upper()

    try:
        rank = int(rank)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid or missing 'rank' parameter"}), 400

    if model_name not in ['LR', 'GB', 'BOTH']:
        return jsonify({"error": "Invalid 'model_name'. Must be one of 'LR', 'GB', 'BOTH'"}), 400

    lr = gb = []
    if model_name in ['LR', 'BOTH']:
        lr = df_ranked[df_ranked['Ranks by Logistic Regression'] == rank]['TestId'].dropna().tolist()
    if model_name in ['GB', 'BOTH']:
        gb = df_ranked[df_ranked['Ranks by Gradient Boost'] == rank]['TestId'].dropna().tolist()

    # Prepare extra info for template
    lr_set, gb_set = set(lr), set(gb)
    context = {
        "rank": rank,
        "model_name": model_name,
        "lr": lr,
        "gb": gb
    }

    if model_name == 'BOTH':
        context.update({
            "common_ids": list(lr_set & gb_set),
            "unique_lr_only": list(lr_set - gb_set),
            "unique_gb_only": list(gb_set - lr_set),
        })
    else:
        context["unique_count"] = len(lr_set or gb_set)

    return render_template('get_test_id.html', **context)


if __name__ == "__main__":
    app.run(debug=True)
