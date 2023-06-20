from flask import Flask, render_template, request
from repo import Repo
from llm import get_chain

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        repo = Repo(url=input_text)
        code, repo_dict = repo()
        chain = get_chain()
        res = chain.run(code)
        modified_text = repo_dict[int(res[0])]
        return render_template('index.html', modified_text=modified_text)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()