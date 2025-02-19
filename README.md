# **JAN Code Price Scraper** 📊  

This project is a web scraping tool that fetches product prices from **Amazon Japan, Yahoo Auctions Japan, and Rakuten Japan** using **Selenium**. The scraped data is saved to an **Excel file** and can be monitored using a **Streamlit** web application.  

---

## **Features**  

✅ Scrapes product prices from Amazon, Yahoo Auctions, and Rakuten using **JAN codes**.  
✅ Uses **Selenium** for automated web scraping.  
✅ Saves results to an **Excel file** (`scraped_prices.xlsx`).  
✅ Provides a **Streamlit dashboard** to monitor scraping status and results.  

---

## **Project Structure**  

```
scraping_app/
│── data/
│   ├── jan_codes.csv       # Input file with JAN codes & existing prices
│   ├── scraped_prices.xlsx # Output file with scraped prices
│── drivers/                # ChromeDriver storage
│── scripts/
│   ├── amazon_scraper.py   # Amazon scraping script
│   ├── yahoo_scraper.py    # Yahoo Auctions scraper
│   ├── rakuten_scraper.py  # Rakuten scraper
│   ├── main.py             # Main script to run all scrapers
│── app.py                  # Streamlit app for monitoring
│── config.py               # Configuration file
│── requirements.txt        # Python dependencies
│── README.md               # Documentation
```

---

## **Installation & Setup**  

### **1️⃣ Install Dependencies**  

Ensure you have **Python 3.8+** installed. Then, install the required Python packages:  

```bash
pip install -r requirements.txt
```

### **2️⃣ Download ChromeDriver**  

- Check your **Google Chrome** version.  
- Download the **matching ChromeDriver** from:  
  [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)  
- Place the `chromedriver` file inside the `drivers/` directory.  

---

## **Usage**  

### **Run Scraper** 🕵️‍♂️  

To scrape prices for all **JAN codes** in `data/jan_codes.csv`, run:  

```bash
python scripts/main.py
```

The results will be saved in `data/scraped_prices.xlsx`.  

### **Run Streamlit Dashboard** 📊  

To monitor scraping results in a web app, run:  

```bash
streamlit run app.py
```

Open the provided **localhost URL** in your browser to view the dashboard.  

---

## **Input File Format (data/jan_codes.csv)**  

Ensure the `jan_codes.csv` file follows this format:  

```csv
JAN,Product Name
4902370519984,Nintendo Switch
4988601009687,PlayStation 5
```

---

## **Output File Format (data/scraped_prices.xlsx)**  

The scraper generates an Excel file with this structure:  

| JAN Code       | Product Name        | Amazon Price | Yahoo Price | Rakuten Price |  
|---------------|--------------------|--------------|-------------|--------------|  
| 4902370519984 | Nintendo Switch    | ¥39,800     | ¥38,500     | ¥39,200      |  
| 4988601009687 | PlayStation 5      | ¥54,800     | ¥52,300     | ¥53,000      |  

---

## **Troubleshooting**  

### **1. Scraper is blocked / detected**  

- **Solution**: Try adding delays (`time.sleep(2)`) or rotating user-agents.  

### **2. ChromeDriver version mismatch**  

- **Solution**: Download the correct **ChromeDriver** version for your Chrome browser.  

### **3. No price found / N/A in Excel**  

- **Solution**: Check the **CSS selectors** in `amazon_scraper.py`, `yahoo_scraper.py`, or `rakuten_scraper.py`.  

---

## **Future Enhancements** 🚀  

- ✅ **Proxy support** to avoid bans.  
- ✅ **Captcha solving** integration.  
- ✅ **Multi-threading** for faster scraping.  

---

## **License**  

This project is **open-source** and free to use.  

📧 For questions or issues, feel free to ask! 🚀
