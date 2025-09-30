# London Stock Exchange - Stock Price Retriever

## Business Context
The goal of this tool is to automate stock price values retrieval for companies listed on the London Stock Exchange.

### Purpose 
The script provides a quick and automated way to acquire latest stock price values from London Stock Exchange for companies defined in input CSV file.

Analysts, data teams and analytics tools often operate on fresh price data to monitor portfolio performance, create reports or trigger alerts when prices
cross certain thresholds. With this tool, the manual, time-consuming process of gathering data can be automated allowing analysts to focus on analyzing prepared data.
Tool can run on schedule to provide fresh data over time. By incorporating this tool into a wider automation pipeline it is possible to create automatic stock reports
or alerts that can be sent to responsible people. 

### Scope and assumptions

- User keeps a CSV file containing company names and stock codes for target stocks
- The script navigates to each company stock page and captures latest stock price with timestamp
- Output is written to another CSV file for further usage
- Only public data from London Stock Exchange is used (no paid feed or login required) which is ~15 minutes delayed
- Designed for moderate workloads. For real-time/high frequency trading, a dedicated paid market data API is required

## Usage

### Installation
1. Create a virtual environment (optional)
2. Install dependencies ``` pip install -r requirements.txt ``` 
3. Download Playwright browser dependencies ``` python -m playwright install```

### Command-line Arguments
| Option | Description                              | Default                                   |
|--------|------------------------------------------|-------------------------------------------|
| `-i, --input` | Path to CSV with company names and codes | `London Stock Exchange task - input.csv`  |
| `-o, --output` | Path to save results                     | `London Stock Exchange task - output.csv` |

### Example
Running with default values:
```python stock_values_retriever.py```

Running with custom path:
```python stock_values_retriever.py -i data/input.csv -o results.csv```