# PhishGuard

PhishGuard is a small web app that checks whether a URL looks like phishing. You paste a link, and it gives you a risk score plus plain-English reasons for the verdict, such as "uses a raw IP address" or "uses a URL shortener".

It works entirely offline. It never visits the link or calls an outside service. It only looks at the text of the URL itself.

## How it works

1. `features.py` turns a URL into 14 numbers: length, dots, hyphens, digits in the domain, `@` symbol, IP address host, HTTPS, subdomain count, phishing-style keywords, shorteners, risky TLDs, punycode, path length and query parameters.
2. `train.py` trains a Random Forest classifier on `data/urls.csv` and saves it to `model/phishguard.joblib`.
3. `app.py` is a Flask server. It loads the model, scores any URL sent to `/api/check`, and shows the result in a simple web page. If no model has been trained yet, it falls back to a basic rule-based score.

## Project layout

```
PhishGuard/
├── app.py              Flask app and API
├── features.py         URL feature extraction and explanations
├── train.py            Model training script
├── data/urls.csv       Small sample dataset (url,label)
├── model/              Trained model is saved here
├── templates/index.html  Web page
├── tests/              pytest tests
└── requirements.txt
```

## Getting started

You need Python 3.9 or newer.

```bash
# 1. Get the code
git clone https://github.com/<your-username>/PhishGuard.git
cd PhishGuard

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the model
python train.py

# 5. Start the app
python app.py
```

Open http://127.0.0.1:5000 in your browser and paste a URL.

## Using the API

```bash
curl -X POST http://127.0.0.1:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-login-verify.xyz/account/update"}'
```

Example response:

```json
{
  "url": "http://paypal-login-verify.xyz/account/update",
  "score": 100.0,
  "verdict": "Phishing",
  "reasons": [
    "Does not use HTTPS",
    "Many hyphens in the domain",
    "Contains several phishing-style keywords",
    "Uses a top-level domain often abused by scammers"
  ]
}
```

`score` is the model's estimated chance (0 to 100) that the URL is phishing. A score of 50 or more is labelled "Phishing".

## Running the tests

```bash
pytest
```

## Training on your own data

Use a CSV with two columns, `url` and `label` (1 = phishing, 0 = safe):

```bash
python train.py path/to/your_data.csv
```

## Limitations

- The bundled dataset is tiny (40 URLs). The 100% accuracy you see after training comes from a very small test set and says nothing about real-world performance. For anything serious, train on a large public dataset such as PhishTank or the UCI phishing data.
- It only inspects the URL text. It cannot see the page content, domain age or reputation.
- Some phishing links will be missed and some safe links will be flagged. Treat the result as a hint, not a guarantee.

## Ideas for improvement

- Train on a larger, current dataset and report proper metrics
- Add checks such as domain age or WHOIS data
- Add a browser extension
- Add Docker support

## License

Released under the MIT License. See [LICENSE](LICENSE).
