# analytics_data_fetcher

- [analytics\_data\_fetcher](#analytics_data_fetcher)
  - [Architecture](#architecture)
  - [Fetch data from CVBankas MANUALLY](#fetch-data-from-cvbankas-manually)
    - [Fetching for the first time](#fetching-for-the-first-time)
    - [Fetching for the second, third, etc. time](#fetching-for-the-second-third-etc-time)
    - [TODO's](#todos)

## Architecture

```
+----------------------+         +------------------------+
|  Raspberry Pi / VM   | ----->  |   .NET API (Azure App) |
| (Scraper + Cron Job) |         |     Receives JSON      |
+----------------------+         +-----------+------------+
                                           |
                                           v
                              +---------------------------+
                              |     Azure SQL Database    |
                              |     (Power BI connects)   |
                              +---------------------------+
```

## Fetch data from CVBankas MANUALLY

### Fetching for the first time

- Open the project in VsCode
- Copy `.env_template` file and rename it to `.env` (this is where you will put your own configurations)
- Change `BASE_DIR` in `.env` file to the path where you have saved this repository
- (OPTIONAL) Change `FETCH_LIMIT` in `.env` file to a small number, like 5 - this is for testing purposes, so you don't have to wait for a long time to fetch data for ALL the jobs (can change this value later, or leave it as 0 to fetch all the jobs)
- (OPTIONAL) Change `FETCH_SPECIFIC` in `.env` file to the actual url of the CVBankas job, and the information about it will be fetched (this is for testing purposes, so you don't have to wait for a long time to fetch data for ALL the jobs)
- Open terminal `` Ctrl + `  ``
- Make sure it's cmd(Command Prompt) terminal that has opened, if not, change it to cmd by clicking on the dropdown arrow in the terminal and selecting "Select Default Profile" and then "Command Prompt"
- Run `cd ADF.Fetches`, here we will create our python virtual environment
- Run `python -m venv venv` to create the virtual environment
- Run `venv\Scripts\activate` to activate the virtual environment
- Run `python -m pip install --upgrade pip` to upgrade pip
- Run `pip install -r requirements.txt` to install the required packages
- Run `pip list` to check if all the required packages(from `requirements.txt`) are installed
- Run `cd cvbankas` to navigate to the folder where the main script is located
- Run `python main.py` to run the main script (it might take up to ~2minutes)
- Check `data` folder for the fetched data in `json` format

### Fetching for the second, third, etc. time

- Open the project in VsCode
- Open terminal `` Ctrl + `  ``
- Make sure it's cmd(Command Prompt) terminal that has opened
- Run `cd ADF.Fetches`
- Run `venv\Scripts\activate` to activate the virtual environment
- Run `cd cvbankas` to navigate to the folder where the main script is located
- Run `python main.py` to run the main script
- Check `data` folder for the fetched data in `json` format

### TODO's

- [x] be able to fetch data from cvbankas manually, data saved in json format
- [ ] be able to fetch for a specific id (for testing purposes)
- [ ] save data in SQL Server database locally (for testing purposes)
- [ ] be able to fetch data from cvbankas automatically, data saved in SQL Server database locally (for testing purposes)
- [ ] fetch data from cvbankas once a day (only the non existing id's) (raspberry pi/VM, scheduled with cron)
- [ ] host .NET api as Azure app on Azure
- [ ] host SQLServer as Azure SQL database on Azure
- [ ] connect Power BI to Azure SQL database
