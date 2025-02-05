from flask import Flask
from flask import render_template
from flask import json
from flask import jsonify
from flask import request
from flask import make_response

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies

from datetime import timedelta

app = Flask(__name__)                                                                                                                  
                                                                                                                                       
# Configuration du module JWT
app.config["JWT_SECRET_KEY"] = "Ma_clé_secrete"  # Ma clée privée
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return render_template('accueil.html')

# Création d'une route qui vérifie l'utilisateur et retour un Jeton JWT si ok.
# La fonction create_access_token() est utilisée pour générer un jeton JWT.
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    users = {
        "admin": {"password": "admin", "role": "admin"},
        "test": {"password": "test", "role": "user"}
    }

    user = users.get(username)
    if user and user["password"] == password:
        access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})
        response = make_response(jsonify({"msg": "Connexion réussie"}), 200)
        set_access_cookies(response, access_token)  # Stocke le token dans un cookie
        return response
    else:
        return jsonify({"msg": "Nom d'utilisateur ou mot de passe incorrect"}), 401


# Route protégée par un jeton valide
@app.route("/protected", methods=["GET"])
@jwt_required(locations=["cookies"])  # Lit le token depuis le Cookie
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    claims = get_jwt()
    if claims.get("role") == "admin":
        return jsonify({"msg": "Bienvenue Admin !"}), 200
    else:
        return jsonify({"msg": "Accès interdit : Vous devez être administrateur"}), 403

@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')
  
if __name__ == "__main__":
  app.run(debug=True)
