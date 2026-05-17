hour = int(input("원하는 시간 입력: "))

if hour <= 9 and hour >= 7:
    print("아침 식사 시간")
elif hour >= 12 and hour <= 14:
    print("점심 시간")
elif hour >= 18 and hour <= 20:
    print('저녁 식사 시간')
else:
    print('식사 금지')