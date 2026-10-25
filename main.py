from frontend.app import app
#from backend import crud
from ml.src.catboosting import predict_risk

app.run(debug=True, port=5000)