
####################################################################################################################################################################################
# VALUATION FUNCTIONS
####################################################################################################################################################################################

# User inputs are cost of capital, RoCE, growth during high growth period, high growth period (years), fade period (years) and terminal growth rate
# Tax rate is assumed constant at 25%.
import pandas as pd


def calculate_intrinsic_pe(coc, roce, g, g_period, fade_period, gt):
  
  ## Initialization
  tax_rate = 0.25
  capital_ending_neg1 = 100

  roce_post_tax = roce * (1-tax_rate)
  reinvestment_rate_1 = g / roce_post_tax
  reinvestment_rate_2 = gt / roce_post_tax

  capital_ending = []
  nopat = []
  ebt = []
  investment = []
  fcf = []
  discount_factor = []
  discount_fcf = []

  
  ## Calculating Earnings Growth Rate
  earning_g_rate = [g]*g_period
  for i in range(fade_period):
    earning_g_rate.append(earning_g_rate[-1] - ((g-gt)/fade_period) )

  
  ## Calculations during the High Growth period
  for i in range (g_period+1):
    if i == 0:
      nopat.append( capital_ending_neg1 * roce_post_tax )
    else:
      nopat.append( capital_ending[-1] * roce_post_tax)
    
    ebt.append(nopat[-1]/(1-tax_rate))
    investment.append(nopat[-1] * reinvestment_rate_1)
    fcf.append(nopat[-1] - investment[-1])
    discount_factor.append( 1 / ((1+coc)**(i)) )
    discount_fcf.append(fcf[-1] * discount_factor[-1])

    if i == 0:
      capital_ending.append( capital_ending_neg1 + investment[-1])
    else:
      capital_ending.append( capital_ending[-1] + investment[-1])

  ## Calculations during the Phase Out period
  for i in range (fade_period):
    nopat.append( capital_ending[-1] * roce_post_tax)
    ebt.append(nopat[-1]/(1-tax_rate))
    investment.append(nopat[-1] * earning_g_rate[i+g_period]  / roce_post_tax)
    fcf.append(nopat[-1] - investment[-1])
    discount_factor.append( 1 / ((1+coc)**(i+g_period+1)) )
    discount_fcf.append(fcf[-1] * discount_factor[-1])
    capital_ending.append( capital_ending[-1] + investment[-1])


  ## Storing the calculations in a df
  earning_g_rate.insert(0,0)
  df = pd.DataFrame({
      "Earnings Growth Rate": earning_g_rate,
      "EBT": ebt, "NOPAT" : nopat,
      "Capital Ending" : capital_ending,
      "Investment" : investment,
      "FCF" : fcf, "Discount Factor": discount_factor, "Discounted FCF" : discount_fcf
  })

  
  ## Terminal Value Calculations
  terminal_nopat = nopat[-1] * (1+gt) / (coc - gt)
  terminal_investment = terminal_nopat * reinvestment_rate_2
  terminal_fcf = terminal_nopat - terminal_investment
  terminal_discount_fcf = terminal_fcf * discount_factor[-1]

  
  ## Storing all the key metrics
  metrics_dict = {}
  metrics_dict["intrinsic value"] = df["Discounted FCF"].sum() + terminal_discount_fcf
  metrics_dict["25 yr Exit Multiple"] = terminal_nopat / (nopat[-1] * (1+gt))
  metrics_dict["terminal / total"] = terminal_discount_fcf / metrics_dict["intrinsic value"]
  metrics_dict["TTM PB"] = metrics_dict["intrinsic value"] / df["Capital Ending"].iloc[0]
  metrics_dict["TTM PE"] = metrics_dict["intrinsic value"] / df["NOPAT"].iloc[0]
  metrics_dict["1yr forward PE"] = metrics_dict["intrinsic value"] / df["NOPAT"].iloc[1]

  print(reinvestment_rate_1, reinvestment_rate_2)
  print(earning_g_rate)
  print(earning_g_rate[0+g_period])
  print(df)
  print(terminal_discount_fcf)
  print(metrics_dict)

  return df, metrics_dict

###################################################################################################

def calculate_degree_of_overvaluation(current_pe, fy23_pe, calculated_intrinsic_pe):
  if current_pe < fy23_pe:
    return (current_pe/calculated_intrinsic_pe) - 1
  else:
    return (fy23_pe/calculated_intrinsic_pe) - 1


# calculate_intrinsic_pe(0.11, 0.2, 0.15, 15, 15, 0.05)
# calculate_intrinsic_pe(0.11, 0.95, 0.15, 15, 15, 0.05)
