# BTB(BitcoinTradingBot)

BTB is a Bitcoin trading bot which calculate profit margin among bitcoin trade pages automatically by ChangguHa.
* Run Image  
[!RunImg](./img/runimg.png)
* Log Image  
[!LogImg](./img/logimg.png)

### Concept
There are difference price in same coin between different coin markets.  
This program calculate profit margin between coin markets.  
If you buy some coin in base market and withdrawal to another market and sell the coin and buy some coin in another market and withdrawal to your base market and sell the coin again, you can make profit.  
This program works like that.  
[!Concept1](./img/Concept1.png)  
At first, compare coin price between base market and market list.  
Second, Calculate the profit  
Finally, If profit is over the profit which you set already, alarm to user mail.  
This program really works but there is a danger because you need to wait for coin withdrawal time and in this time the price of coin can be changed.  
[!Concept2](./img/Concept2.png)
### 개념
코인거래소간에는 같은 코인임에도 불구하고 가격차이가 있습니다.  
코인트레이딩봇은 실시간으로 거래소간의 시세차익을 계산해주는 프로그램입니다.  
베이스 거래소에서 어떤 코인을 사서, 다른 마켓으로 인출 후 다른 마켓에서 판뒤, 다른 마켓에서 다른 코인을 산뒤 그 다른 코인을 베이스거래소로 인출 한 뒤 판매하여 수익을 낼 수 있습니다.  
이 프로그램은 베이스 거래소로부터 다른 거래소간의 가격차이를 계산해준 뒤, 사용자가 지정해놓은 일정 수익이 넘을경우 베이스 거래소에서 어떤 코인을 사야하고, 어떤 거래소로 인출해야하며, 다시 어떤 코인을 사서 베이스 거래소로 다시 인출해서 팔아야하는지를 메일을 통해 알려주게 됩니다.  
### How to use
* Set wanted profit, money, mail ID & PW, Base Market, and Markets which you want to calculate.
(Gate, Kucoin, Poloniex, Binance, Bithumb, Gopax are now available)
* When run this program, this program calculate margin profits between markets in real time.
* When one cycle ended, this program show you the information about market and coin and makes log file.
* If the profit exceed your wanted profit, send you the information on your email address.
### 사용법
* Main.py에 목표 수익률, 거래금액, 메일 아이디 및 패스워드, 중심이 될 거래소 및 시세차익을 계산할 거래소를 추가합니다.
(현재 Gate, Kucoin, Poloniex, Binance, Bithumb, Gopax 가능)
* 실행버튼을 누를경우, 실시간으로 거래소간 시세차익을 계산합니다.
* 한 사이클이 돌때마다 현재기준으로 가장 수익이 많이 나는 거래소, 코인 정보 등을 console에 알려주고 Log파일로 남겨줍니다.
* 목표 수익률을 초과할 경우 해당 메일으로 위의 정보를 보내줍니다.

### Archithecture
[!Architecture](./img/Architecture.png)

