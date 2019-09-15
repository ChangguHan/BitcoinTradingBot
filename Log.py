import time
class Log_coinSelect :
    def __init__(self,cuName, coinName):
        self.filename = "./log/"+cuName+"/" + coinName + ".txt"
        file = open(self.filename, "w")
        file.close()

def write(filename,text):
    file = open(filename, 'a')
    file.write(str(text)+",")
    file.close()


class Log :
    smallLine = "------------------------------------------\n";
    middleLine = "==========================================\n";
    largeLine = "##########################################\n";
    def __init__(self):
        nowtime =self.nowtime_filename()
        self.filename = "./log/" + nowtime+".txt"
        file = open(self.filename,"w")
        file.write(self.largeLine)
        file.write("start time : " + self.nowtime() + "\n")
        file.write(self.largeLine)
        file.close()

    def putSmallLine(self):
        file = open(self.filename, 'a')
        file.write(self.smallLine)
        file.close()

    def putMiddleLine(self):
        file = open(self.filename, 'a')
        file.write(self.middleLine)
        file.close()

    def putLargeLine(self):
        file = open(self.filename, 'a')
        file.write(self.largeLine)
        file.close()
    def write(self,text):
        file = open(self.filename, 'a')
        nowtime = self.nowtime()
        print(text)
        file.write(nowtime + "  //  " + str(text)+ "\n")
        file.close()

    def nowtime(self):
        now = time.localtime()
        nowtime = str("%04d-%02d-%02d %02d:%02d:%02d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        return nowtime
    def nowtime_filename(self):
        now = time.localtime()
        nowtime = str("%04d%02d%02d %02d%02d%02d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        return nowtime

    def coinTimeLog(self, market_string, coin_string, text):
        filename = "./log/coin/" + market_string+"-"+coin_string+".txt"
        try :
            file = open(filename, "a")
        except :file = open(filename, "w")
        file.write(str(text) + "/" + self.nowtime() + "\n")
        file.close()

    def writeCalculation(self,calculationDic):
        file = open(self.filename, 'a')
        nowtime = self.nowtime()
        print(calculationDic)

        file.write(nowtime +  " // \n")
        for i in list(calculationDic.keys()) :
            if not str(i) == "details" :
                file.write("    " + str(i) + " : " + str(calculationDic[i]) + "\n")
            else :
                file.write("    " + str(i) + " : " + "\n")
                for j in list(calculationDic[i].keys()) :
                    file.write("        " + str(j) + " : " + str(calculationDic[i][j]) + "\n")

        file.write(self.smallLine)
        file.close()

    def writeCoinSorting(self,result_coinSorting):
        file = open(self.filename, 'a')
        nowtime = self.nowtime()
        file.write(nowtime + " // \n")



        for market in result_coinSorting :
            file.write(self.middleLine + "\n")
            file.write('            ' + market + "\n")
            firstExProfit = {}
            secondExProfit = {}
            for coinFirstEx in result_coinSorting[market]["first"] :
                firstExProfit[coinFirstEx] = result_coinSorting[market]["first"][coinFirstEx][0]
            for coinSecondEx in result_coinSorting[market]["second"]:
                secondExProfit[coinSecondEx] = result_coinSorting[market]["second"][coinSecondEx][0]


            firstExProfitList = list(firstExProfit.values())
            firstExProfitList.sort()
            firstExProfitList.reverse()

            secondExProfitList = list(secondExProfit.values())
            secondExProfitList.sort()
            secondExProfitList.reverse()

            firstMap = {}
            i=0


            for coinName in firstExProfit :
                for coinName in firstExProfit :
                    if firstExProfit[coinName] == firstExProfitList[i] :
                        i = i+1
                        firstMap[i] = [coinName, firstExProfit[coinName]]
                if i>=5 : break
            secondMap = {}
            j=0

            for coinName2 in secondExProfit :
                for coinName2 in secondExProfit :
                    if secondExProfit[coinName2] == secondExProfitList[j] :
                        j = j+1
                        secondMap[j] = [coinName2, secondExProfit[coinName2]]
                if j>=5 : break


            file.write("Best : " + firstMap[1][0]   + "-" +  secondMap[1][0] + "("+ str(firstMap[1][1] * secondMap[1][1])  + ")" + "\n")
            file.write(self.smallLine)
            file.write("First Ex" + "\n")
            # print(firstMap)
            for rank in firstMap :
                track = result_coinSorting[market]["first"][firstMap[rank][0]][1].split("-")
                # print(track)
                file.write(str(rank) + " : " + firstMap[rank][0] + " (" + str(firstMap[rank][1]) + ") :: " + track[2] + "-" + track[3] + "-" + track[4] + "\n")

            file.write(self.smallLine)
            file.write("Second Ex" + "\n")
            for rank2 in secondMap:
                track2 = result_coinSorting[market]["second"][secondMap[rank2][0]][1].split("-")
                file.write(
                    str(rank2) + " : " + secondMap[rank2][0] + " (" + str(secondMap[rank2][1]) + ") :: " + track2[4] + "-" + track2[
                        5] + "-" + track2[6] + "\n")

        file.write(self.middleLine)


