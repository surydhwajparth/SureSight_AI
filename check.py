import os, io
import google.generativeai as genai
from PIL import Image

genai.configure(api_key="AIzaSyCi7XQTGOh_Nks15ap6sM1GWdCFVqcKQbo")
m = genai.GenerativeModel("gemini-1.5-flash")
img = Image.open(r"C:\Users\ParthSurydhwaj\Downloads\OIP.jpg").convert("RGB")
resp = m.generate_content(["Read the text verbatim.", img])
print(resp.text[:200])