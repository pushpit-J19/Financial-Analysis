####################################################################################################################################################################################
# SCRAPING FUNCTIONS
####################################################################################################################################################################################

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_screener_info(symbol):

  url = "https://www.screener.in/company/"+ symbol.upper() +"/consolidated/"

  try:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # CHECKING IF CONSOLIDATED DATA IS AVAILABLE
    # by checking if PnL table is filled or not
    if not check_consolidated_available(soup):
      try:
        url = "https://www.screener.in/company/"+ symbol.upper() +"/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Using Standalone data, since consolidated numbers are not available")
      except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return -1, "Error"
    
    pnl_section = soup.find("section", id="profit-loss")

    # # TOP RATIOS
    # top_ratios_data = get_top_ratios(soup)

    # print(top_ratios_data)


    # # 3, 5, 10 YEAR DATA
    # year_data_tables_data = get_range_tables(pnl_section)
    
    # tmp_df = pd.DataFrame(year_data_tables_data)[["", "10 Years", "5 Years", "3 Years", "TTM"]]
    # tmp_df.set_index(tmp_df.columns[0], inplace = True)
    # l = [col for col in tmp_df.columns.to_list()][:]
    # print(l)
    # print(tmp_df.loc["Sales Growth", :].to_list())


    # print(year_data_tables_data)
    # print(pd.DataFrame(year_data_tables_data))


    # # PNL TABLE
    # pnl_df = get_pnl_table(pnl_section)
    # print(pnl_df)
    # # print(pnl_df.loc["Net Profit", :].iloc[-6:-1])
    # # print(pnl_df.loc["Net Profit", "Mar 2023"])

    # # RATIO TABLE
    # ratio_df = get_ratios(soup)
    # print(ratio_df)
    # print(ratio_df.loc["ROCE %",:].iloc[-7:-2])

    return 200, soup

  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return -1, "Error"

# scrape_screener_info("ASIANPAINT")

###################################################################################################

def check_consolidated_available(soup):
  section = soup.find("section", id="profit-loss")
  trows = section.find("table", class_="data-table").find("tbody").find_all("tr")
  if len(trows[0].find_all("td")) > 1:
    print(len(trows[0].find_all("td")))
    return True
  else:
    print(len(trows[0].find_all("td")))
    return False


#############  TOP RATIOS  ############
def get_top_ratios(soup):

  top_ratios_data = {}
  top_ratios_ul = soup.find('ul', id='top-ratios')

  if top_ratios_ul:
    ratios = top_ratios_ul.find_all("li")

    for ratio in ratios:
      ratio_label = ratio.find("span", class_="name").text.strip()
      if ratio_label == "High / Low":
        # ratio_value_list = [span.text.strip().replace(",","") for span in ratio.find_all("span", class_="number")]
        # ratio_value = ' / '.join(ratio_value_list)
        ratio_value_list = ratio.find_all("span", class_="number")
        top_ratios_data["High"] = ratio_value_list[0].text.strip().replace(",","")
        top_ratios_data["Low"] = ratio_value_list[1].text.strip().replace(",","")
      else:
        ratio_value = ratio.find("span", class_="number").text.strip().replace(",","")
        top_ratios_data[ratio_label] = ratio_value

  return top_ratios_data

############  3, 5, 10 YEAR DATA  ############
def get_range_tables(pnl_section):

  year_data_tables_data = []
  year_data_tables = pnl_section.find_all("table", class_ = "ranges-table")

  for table in year_data_tables:
    table_data = {}
    trows = table.find_all("tr")
    header = trows[0].find("th").text.strip()
    table_data[""] = header

    for i in range (1, len(trows)):
      data_points = trows[i].find_all("td")
      label = data_points[0].text.strip().replace(",","").replace(":","").replace("Years", "YRS").strip()
      value = data_points[1].text.strip().replace(",","").replace(":","").replace("%", "").strip()
      table_data[label] = round(float(value),2)
    
    year_data_tables_data.append(table_data)
  year_data_tables_data[0][""] = "Sales Growth"
  year_data_tables_data[1][""] = "Profit Growth"

  # for table in year_data_tables:
  #   trows = table.find_all("tr")
  #   header = trows[0].find("th").text.strip()
  #   year_data_tables_data[header] = {}

  #   for i in range (1, len(trows)):
  #     data_points = trows[i].find_all("td")
  #     label = data_points[0].text.strip().replace(",","").replace(":","")
  #     value = data_points[1].text.strip().replace(",","").replace(":","")
  #     year_data_tables_data[header][label] = value

  return year_data_tables_data


############  PNL STATEMENT  ############
def get_pnl_table(pnl_section):
  table = pnl_section.find("table", class_="data-table")
  headers = [th.text.strip() for th in table.find('thead').find_all('th')]
  headers[0] = "Particulars"

  data = []
  for row in table.find('tbody').find_all('tr'):
    # row_data = [td.text.strip() for td in row.find_all('td')]
    tds = row.find_all('td')
    row_data = []
    for i in range(len(tds)):
      if i == 0:
        row_data.append(tds[i].text.strip().replace("+", "").strip())
      else:
        data_value = tds[i].text.strip().replace(",", "").replace("%","").strip()
        row_data.append(float(data_value)) if data_value else row_data.append(data_value)

    data.append(row_data)

  df = pd.DataFrame(data, columns=headers)
  df.set_index(df.columns[0], inplace = True)

  return df


############  RATIOS  ############
def get_ratios(soup):
  ratio_section = soup.find("section", id="ratios")
  table = ratio_section.find("table", class_="data-table")

  headers = [th.text.strip() for th in table.find('thead').find_all('th')]
  headers[0] = "Particulars"

  data = []
  for row in table.find('tbody').find_all('tr'):
    # row_data = [td.text.strip() for td in row.find_all('td')]
    tds = row.find_all('td')
    row_data = []
    for i in range(len(tds)):
      if i == 0:
        row_data.append(tds[i].text.strip())
      else:
        data_value = tds[i].text.strip().replace(",", "").replace("%","").strip()
        row_data.append(float(data_value)) if data_value else row_data.append(data_value)

    data.append(row_data)

  df = pd.DataFrame(data, columns=headers)
  df.set_index(df.columns[0], inplace = True)
  
  return df

