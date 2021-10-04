import numpy as np,sys,time
from selenium.webdriver.common import keys
x=np.array([1,2,3,4])
print(x.argmin())
rates=['89/240', '38/120', '13/24', '365/360', '459/600', '1170/1200', '12/60']
rates= [rate.split("/") for rate in rates]
int_rates=[[int(rate)for rate in split_rate] for split_rate in rates]
print(int_rates)
normalized_rates= [(rate[1]-rate[0])*rate[1] for rate in int_rates]
normalized_rates=np.log(np.array(normalized_rates))
minimum_rate=normalized_rates.min()
minimum_rate_index=normalized_rates.argmin()
print(minimum_rate, normalized_rates, minimum_rate_index, sep="\n")
x=0
class X():
    def __init__(self) -> None:
        pass
    def show(self):
        print("Xx")
x=X()
eval("x.show()")