# Readme

This software uses pyqt for gui and selenium to download stock market data from NSE website. Sometimes nse website goes down, in that case the indices can be downloaded from moneycontrol website as well. In both the cases, selenium has been used to automate and web scrapping. Then the bhavcopy has been downloaded from NSE website, and the trading volume and delivery volume report was downloaded and together merged to get a consolidated modified bhavcopy files. The resultant bhavcopy files are saved in respective directories (separate directories for trading volume and delivery volume).

**Limitations** :

Download of BSE data is restricted and only NSE data is being downloaded as of now.

!["Application photo"](images/application.jpg "Application pic")



!["Snapshot 1"](images/snapshot1.jpg "Snapshot1")



!["Snapshot 2"](images/snapshot2.jpg "Snapshot2")
