let audioCtx: AudioContext | null = null;
let armed = false;

function hasLiveGesture(): boolean {
  return navigator.userActivation?.isActive === true;
}

/** Gọi từ click chuông: chỉ lúc đó Chrome mới cho tạo loa. */
export function unlockAlertSound() {
  armed = true;
  if (!hasLiveGesture()) return;
  const Ctor =
    window.AudioContext ||
    (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!Ctor) return;
  if (!audioCtx) audioCtx = new Ctor();
  if (audioCtx.state === "suspended") void audioCtx.resume().catch(() => undefined);
}

export function pingAlert() {
  if (!armed || !audioCtx || audioCtx.state !== "running") return;

  try {
    navigator.vibrate?.([180, 80, 180, 80, 240]);
  } catch {
    /* Windows thường không rung */
  }

  const now = audioCtx.currentTime;
  const ding = (at: number, freq: number, dur: number) => {
    const osc = audioCtx!.createOscillator();
    const gain = audioCtx!.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(freq, at);
    gain.gain.setValueAtTime(0.001, at);
    gain.gain.exponentialRampToValueAtTime(0.22, at + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, at + dur);
    osc.connect(gain);
    gain.connect(audioCtx!.destination);
    osc.start(at);
    osc.stop(at + dur + 0.02);
  };
  ding(now, 880, 0.18);
  ding(now + 0.16, 1174, 0.28);
}
