from frontend.app import app
from ml.src.catboosting import predict_risk

app.run(host='0.0.0.0', port=5000, debug=True)
