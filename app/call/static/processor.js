class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            const channelData = input[0];  // モノラル音声データを取得
            this.port.postMessage(channelData);  // メインスレッドに音声データを送信
        }
        return true;
    }
}

registerProcessor('audio-processor', AudioProcessor);
