# scrapy_cebupacificair
cebupacificair price search
# Useage
seach price for Beijing to Manila from 2018-07-01 ~ 2018-12-31 :
```scrapy crawl flight-sale -a origins="PEK,MNL" -a date="2018-07-01,2018-12-31" ```

results will be downloaded in `go.csv` and `back.csv`,

# Notes
proxy IP in the `setting.py` list sometimes will be blocked, then you need to change another one, you can find free proxy IP on the Internet.
