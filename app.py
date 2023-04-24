import os
import json
import shutil
import string
import random
import zipfile
import cloudinary
import cloudinary.uploader
from flask import *
from zipfile import ZipFile

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, mode='w') as zipf:
        len_dir_path = len(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])

def uploader(filepath):
  uploa = cloudinary.uploader.upload(filepath, resource_type = "raw")
  return uploa['secure_url']

cloudinary.config(
    cloud_name = 'yss-projects',
    api_key = '663483921387345',
    api_secret = '3tWGt10OeDzWfaQ-V4CIO3Wv8tU'
)

app = Flask(__name__)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/extract', methods=['POST'])
def upload():
  file = request.files['file']
  folder_path = ''.join(random.choices(string.ascii_uppercase , k=4))
  file_name = file.filename.replace('.aia','')
  file_path = f"{folder_path}/"+file.filename.replace('.aia','.zip')
  os.makedirs(folder_path)
  file.save(file_path)
  ZipFile(file_path).extractall(folder_path)
  links = []
  titles = []
  try:
    for file in os.listdir(f"{folder_path}/assets/external_comps"):
          source = f"{folder_path}/assets/external_comps/{file}"
          a_file = open(f"{source}/components.json", "r")
          json_object = json.load(a_file)
          a_file.close()
          json_object[0]['helpUrl'] = "https://telegram.dog/yssprojects"
          a_file = open(f"{source}/components.json", "w")
          json.dump(json_object, a_file)
          a_file.close()
          f_path = f"{folder_path}/"+file
          os.makedirs(f_path)
          dest = shutil.move(source, f_path)
          zip_directory(f_path,f"{f_path}.zip")
          os.rename(f"{f_path}.zip",f"{f_path}.aix")
          link = uploader(f"{f_path}.aix")
          links.append(link)
          titles.append(file)
    shutil.rmtree(folder_path)
    return render_template("upload.html",links=links,titles=titles,length=len(links))
  except:
      shutil.rmtree(folder_path)
      return render_template('error.html')

@app.errorhandler(500)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html')




if __name__ == '__main__':
    app.run(debug=True)
