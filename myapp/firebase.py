import pyrebase 

# Pyrebase Configuration
firebaseConfig = { 
    "apiKey": "AIzaSyCyGsSMhNIwRINnA8IZj0xxKTeLiinEpwo",
    "authDomain": "pipelinedatalink.firebaseapp.com",
    "databaseURL": "https://pipelinedatalink-default-rtdb.firebaseio.com",
    "projectId": "pipelinedatalink",
    "storageBucket": "pipelinedatalink.firebasestorage.app",
    "messagingSenderId": "1061770858204",
    "appId": "1:1061770858204:web:14a25ca0b2828b93b6ee19",
    "measurementId": "G-69RG49R6QZ"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth_instance = firebase.auth()
storage = firebase.storage()  # Initialize Firebase Storage

# Path to the Firebase Admin SDK service account key file
service_account_path = 'C:/Users/Administrator/Desktop/DjangoCapstone/djangoData/FrontEnd_Django/ctuacaccreditedboardinghouse-firebase-adminsdk-f2r9o-1727478a48.json'
 