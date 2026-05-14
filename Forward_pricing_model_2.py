import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Cleaning and extracting, SP500 data
sp = pd.read_csv('SP500.csv', parse_dates=['observation_date'])
sp = sp.rename(columns = {"observation_date":"date", "SP500":"sp500"})
sp = sp.set_index('date').sort_index() #Setting primary index to date, for later concat
spquart = sp.resample('QE').last() #Extracting end of quarter values


#Data check 1
#print(spquart.head(10))


#To avoid writing 4 different read csv files and sorting them out into their own variables,
#I've made a function that will do this for the individual csv files and output them as variables,
#As this will make it cleaner later on to iterate over when we do our forward price function

def correspyield(path, col_name_new):
    df = pd.read_csv(path, parse_dates=["observation_date"])
    df = df.rename(columns = {"observation_date":"date"})
    df = df.set_index('date').sort_index()
    dfquart = df.resample('QE').last()
    dfquart = dfquart.rename(columns={dfquart.columns[0]:col_name_new})
    return dfquart

#Generating different risk-free for different maturities

rf_1q = correspyield("DGS1.csv", "rf_1y") #1-year maturity yield
rf_3q = correspyield("DGS3.csv", "rf_3y") #3-year maturity yield
rf_5q = correspyield("DGS5.csv", "rf_5y") #5-year maturity yield
rf_10q = correspyield("DGS10.csv", "rf_10y") #10 year-maturity yield


#Merge the data into one dataframe
data = spquart.join([rf_1q, rf_3q, rf_5q, rf_10q], how = "inner")

#Data check 2
#print(data)

#Conversion to continous rates will go here
for col in ['rf_1y', 'rf_3y', 'rf_5y', 'rf_10y']:
#Turning quarterly maturity rate from percentage to decimal, and then compounding it continously
    rf = data[col] / 100
    data[col] = np.log(1+rf)

#The Future price calculation
def future_price(S0, r, T):
    F0 = S0*np.exp((r)*T)
    return F0

#Data check 3
print(data[col])

#Calculating individual forward prices for each end of quarter spot
data["F_1yr"] = future_price(data["sp500"],data["rf_1y"],1)
data["F_3yr"] = future_price(data["sp500"],data["rf_3y"],3)
data["F_5yr"] = future_price(data["sp500"],data["rf_5y"],5)
data["F_10yr"] = future_price(data["sp500"],data["rf_10y"],10)

#Neating output, to only display data we want
output_cols = ["sp500","F_1yr","F_3yr","F_5yr","F_10yr"]


#Basic Terminal Table
pd.set_option("display.float_format", lambda x: f"{x: ,.4f}")
print("\nTheoretical Future Prices (US$), for 1,3,5,10 year maturities: \n")
print(data[output_cols])

#Exporting data for comparision and easy visibility
data_to_export = data[["sp500", "F_1yr", "F_3yr", "F_5yr", "F_10yr"]]
data_to_export.to_csv("futures_output.csv", index_label="date")


#Generating pretty line graph to use in report
#fig, ax = plt.subplots(figsize = (8,5))
#ax.plot(data.index, data["sp500"], label = "Spot S&P500 prices")
#ax.plot(data.index, data["F_1yr"], label = "1-year Future prices")
#ax.plot(data.index, data["F_3yr"], label = "3-year Future prices")
#ax.plot(data.index, data["F_5yr"], label = "5-year Future prices")
#ax.plot(data.index, data["F_10yr"], label = "10-year Future prices")

#ax.set_xlabel("Date")
#ax.set_ylabel("Future Prices ($)")
#ax.set_title("Theoretical Future Prices (US$), for 1,3,5,10 year maturities")
#ax.legend()
#fig.autofmt_xdate()
#plt.tight_layout()
#plt.savefig("futures_output.png",dpi=300)

#plt.show()
#It turns out it was useless

fin_data = data_to_export
fin_data = fin_data.round(2) #Making data more readable and prettier for table

#Date labels
fin_data.index = pd.to_datetime(fin_data.index) .strftime("%d %b, %Y")

#Subset = fin_data,iloc[:4]   #Check for data, first 4 rows

#Final construction of the table
fig, ax = plt.subplots(figsize = (10,10))
ax.axis('off') #eliminates axis frames
ax.axis('tight')


the_table = ax.table(
    cellText = fin_data.values,
    rowLabels = fin_data.index,
    colLabels = ["S&P500", "1-year", "3-year", "5-year", "10-year"],
    cellLoc = "center",
    rowLoc = "center",
    loc = "center",
)


#Choosing the tables style

the_table.auto_set_font_size(False)
the_table.set_fontsize(9)
the_table.scale(1.2,1.4)    #Width and height

#Title and headers
for(row,col), cell in the_table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight = "bold", color = "black")
        cell.set_facecolor("#e6e6e6")   #column title colour
    elif row % 2:
        cell.set_facecolor("#f9f9f9")  #Stripe pattern

#plt.title(
#    "Table 2: Theoretical Futures Price (in USD)",
#   fontsize = 11,
#    pad = 20,
#    loc = "center",
#)

#Finally display the table
plt.tight_layout()
plt.savefig("table2.png",dpi = 300, bbox_inches = "tight")
plt.show()








