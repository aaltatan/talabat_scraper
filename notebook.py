import marimo

__generated_with = "0.11.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import json

    import pandas as pd
    return json, pd


@app.cell
def _(json):
    with open('data.jsonl', encoding='utf-8') as file:
        data = (json.loads(line[:-1]) for line in file.readlines())
    return data, file


@app.cell
def _(data, pd):
    df = pd.json_normalize(data)
    return (df,)


@app.cell
def _(df):
    df.sample(50).to_excel('data.xlsx')
    return


if __name__ == "__main__":
    app.run()
