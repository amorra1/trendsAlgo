# region imports
from AlgorithmImports import *
# endregion

class UglyGreenBee(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Hour).Symbol

        #50 hour moving average
        self.sma = self.SMA(self.symbol, 50, Resolution.Hour)

        self.window = RollingWindow[QuoteBar](20)

        self.trendlinePoints = 3

        #super trend indicator with period of 4 hours, multipler of 3, defualt moving average type
        self.st = self.STR(self.symbol, 4, 3, MovingAverageType.Wilders)
        self.SetWarmup(4)

        self.previousSTDirection = None
    

    def OnData(self, data: Slice):
        if self.symbol not in data or data[self.symbol] is None:
            return

        if not self.sma.IsReady:
            return

        #check current trend (up / down)
        currentPrice = data[self.symbol].Close
        currentSMA = self.sma.Current.Value

        if currentSMA >= currentPrice:
            trendDirection = "uptrend"
        else:
            trendDirection = "downtrend"

        #generate trendline
        if trendDirection == "uptrend":
            lows = [bar.Low for bar in self.window]
            trendlinePoints = sorted(lows)[:self.trendlinePoints]
        else:
            highs = [bar.High for bar in self.window]
            trendlinePoints = sorted(highs, reverse=True)[:self.trendlinePoints]

        #generate trendlimits
        if trendDirection == "uptrend":
            highs = [bar.High for bar in self.window]
            trendLimits = sorted(highs, reverse=True)[:3]
        else:
            lows = [bar.Low for bar in self.window]
            trendLimits = sorted(lows)[:3]

        #Super trend
        #if super trend reports a sell
        if self.st.Current.Value > currentPrice and self.previousSTDirection != "sell":
            self.previousSTDirection = "sell"
        #if super trend reports a buy
        elif self.st.Current.Value < currentPrice and self.previousSTDirection != "buy":
            self.previousSTDirection = "buy"

        if self.previousSTDirection == "buy" and data[self.symbol].Open > self.st.Current.Value:
            self.SetHoldings(self.symbol, 1.0)
            self.previousSTDirection = None
        elif self.previousSTDirection == "sell" and data[self.symbol].Open < self.st.Current.Value:
            self.SetHoldings(self.symbol, -1.0)
            self.previousSTDirection = None