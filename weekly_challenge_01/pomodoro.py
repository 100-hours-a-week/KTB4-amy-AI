import argparse
import asyncio
import sys


#타이머 함수
async def countdown_work(sec):
    print('Working time!')
    while sec > 0:
        sec -= 1
        minute = sec // 60
        second = sec % 60

        print(f"{minute:02d}:{second:02d}", end='\r',
              flush=True)  # \r 은 출력 위치를 줄의 맨 앞으로 flush 는 버퍼 거치지 않고 바로 데이터를 송출 함으로써 실시간성 확보
        await asyncio.sleep(1)

    #알림
    print('\a', end='')  # 끝났다고 소리 내기
    tmp = await asyncio.create_subprocess_shell("osascript -e 'display notification \"쉬는시간~!\" with title \"뽀모도로\"'")
    await tmp.wait() # 알림창 명령어 실행하자마자 함수가 종료되어 알림창이 뜨지 못하는 현상 개선/작업이 끝날때까지 비동기 하지말고 대기 (wait은 동기이다)

async def countdown_break(sec):
    print('Break time!')
    while sec > 0:
        sec -= 1
        minute = sec // 60
        second = sec % 60

        print(f"{minute:02d}:{second:02d}", end='\r',
              flush=True)  # \r 은 출력 위치를 줄의 맨 앞으로 flush 는 버퍼 거치지 않고 바로 데이터를 송출 함으로써 실시간성 확보
        await asyncio.sleep(1)

    #알림
    print('\a', end='')  # 끝났다고 소리 내기
    tmp = await asyncio.create_subprocess_shell("osascript -e 'display notification \"일 합시다 일\" with title \"뽀모도로\"'")
    await tmp.wait()

# 입력
parse = argparse.ArgumentParser(prog= 'Pomodoro')
parse.add_argument('-on', type = int)
parse.add_argument('-time', choices= ['25/5', '50/15'])
# TODO: 중도 정지 기능 추가하면 초 합산해서 출력하는 기능 추가하기
# parse.add_argument('-total', action= 'store_true') # total은 스위치의 기능과 유사하여 커맨드 입력시 들어가는 데이터가 없으므로 아예 true 선언을 해준다
args = parse.parse_args()

#변수 할당
pomodoro_on = args.on
pomodoro_time = args.time

for i in range(pomodoro_on):
    if (pomodoro_time == '25/5'):
        asyncio.run(countdown_work(25))
        asyncio.run(countdown_break(5))
    else:
        asyncio.run(countdown_work(50 * 60))
        asyncio.run(countdown_break(15 * 60))
