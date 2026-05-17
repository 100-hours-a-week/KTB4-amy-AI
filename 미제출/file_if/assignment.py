print('''[option]
1. 작성 2. 조회 3. 수정 4. 삭제 5. 추가기능 6. 종료 ''')
num = int(input('번호를 선택해주세요'))

while num != 6:
    if num == 1:
        print('작성')
    elif num == 2:
        print('조회')
    elif num == 3:
        print('수정')
    elif num == 4:
        print('삭제')
    elif num == 5:
        print('추가기능')

    print('''[option]
1. 작성 2. 조회 3. 수정 4. 삭제 5. 추가기능 6. 종료 ''')
    num = int(input('번호를 선택해주세요'))

if num == 6:
    print('종료')