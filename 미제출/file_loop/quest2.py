for i in range(1, 10):
    if i % 2 != 0:
        tmp = 9 - i
        for j in range(tmp // 2):
            print(' ', end='')
        for j in range(i):
            print('*', end='')
        for j in range(tmp // 2):
            print(' ', end='')
        print()

#quest3 는 i/o 과제 파일 참고