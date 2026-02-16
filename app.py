from flask import Flask, request, jsonify
import requests, uuid, re, time

app = Flask(__name__)


class NSFWDetector:

    BASE_URL = "https://minitoolai.com/nsfw-content-detector/"

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': "Mozilla/5.0",
            'x-requested-with': "XMLHttpRequest",
            'origin': "https://minitoolai.com",
            'referer': self.BASE_URL
        }

    # ========================
    # جلب التوكن
    # ========================
    def get_token(self):
        res = self.session.get(self.BASE_URL)
        utoken = re.search(
            r"var\s+utoken\s*=\s*['\"]([^'\"]+)['\"]",
            res.text
        ).group(1)
        return utoken

    # ========================
    # رفع الصورة
    # ========================
    def upload_image(self, image_file, utoken):

        url = self.BASE_URL + "upload_img.php"

        files = {
            "image": (str(uuid.uuid4()), image_file, "image/png")
        }

        data = {"utoken": utoken}

        res = self.session.post(url, files=files, data=data, headers=self.headers)
        return res.text.strip()

    # ========================
    # تحليل الصورة
    # ========================
    def detect(self, uploaded_path, utoken):

        url = self.BASE_URL + "nsfw_detector.php"

        payload = {
            "textContent": "",
            "uploadedImageUrl": uploaded_path,
            "utoken": utoken
        }

        time.sleep(1)  # نفس سكربتك
        res = self.session.post(url, data=payload, headers=self.headers)
        return res.json()["results"][0]

    # ========================
    # الدالة الرئيسية
    # ========================
    def check_image(self, image_file):

        utoken = self.get_token()

        uploaded_path = self.upload_image(image_file, utoken)

        result = self.detect(uploaded_path, utoken)

        score = result["category_scores"]["sexual"]
        percent = int(score * 100)

        is_nsfw = result["categories"]["sexual"] and score > 0.6

        return {
            "nsfw": is_nsfw,
            "score": percent
        }


detector = NSFWDetector()

# ========================
# API Route
# ========================
@app.route("/")
def home():
    return "You have to upload a picture"
    
@app.route("/check", methods=["POST"])
def check():

    if "image" not in request.files:
        return jsonify({"error": "no image"}), 400

    image = request.files["image"]

    result = detector.check_image(image)

    return jsonify(result)


# ========================
# تشغيل السيرفر
# ========================
