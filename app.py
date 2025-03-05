from flask import Flask, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Ensure templates are reloaded automatically

@app.route('/')
def home():
    return render_template('layout.html')

if __name__ == '__main__':
    app.run(debug=True)  # Debug mode should automatically reload server when code changes
