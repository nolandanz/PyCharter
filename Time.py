
#returns the amount of time (hours and decimal of hour) between the two given
#times
def calc_time(time1, time2):
        oneHrs = time1[0]
        oneHrs = oneHrs + time1[1]
        oneHrs = int(oneHrs)
        oneMins = time1[2]
        oneMins = oneMins+time1[3]
        oneMins = int(oneMins)

        twoHrs = time2[0]
        twoHrs = twoHrs + time2[1]
        twoHrs = int(twoHrs)
        twoMins = time2[2]
        twoMins = twoMins+time2[3]
        twoMins = int(twoMins)


        #Need to see if we went over midnight.  We know this if
        #time2 < time1, if so we need to add 24 hours to time2
        if twoHrs < oneHrs:
            twoHrs = twoHrs + 24
        #First let's subtract minutes
        #Need to make sure time 2's mins is greater than time 1
        #otherwise we need to borrow an hour from time 2 hrs
        if twoMins < oneMins:
            twoMins = twoMins+60
            twoHrs = twoHrs - 1
        #Now subtract the mins
        answerMins = twoMins - oneMins


        #now subtract hours
        answerHrs = twoHrs - oneHrs

        #Now convert minutes to a decimal by dividing by 60 and rounding
        #to the nearest tenth
        answerMins = round(answerMins/60, 1)
        answer = answerHrs+answerMins
        return answer
        

print(calc_time('2245', '0115'))
