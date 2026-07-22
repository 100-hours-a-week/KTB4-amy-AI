## 기동 직후
![img](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.10.05%E2%80%AFPM.png)
- ps 명령어를 통하여 현재 서버가 정상적으로 띄워졌음을 확인
- 이후 free를 통하여 개인프로젝트가 메모리르 어느정도 사용하는지도 확인하였다.
![img](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.11.28%E2%80%AFPM.png)
- 그냥 top 했을때의 모습, 단순히 프로젝트를 띄워놓기만 한 상황이기에 cpu 사용량이 크게 차이 나지는 않지만 개인프로젝트(24298)만 cpu가 사용되고 있음을 알 수 있다.
![img](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.10.45%E2%80%AFPM.png)
- 24298을 지정해서 top 했을때의 모습

## 부하
![img.png](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.15.14%E2%80%AFPM.png)
- 부하를 주자 확연히 다른 프로세스들과는 달리 cpu 사용률이 치솟았음을 알 수 있다

## 종료
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.17.34%E2%80%AFPM.png)
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.18.39%E2%80%AFPM.png)
- 메모리 사용량이 줄어들었음이 확실히 보임, 또한 top를 하였을때 작동중인 프로세스가 없음을 통해 종료되었음을 알 수 있다.

---
## wireshark
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.51.27%E2%80%AFPM.png)
