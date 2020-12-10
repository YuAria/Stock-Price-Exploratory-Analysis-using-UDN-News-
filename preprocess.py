import pandas as pd
from datetime import datetime, timedelta

class Preprocessor():
    """
    A class that is used for preprocessing news and stock data.

    Methods
    -------
    loadStockData(self, file):
        Loads and processes the desired stock data from the designated folder.
    
    processNews(self, data):
        Processes the news outputted from the Scraper class.
    
    combine(self, newsData, stockData):
        Combines the news data and stock data into a suitable format for text mining.
    """

    def loadStockData(self, file):
        """
        Loads and processes the desired stock data from the designated folder.
        According to the Rate of Return (Return%) of the day,
        each day will be assigned to one of three categories:
        Return% >1: "1" (type str)
        -1< Return% <1: "0" (type str)
        Return% <-1: "-1" (type str)

        Parameters
        ----------
        file: str
            The name of the stock data file.

        Returns
        -------
        stock: DataFrame
            The processed stock data (including date and category)
        """
        stock = pd.read_csv(file)[["Date", "Change%"]]
        stock.insert(loc = 2, column = "Category", value = "0")
        stock.loc[stock["Change%"]<-1, "Category"] = "-1"
        stock.loc[stock["Change%"]>1, "Category"] = "1"
        stock.drop(["Change%"], axis = 1, inplace = True)
        return stock

    def processNews(self, data):
        """
        Processes the news outputted from the Scraper class.

        Parameters
        ----------
        data: List
            The news data obtained from the output of the scraper.
            This will be used for preprocessing.

        Returns
        -------
        data: DataFrame
            The preprocessed news data, including time (offset by 10:30) and context of each article.
            Why offset by 10:30?
            Because in our project news articles published after 1:30pm will affect next day's stock price.

        """
        data = pd.DataFrame(data = data)
        data.drop_duplicates(["link", "text"], inplace = True)
        data.dropna(inplace = True)
        data.drop(["title", "link"], axis = 1, inplace = True)
        data["text"] = [text.replace("\n", "").replace("\r", "") for text in data.text]

        data.time = [datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in data.time]
        data.time = [time+timedelta(hours = 10, minutes = 30) for time in data.time]
        data = data.loc[(data.time > "2019-01-01") & (data.time <= "2020-10-31")]
        data = data.loc[data.category.isin(['數位', '股市', '產經', '全球'])]
        data.drop(["category"], axis = 1, inplace = True)
        data.reset_index(drop = True, inplace = True)
        return data
    
    def combine(self, newsData, stockData):
        """
        Inserts the context of each news article to the day the stock price is affected.
        Criteria:
        Each day after 1:30pm -> the next day
        If stock market does not open that day -> the next day the stock market is open

        Parameters
        ----------
        newsData: DataFrame
            The returned DataFrame generated from processNews(self, file).

        stockData: DataFrame
            The returned DataFrame generated from loadStockData(self, data).

        Returns
        -------
        output: DataFrame
            The output generated by combining newsData and stockData.
            Contains "Text"(x) and "Category"(y).
        """
        output = stockData
        output.insert(loc = 1, column = "Text", value = "")
   
        for index, row in newsData.iterrows():
            entry_date = row.time.strftime('%Y/%m/%d')
            try:
                pointer = output[output.Date == entry_date].index[0]
                output.iloc[pointer, 1] = output.iloc[pointer, 1] + row.text
        
            except:
                output.iloc[pointer, 1] = output.iloc[pointer, 1] + row.text
        
        output = output[output.Text != ""]
        output.drop(["Date"], axis = 1, inplace = True)

        return output