# simulated_streaming_recognition.py

import wave
import time
import threading
import queue
import sys


class SimulatedStreamingRecognizer:
    def __init__(self, wav_file, chunk_duration_ms=100):
        """
        初始化模拟流式识别器
        
        :param wav_file: WAV文件路径
        :param chunk_duration_ms: 每个音频块的时长（毫秒）
        """
        self.wav_file = wav_file
        self.chunk_duration_ms = chunk_duration_ms
        self.audio_queue = queue.Queue()
        self.running = True

    def read_audio_chunks(self):
        """
        从WAV文件中读取音频数据块并放入队列
        """
        with wave.open(self.wav_file, 'rb') as wf:
            # 获取音频参数
            framerate = wf.getframerate()
            sampwidth = wf.getsampwidth()
            nchannels = wf.getnchannels()
            
            # 计算每个块的帧数
            chunk_frames = int(framerate * self.chunk_duration_ms / 1000)
            
            while self.running:
                # 读取一个块的数据
                data = wf.readframes(chunk_frames)
                if not data:
                    break
                
                # 将数据放入队列
                self.audio_queue.put(data)
                
                # 模拟实时采集间隔
                time.sleep(self.chunk_duration_ms / 1000.0)
            
            # 发送结束信号
            self.audio_queue.put(None)

    def simulate_recognition(self):
        """
        模拟识别过程，从队列中获取音频数据块并进行识别
        """
        while self.running:
            try:
                # 从队列中获取音频数据块
                data = self.audio_queue.get(timeout=1)
                if data is None:
                    break
                
                # 模拟识别过程（这里可以替换为实际的模型调用）
                result = self.fake_recognize(data)
                
                # 打印识别结果
                if result:
                    print(f"识别结果: {result}")
                    
            except queue.Empty:
                continue

    def fake_recognize(self, audio_data):
        """
        模拟识别函数（可替换为实际模型）
        
        :param audio_data: 音频数据块
        :return: 识别结果（文本）
        """
        # 这里只是一个示例，实际应用中应替换为真实的模型调用
        # 只有当数据量足够大时才返回"识别结果"
        if len(audio_data) > 0:
            return f"识别到文本 (数据长度: {len(audio_data)} bytes)"
        return None

    def start(self):
        """
        启动模拟流式识别过程
        """
        # 创建并启动读取音频线程
        read_thread = threading.Thread(target=self.read_audio_chunks)
        read_thread.start()
        
        # 在主线程中进行识别
        self.simulate_recognition()
        
        # 等待读取线程结束
        read_thread.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simulated_streaming_recognition.py <wav_file> [chunk_duration_ms]")
        sys.exit(1)
    
    wav_file = sys.argv[1]
    chunk_duration_ms = 100
    if len(sys.argv) > 2:
        chunk_duration_ms = int(sys.argv[2])
    
    recognizer = SimulatedStreamingRecognizer(wav_file, chunk_duration_ms)
    recognizer.start()