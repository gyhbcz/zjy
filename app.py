from flask import Flask, render_template, request, send_file
import requests
import os

app = Flask(__name__)
API_KEY = "3406449b435c48d3b19874920202e54f.4FLlvV3yg0NbanY0"
API_URL = "https://open.bigmodel.cn/api/paas/v4/images/generations"

# 预设画风前缀
style_dict = {
    "默认二次元": "masterpiece, best quality, anime style, Kyoto animation style, detailed eyes",
    "新海诚画风": "masterpiece, Makoto Shinkai style, vivid light, fine background",
    "水彩插画": "watercolor illustration, translucent color, paper texture",
    "写实照片": "photorealistic, 8k, DSLR, realistic skin texture"
}
# 图片尺寸
size_dict = {
    "1:1(1024×1024)": "1024x1024",
    "竖屏9:16(768×1344)": "768x1344",
    "横屏16:9(1344×768)": "1344x768"
}

@app.route('/', methods=['GET','POST'])
def index():
    img_path = ""
    # 默认负面提示词
    default_neg = "worst quality, low quality, blurry, deformed, bad anatomy, extra fingers, text, watermark"
    if request.method == "POST":
        base_pos = request.form["prompt"]
        custom_neg = request.form["neg_prompt"]
        sel_style = request.form["style"]
        sel_size = request.form["size"]

        # 画风前缀 + 用户正向词
        full_pos = style_dict[sel_style] + ", " + base_pos

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "cogview-3-flash",
            "prompt": full_pos,
            "negative_prompt": custom_neg,
            "size": size_dict[sel_size]
        }
        res = requests.post(API_URL, json=data, headers=headers).json()
        img_url = res["data"][0]["url"]
        img_bin = requests.get(img_url).content
        save_name = "out.png"
        with open(save_name, "wb") as f:
            f.write(img_bin)
        img_path = save_name

    return render_template("index.html",
                           style_list=style_dict.keys(),
                           size_list=size_dict.keys())

@app.route("/download")
def download():
    return send_file("out.png", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
