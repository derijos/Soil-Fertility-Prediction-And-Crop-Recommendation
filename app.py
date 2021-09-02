'''
@author - Dereck Jos
Rest API Deployed To Azure Cloud
'''

from flask import Flask, render_template, request, session
import pickle
import requests

app = Flask(__name__)

app.secret_key = "secret_key"

@app.route("/", methods=["GET", "POST"])
def index():
    model_params = pickle.load(open('model/model_params.pkl', "rb"))
    N = model_params["N"]
    K = model_params["K"]
    S = model_params["S"]
    cu = model_params["cu"]
    P = model_params["P"]
    fe = model_params["fe"]
    Mn = model_params["Mn"]
    B = model_params["B"]
    ph = model_params["ph"]
    ec = model_params["ec"]
    oc = model_params["oc"]


    return render_template("soil_index_2.html", N=N, P=P, K=K, ph=ph, ec=ec, oc=oc, S=S, fe=fe, cu=cu, Mn=Mn, B=B)

@app.route("/model_pred", methods=["POST"])
def model_pred():
    N = request.form["N"]
    P = request.form["P"]
    K = request.form["K"]
    ph = request.form["ph"]
    ec = request.form["ec"]
    oc = request.form["oc"]
    S = request.form["S"]
    fe = request.form["fe"]
    cu = request.form["cu"]
    Mn = request.form["Mn"]
    B = request.form["B"]

    response = {"Nutrients" : [N, P, K, ph, ec, oc, S, fe, cu, Mn, B]}
    pred = requests.post(url="https://rest-api-soil.azurewebsites.net/model_pred", json=response)


    # X = [[N, P, K, ph, ec, oc, S, fe, cu, Mn, B]]
    # model = pickle.load(open("model/model.cpickle","rb"))
    # pred = model.predict(X)[0]

    #pickle.dump(pred, open("model_prediction.pkl", "wb"))
    session["pred"] = str(pred.json())
    pred1 = ""
    if pred == 0:
        pred1 = "Less Fertile"

    elif pred == 1:
        pred1 = "Fertile"

    else:
        pred1 = "Highly Fertile"


    return render_template("soil_prediction_2.html", pred=pred1)


@app.route("/crop_recom", methods=['GET', 'POST'])
def crop_recom():
    min_rainfall = pickle.load(open("model/rainfall_stats.pkl", "rb"))["min_rainfall"]
    max_rainfall = pickle.load(open("model/rainfall_stats.pkl", "rb"))["max_rainfall"]
    return render_template("crop_recommend.html", flag=False, min_rainfall=min_rainfall, max_rainfall=max_rainfall)



@app.route("/crop_recom_res", methods=['POST'])
def crop_recom_res():
        pred = int(session["pred"])
        min_rainfall = pickle.load(open("model/rainfall_stats.pkl", "rb"))["min_rainfall"]
        max_rainfall = pickle.load(open("model/rainfall_stats.pkl", "rb"))["max_rainfall"]
        model = pickle.load(open("model/knn.cpickle", "rb"))
        fertility = pred
        crop_recommend_list = pickle.load(open("model/crop_recom.cpickle", "rb"))
        crop_recommend_list = crop_recommend_list["crop"].to_dict()
        min_rainfall_form = request.form["min"]
        max_rainfall_form = request.form["max"]
        x = [[min_rainfall_form, max_rainfall_form, fertility]]
        pred = model.predict(x)[0]

        crop = crop_recommend_list[pred]

        return render_template("crop_recommend.html", flag=True, min_rainfall=min_rainfall, max_rainfall=max_rainfall, crop = crop)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

