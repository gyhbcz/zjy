from flask import Flask, render_template, request, send_file, send_from_directory
import requests
import os
import json

app = Flask(__name__)
API_KEY = "3406449b435c48d3b19874920202e54f.4FLlvV3yg0NbanY0"
API_URL = "https://open.bigmodel.cn/api/paas/v4/images/generations"
style_file = "style_list.json"

# 默认内置画风
default_style = {
    "默认二次元": "masterpiece, best quality, anime style, Kyoto animation style, detailed eyes",
    "新海诚画风": "masterpiece, Makoto Shinkai style, vivid light, fine background",
    "水彩插画": "watercolor illustration, translucent color, paper texture",
    "写实照片": "photorealistic, 8k, DSLR, realistic skin texture"
}

def load_style():
    if os.path.exists(style_file):
        with open(style_file,"r",encoding="utf-8") as f:
            return json.load(f)
    return default_style.copy()

def save_style(data):
    with open(style_file,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

size_dict = {
    "1:1(1024×1024)": "1024x1024",
    "竖屏9:16(768×1344)": "768x1344",
    "横屏16:9(1344×768)": "1344x768"
}

@app.route('/static/<filename>')
def static_img(filename):
    return send_from_directory("static", filename)

@app.route("/download")
def download():
    return send_file("static/out.png", as_attachment=True)

@app.route('/', methods=['GET','POST'])
def index():
    img_path = ""
    style_data = load_style()
    # 完整版丰富负面提示词
    full_neg = "worst quality, low quality, normal quality, blurry, fuzzy, out of focus, ugly, deformed, disfigured, mutated, bad anatomy, extra limb, missing limb, floating limbs, extra fingers, missing fingers, fused fingers, malformed hands, asymmetrical face, mismatched eyes, cross eyes, deformed pupils, multiple heads, watermark, text, signature, logo, cropped, oversaturated, grayscale, 3d render, plastic skin"

    # 删除画风
    if request.method == "POST" and "del_style" in request.form:
        del_name = request.form["del_style"]
        if del_name in style_data:
            del style_data[del_name]
            save_style(style_data)

    # 保存自定义画风
    if request.method == "POST" and "save_style_name" in request.form:
        s_name = request.form["save_style_name"].strip()
        s_text = request.form["save_style_text"].strip()
        if s_name and s_text:
            style_data[s_name] = s_text
            save_style(style_data)

    # 生成图片
    if request.method == "POST" and "prompt" in request.form:
        base_pos = request.form["prompt"]
        custom_neg = request.form["neg_prompt"]
        sel_style = request.form["style"]
        sel_size = request.form["size"]
        full_pos = style_data[sel_style] + ", " + base_pos

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
        res = requests.post(API_URL, json=data, headers=headers, timeout=30)
        ret = res.json()
        img_url = ret["data"][0]["url"]
        img_bin = requests.get(img_url,timeout=30).content

        if not os.path.exists("static"):
            os.mkdir("static")
        with open("static/out.png","wb") as f:
            f.write(img_bin)
        img_path = "out.png"

    return render_template("index.html",
                           style_list=style_data.keys(),
                           size_list=size_dict.keys(),
                           default_neg=full_neg,
                           img=img_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
