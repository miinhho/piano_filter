# 🎹 Piano Filter

컴퓨터에서 피아노 소리가 나오면 자동으로 볼륨을 줄이는 프로그램입니다.

## 📋 주요 기능

- **시스템 오디오 캡처**: Windows 시스템 오디오 출력을 실시간으로 모니터링
- **AI 기반 피아노 감지**: YAMNet 모델을 사용한 정확한 피아노 소리 감지
- **자동 볼륨 조절**: 피아노 소리 감지 시 자동으로 시스템 볼륨 감소
- **슬라이딩 윈도우**: Detection history를 통한 안정적인 상태 관리
- **모듈화된 구조**: 각 기능이 독립적인 모듈로 구성

## 🏗️ 아키텍처

```
시스템 오디오 출력 → AudioCapture → YAMNetDetector → StateMachine → VolumeController
                     (loopback)     (TensorFlow)     (history)      (pycaw)
```

### State Machine

**2-State System with Detection History:**

1. **NORMAL**: 피아노 감지 안됨 (정상 볼륨)
2. **PIANO_DETECTED**: 피아노 감지됨 (볼륨 감소)

- **Detection History**: 최근 N개 프레임의 감지 결과를 슬라이딩 윈도우로 추적
- **Restore Logic**: Detection history의 일정 비율 이상이 non-detection이어야 NORMAL로 복귀

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
uv sync
```

### 2. Windows 오디오 설정

Windows에서 시스템 오디오를 캡처하려면 **Stereo Mix**를 활성화해야 합니다:

1. 작업 표시줄의 스피커 아이콘 우클릭 → "소리 설정 열기"
2. "사운드 제어판" 클릭
3. "녹음" 탭 선택
4. 빈 공간에 우클릭 → "사용 안 함 장치 표시"
5. "스테레오 믹스" 찾아서 우클릭 → "사용"

### 3. 프로그램 실행

```bash
uv run main.py
```

## ⚙️ 설정

[main.py](main.py)에서 `FilterConfig`를 수정하여 설정을 변경할 수 있습니다:

```python
config = FilterConfig(
    detection_threshold=0.001,      # 피아노 감지 임계값 (낮을수록 민감)
    reduced_volume=0.2,             # 피아노 감지 시 볼륨 (20%)
    detection_history_size=15,      # Detection history 크기
    restore_threshold=0.9,          # 복구에 필요한 non-detection 비율
    buffer_size=2048,               # 오디오 버퍼 크기
)
```

### 설정 파라미터 설명

- **detection_threshold** (0.0 ~ 1.0): YAMNet 점수 임계값. 낮을수록 민감하게 감지
- **reduced_volume** (0.0 ~ 1.0): 피아노 감지 시 설정할 볼륨 (0.2 = 20%)
- **detection_history_size**: 슬라이딩 윈도우 크기. 클수록 안정적이지만 느림
   ```
   [👂 listening] Score: 0.003 | History: ░░░░░░ | State: normal
   ```

2. 피아노 소리가 감지되면:
   ```
   [🎹 DETECTED] Score: 0.245 | History: █░░░░░ | State: normal
   🎹 Piano detected! Reducing volume...
   [🎹 DETECTED] Score: 0.387 | History: ██░░░░ | State: piano_detected
   ```
   - 시스템 볼륨이 설정한 값으로 감소합니다
   
3. 피아노가 연속으로 연주되는 동안:
   ```
   [🎹 DETECTED] Score: 0.412 | History: █████░ | State: piano_detected
   ```
   - 볼륨이 낮게 유지됩니다
   
4. 피아노 소리가 멈추면:
   ```
   [👂 listening] Score: 0.012 | History: ████░░░░░░░░░░░ | State: piano_detected
   🔊 Piano stopped. Restoring normal volume...
   ```
   - Detection history가 충분히 비워지면 Piano stopped. Entering cooldown...
   ```
   - 쿨다운 상태로 진입합니다
   
4. 쿨다운 시간이 지나면:
   ```
   🔊 Restoring normal volume...
   ```
   - 정상 볼륨으로 복귀합니다Detection history with sliding window
- **Architecture**: Modular design with dataclasses
- **Package Manager**: uv

## 📝 참고사항

- 이 프로그램은 **마이크 입력을 사용하지 않습니다**. 시스템 오디오 출력만 캡처합니다.
- Windows 10/11에서 테스트되었습니다.
- 첫 실행 시 YAMNet 모델 다운로드에 시간이 걸릴 수 있습니다.
- Ctrl+C로 프로그램을 종료할 수 있습니다.
:
- 더 민감하게: `0.05` 이하
- 덜 민감하게: `0.15` 이상

### 볼륨이 자주 오락가락함

→ `detection_history_size`를 늘리세요 (예: 20)

### 볼륨 복구가 너무 빠름/느림

→ `restore_threshold` 값을 조정하세요:
- 더 빠르게 복구: `0.6` (60% non-detection)
- 더 느리게 복구: `0.9` (90% non-detection)
## 🔧 문제 해결

### "No loopback device found" 오류

→ Stereo Mix를 활성화하거나 VB-CABLE을 설치하세요.

### 피아노 감지가 너무 민감/둔감함

→ `detection_threshold` 값을 조정하세요 (낮을수록 민감).

